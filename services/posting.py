"""
Posting service - Handle document posting to inventory ledger
خدمة الترحيل - ترحيل المستندات إلى دفتر الحركة
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from data import (
    DocumentHeader, DocumentLine, DocumentStatus, DocumentType,
    InventoryLedger, StockBalance, session_scope
)
from services.costing import CostingService
from services.validation import ValidationService


class PostingError(Exception):
    """خطأ في الترحيل"""
    pass


class PostingService:
    """Service for posting inventory documents"""
    
    def __init__(self):
        self.costing_service = CostingService()
        self.validation_service = ValidationService()
    
    def post_document(self, document_id: int, user_id: int, posting_date: Optional[date] = None) -> bool:
        """
        Post a document to the inventory ledger
        
        Args:
            document_id: Document ID to post
            user_id: User performing the posting
            posting_date: Date to post the document (defaults to today)
            
        Returns:
            True if posting successful
            
        Raises:
            PostingError: If posting fails
        """
        if posting_date is None:
            posting_date = date.today()
        
        with session_scope() as session:
            # Get document with lines
            document = session.query(DocumentHeader).filter_by(id=document_id).first()
            
            if not document:
                raise PostingError(f'المستند رقم {document_id} غير موجود')
            
            # Validate document can be posted
            self._validate_can_post(document)
            
            # Validate document lines
            self.validation_service.validate_document(document, session)
            
            # Post based on document type
            if document.doc_type == DocumentType.GRN_RECEIPT:
                self._post_receipt(document, posting_date, user_id, session)
            elif document.doc_type == DocumentType.ISSUE:
                self._post_issue(document, posting_date, user_id, session)
            elif document.doc_type == DocumentType.TRANSFER:
                self._post_transfer(document, posting_date, user_id, session)
            elif document.doc_type == DocumentType.ADJUSTMENT:
                self._post_adjustment(document, posting_date, user_id, session)
            elif document.doc_type == DocumentType.RETURN_IN:
                self._post_return_in(document, posting_date, user_id, session)
            elif document.doc_type == DocumentType.RETURN_OUT:
                self._post_return_out(document, posting_date, user_id, session)
            else:
                raise PostingError(f'نوع المستند {document.doc_type} غير مدعوم للترحيل')
            
            # Update document status
            document.status = DocumentStatus.POSTED
            document.posting_date = posting_date
            document.posted_by = user_id
            document.posted_at = datetime.utcnow()
            
            session.commit()
            
            return True
    
    def _validate_can_post(self, document: DocumentHeader):
        """Validate document can be posted"""
        if document.status == DocumentStatus.POSTED:
            raise PostingError('المستند مُرحّل بالفعل')
        
        if document.status == DocumentStatus.CANCELLED:
            raise PostingError('لا يمكن ترحيل مستند ملغي')
        
        if not document.lines:
            raise PostingError('المستند لا يحتوي على بنود')
    
    def _post_receipt(self, document: DocumentHeader, posting_date: date, 
                     user_id: int, session: Session):
        """Post a receipt document (GRN)"""
        warehouse_id = document.to_warehouse_id
        
        for line in document.lines:
            # Create ledger entry for receipt
            ledger = InventoryLedger(
                posting_date=posting_date,
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                location_id=line.to_location_id,
                item_id=line.item_id,
                qty_in=line.base_qty,
                qty_out=Decimal(0),
                unit_cost=line.unit_cost or Decimal(0),
                value_in=line.total_cost or Decimal(0),
                value_out=Decimal(0),
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                doc_type=document.doc_type,
                doc_id=document.id,
                doc_no=document.doc_no,
                line_no=line.line_no,
                created_by=user_id
            )
            session.add(ledger)
            
            # Update stock balance
            self._update_stock_balance(
                session=session,
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                location_id=line.to_location_id,
                item_id=line.item_id,
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                qty_change=line.base_qty,
                value_change=line.total_cost or Decimal(0)
            )
    
    def _post_issue(self, document: DocumentHeader, posting_date: date,
                   user_id: int, session: Session):
        """Post an issue document"""
        warehouse_id = document.from_warehouse_id
        
        for line in document.lines:
            # Get current average cost
            avg_cost = self.costing_service.get_average_cost(
                session=session,
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                item_id=line.item_id,
                lot_id=line.lot_id
            )
            
            value_out = line.base_qty * avg_cost
            
            # Create ledger entry for issue
            ledger = InventoryLedger(
                posting_date=posting_date,
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                location_id=line.from_location_id,
                item_id=line.item_id,
                qty_in=Decimal(0),
                qty_out=line.base_qty,
                unit_cost=avg_cost,
                value_in=Decimal(0),
                value_out=value_out,
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                doc_type=document.doc_type,
                doc_id=document.id,
                doc_no=document.doc_no,
                line_no=line.line_no,
                created_by=user_id
            )
            session.add(ledger)
            
            # Update stock balance
            self._update_stock_balance(
                session=session,
                company_id=document.company_id,
                warehouse_id=warehouse_id,
                location_id=line.from_location_id,
                item_id=line.item_id,
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                qty_change=-line.base_qty,
                value_change=-value_out
            )
    
    def _post_transfer(self, document: DocumentHeader, posting_date: date,
                      user_id: int, session: Session):
        """Post a transfer document (from warehouse to warehouse)"""
        for line in document.lines:
            # Get current average cost from source warehouse
            avg_cost = self.costing_service.get_average_cost(
                session=session,
                company_id=document.company_id,
                warehouse_id=document.from_warehouse_id,
                item_id=line.item_id,
                lot_id=line.lot_id
            )
            
            value = line.base_qty * avg_cost
            
            # Issue from source warehouse
            ledger_out = InventoryLedger(
                posting_date=posting_date,
                company_id=document.company_id,
                warehouse_id=document.from_warehouse_id,
                location_id=line.from_location_id,
                item_id=line.item_id,
                qty_in=Decimal(0),
                qty_out=line.base_qty,
                unit_cost=avg_cost,
                value_in=Decimal(0),
                value_out=value,
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                doc_type=document.doc_type,
                doc_id=document.id,
                doc_no=document.doc_no,
                line_no=line.line_no,
                created_by=user_id
            )
            session.add(ledger_out)
            
            # Receipt to destination warehouse
            ledger_in = InventoryLedger(
                posting_date=posting_date,
                company_id=document.company_id,
                warehouse_id=document.to_warehouse_id,
                location_id=line.to_location_id,
                item_id=line.item_id,
                qty_in=line.base_qty,
                qty_out=Decimal(0),
                unit_cost=avg_cost,
                value_in=value,
                value_out=Decimal(0),
                lot_id=line.lot_id,
                serial_id=line.serial_id,
                doc_type=document.doc_type,
                doc_id=document.id,
                doc_no=document.doc_no,
                line_no=line.line_no,
                created_by=user_id
            )
            session.add(ledger_in)
            
            # Update stock balances
            self._update_stock_balance(
                session, document.company_id, document.from_warehouse_id,
                line.from_location_id, line.item_id, line.lot_id, line.serial_id,
                -line.base_qty, -value
            )
            self._update_stock_balance(
                session, document.company_id, document.to_warehouse_id,
                line.to_location_id, line.item_id, line.lot_id, line.serial_id,
                line.base_qty, value
            )
    
    def _post_adjustment(self, document: DocumentHeader, posting_date: date,
                        user_id: int, session: Session):
        """Post an adjustment document"""
        warehouse_id = document.to_warehouse_id or document.from_warehouse_id
        
        for line in document.lines:
            # Positive adjustment (increase)
            if line.base_qty > 0:
                avg_cost = line.unit_cost or Decimal(0)
                value = line.base_qty * avg_cost
                
                ledger = InventoryLedger(
                    posting_date=posting_date,
                    company_id=document.company_id,
                    warehouse_id=warehouse_id,
                    location_id=line.to_location_id or line.from_location_id,
                    item_id=line.item_id,
                    qty_in=line.base_qty,
                    qty_out=Decimal(0),
                    unit_cost=avg_cost,
                    value_in=value,
                    value_out=Decimal(0),
                    lot_id=line.lot_id,
                    serial_id=line.serial_id,
                    doc_type=document.doc_type,
                    doc_id=document.id,
                    doc_no=document.doc_no,
                    line_no=line.line_no,
                    created_by=user_id
                )
                session.add(ledger)
                
                self._update_stock_balance(
                    session, document.company_id, warehouse_id,
                    line.to_location_id or line.from_location_id,
                    line.item_id, line.lot_id, line.serial_id,
                    line.base_qty, value
                )
            # Negative adjustment (decrease)
            elif line.base_qty < 0:
                qty_out = abs(line.base_qty)
                avg_cost = self.costing_service.get_average_cost(
                    session, document.company_id, warehouse_id, line.item_id, line.lot_id
                )
                value = qty_out * avg_cost
                
                ledger = InventoryLedger(
                    posting_date=posting_date,
                    company_id=document.company_id,
                    warehouse_id=warehouse_id,
                    location_id=line.from_location_id or line.to_location_id,
                    item_id=line.item_id,
                    qty_in=Decimal(0),
                    qty_out=qty_out,
                    unit_cost=avg_cost,
                    value_in=Decimal(0),
                    value_out=value,
                    lot_id=line.lot_id,
                    serial_id=line.serial_id,
                    doc_type=document.doc_type,
                    doc_id=document.id,
                    doc_no=document.doc_no,
                    line_no=line.line_no,
                    created_by=user_id
                )
                session.add(ledger)
                
                self._update_stock_balance(
                    session, document.company_id, warehouse_id,
                    line.from_location_id or line.to_location_id,
                    line.item_id, line.lot_id, line.serial_id,
                    -qty_out, -value
                )
    
    def _post_return_in(self, document: DocumentHeader, posting_date: date,
                       user_id: int, session: Session):
        """Post a return in document (return to supplier)"""
        self._post_issue(document, posting_date, user_id, session)
    
    def _post_return_out(self, document: DocumentHeader, posting_date: date,
                        user_id: int, session: Session):
        """Post a return out document (return from customer)"""
        self._post_receipt(document, posting_date, user_id, session)
    
    def _update_stock_balance(self, session: Session, company_id: int,
                             warehouse_id: int, location_id: Optional[int],
                             item_id: int, lot_id: Optional[int],
                             serial_id: Optional[int],
                             qty_change: Decimal, value_change: Decimal):
        """Update stock balance after posting"""
        # Find existing balance
        query = session.query(StockBalance).filter_by(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id
        )
        
        if location_id:
            query = query.filter_by(location_id=location_id)
        if lot_id:
            query = query.filter_by(lot_id=lot_id)
        if serial_id:
            query = query.filter_by(serial_id=serial_id)
        
        balance = query.first()
        
        if balance:
            # Update existing balance
            balance.on_hand_qty += qty_change
            balance.on_hand_value += value_change
            
            # Recalculate average cost
            if balance.on_hand_qty > 0:
                balance.avg_cost = balance.on_hand_value / balance.on_hand_qty
            else:
                balance.avg_cost = Decimal(0)
            
            balance.last_updated = datetime.utcnow()
        else:
            # Create new balance
            avg_cost = Decimal(0)
            if qty_change > 0:
                avg_cost = value_change / qty_change
            
            balance = StockBalance(
                company_id=company_id,
                warehouse_id=warehouse_id,
                location_id=location_id,
                item_id=item_id,
                lot_id=lot_id,
                serial_id=serial_id,
                on_hand_qty=qty_change,
                on_hand_value=value_change,
                avg_cost=avg_cost,
                last_updated=datetime.utcnow()
            )
            session.add(balance)
