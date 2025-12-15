"""
Validation service - Document and business rule validation
خدمة التحقق - التحقق من المستندات وقواعد العمل
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from data import (
    DocumentHeader, DocumentLine, Item, StockBalance,
    TrackingType, ItemType
)
from services.policy import PolicyService


class ValidationError(Exception):
    """خطأ في التحقق"""
    pass


class ValidationService:
    """Service for validating documents and business rules"""
    
    def __init__(self):
        self.policy_service = PolicyService()
    
    def validate_document(self, document: DocumentHeader, session: Session):
        """
        Validate a document before posting
        
        Args:
            document: Document to validate
            session: Database session
            
        Raises:
            ValidationError: If validation fails
        """
        if not document.lines:
            raise ValidationError('المستند لا يحتوي على بنود')
        
        for line in document.lines:
            self.validate_line(document, line, session)
    
    def validate_line(self, document: DocumentHeader, line: DocumentLine, 
                     session: Session):
        """Validate a document line"""
        # Get item
        item = session.query(Item).filter_by(id=line.item_id).first()
        if not item:
            raise ValidationError(f'الصنف رقم {line.item_id} غير موجود')
        
        # Validate item is active
        if not item.is_active:
            raise ValidationError(f'الصنف {item.name_ar} غير نشط')
        
        # Validate stock item for inventory transactions
        if item.item_type != ItemType.STOCK:
            if document.doc_type.value in ['GRN_RECEIPT', 'ISSUE', 'TRANSFER']:
                raise ValidationError(f'الصنف {item.name_ar} ليس صنف مخزني')
        
        # Validate quantity
        if line.base_qty <= 0:
            raise ValidationError(f'الكمية يجب أن تكون أكبر من صفر للصنف {item.name_ar}')
        
        # Validate tracking
        self._validate_tracking(item, line)
        
        # Validate negative stock
        if document.doc_type.value in ['ISSUE', 'TRANSFER', 'RETURN_IN']:
            self._validate_negative_stock(document, line, item, session)
    
    def _validate_tracking(self, item: Item, line: DocumentLine):
        """Validate lot/serial tracking requirements"""
        if item.tracking_type == TrackingType.LOT:
            if not line.lot_id:
                raise ValidationError(f'الصنف {item.name_ar} يتطلب رقم تشغيلة (Lot)')
        
        elif item.tracking_type == TrackingType.SERIAL:
            if not line.serial_id:
                raise ValidationError(f'الصنف {item.name_ar} يتطلب رقم تسلسلي (Serial)')
        
        elif item.tracking_type == TrackingType.LOT_EXPIRY:
            if not line.lot_id:
                raise ValidationError(f'الصنف {item.name_ar} يتطلب رقم تشغيلة وتاريخ انتهاء')
    
    def _validate_negative_stock(self, document: DocumentHeader, 
                                 line: DocumentLine, item: Item,
                                 session: Session):
        """Validate against negative stock policy"""
        warehouse_id = document.from_warehouse_id
        
        # Get current stock
        query = session.query(StockBalance).filter_by(
            company_id=document.company_id,
            warehouse_id=warehouse_id,
            item_id=line.item_id
        )
        
        if line.lot_id:
            query = query.filter_by(lot_id=line.lot_id)
        if line.serial_id:
            query = query.filter_by(serial_id=line.serial_id)
        if line.from_location_id:
            query = query.filter_by(location_id=line.from_location_id)
        
        balance = query.first()
        current_qty = balance.on_hand_qty if balance else Decimal(0)
        
        # Check if issuing more than available
        if current_qty < line.base_qty:
            # Check policy
            block_negative = self.policy_service.get_policy_value(
                session=session,
                policy_name='BLOCK_NEGATIVE_STOCK',
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                item_id=line.item_id
            )
            
            if block_negative:
                raise ValidationError(
                    f'الصنف {item.name_ar}: الكمية المتاحة ({current_qty}) '
                    f'أقل من الكمية المطلوبة ({line.base_qty})'
                )
    
    def validate_location(self, location_id: Optional[int], session: Session) -> bool:
        """Validate location exists and is active"""
        if not location_id:
            return True
        
        from data import Location
        location = session.query(Location).filter_by(id=location_id).first()
        
        if not location:
            raise ValidationError(f'الموقع رقم {location_id} غير موجود')
        
        if not location.is_active:
            raise ValidationError(f'الموقع {location.code} غير نشط')
        
        return True
