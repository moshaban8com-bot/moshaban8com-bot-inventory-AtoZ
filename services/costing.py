"""
Costing service - Average cost calculation
خدمة التكلفة - حساب متوسط التكلفة
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from data import StockBalance, InventoryLedger
from config import COSTING_CONFIG


class CostingService:
    """Service for calculating item costs"""
    
    def get_average_cost(self, session: Session, company_id: int,
                        warehouse_id: int, item_id: int,
                        lot_id: Optional[int] = None) -> Decimal:
        """
        Get average cost for an item
        
        Args:
            session: Database session
            company_id: Company ID
            warehouse_id: Warehouse ID
            item_id: Item ID
            lot_id: Lot ID (optional)
            
        Returns:
            Average cost as Decimal
        """
        # Try to get from stock balance cache
        query = session.query(StockBalance).filter_by(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id
        )
        
        if lot_id:
            query = query.filter_by(lot_id=lot_id)
        
        balance = query.first()
        
        if balance and balance.on_hand_qty > 0:
            return self._round_cost(balance.avg_cost)
        
        # If not in cache, calculate from ledger
        return self._calculate_from_ledger(
            session, company_id, warehouse_id, item_id, lot_id
        )
    
    def _calculate_from_ledger(self, session: Session, company_id: int,
                               warehouse_id: int, item_id: int,
                               lot_id: Optional[int] = None) -> Decimal:
        """Calculate average cost from inventory ledger"""
        query = session.query(
            func.sum(InventoryLedger.qty_in - InventoryLedger.qty_out).label('total_qty'),
            func.sum(InventoryLedger.value_in - InventoryLedger.value_out).label('total_value')
        ).filter_by(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id
        )
        
        if lot_id:
            query = query.filter_by(lot_id=lot_id)
        
        result = query.first()
        
        if result and result.total_qty and result.total_qty > 0:
            avg_cost = result.total_value / result.total_qty
            return self._round_cost(avg_cost)
        
        return Decimal(0)
    
    def _round_cost(self, cost: Decimal) -> Decimal:
        """Round cost to configured precision"""
        if cost is None:
            return Decimal(0)
        
        precision = COSTING_CONFIG['precision']
        return round(Decimal(cost), precision)
    
    def calculate_total_value(self, session: Session, company_id: int,
                             warehouse_id: Optional[int] = None) -> Decimal:
        """
        Calculate total inventory value
        
        Args:
            session: Database session
            company_id: Company ID
            warehouse_id: Warehouse ID (optional, for specific warehouse)
            
        Returns:
            Total inventory value
        """
        query = session.query(
            func.sum(StockBalance.on_hand_value)
        ).filter_by(company_id=company_id)
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        result = query.scalar()
        return Decimal(result) if result else Decimal(0)
