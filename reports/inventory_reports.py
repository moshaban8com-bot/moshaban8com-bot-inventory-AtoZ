"""
Inventory reports and queries
تقارير المخزون
"""

from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from data import (
    Item, StockBalance, InventoryLedger, Warehouse, Location,
    ItemCategory, UOM, Lot, Serial
)


class InventoryReports:
    """Inventory reporting queries"""
    
    @staticmethod
    def stock_on_hand(session: Session, company_id: int,
                     warehouse_id: Optional[int] = None,
                     item_id: Optional[int] = None) -> List[Dict]:
        """
        Stock on hand report
        تقرير الأرصدة الحالية
        
        Returns:
            List of dict with item details and current stock
        """
        query = session.query(
            Item.code,
            Item.name_ar,
            Item.name_en,
            UOM.code.label('uom'),
            Warehouse.name_ar.label('warehouse'),
            StockBalance.on_hand_qty,
            StockBalance.avg_cost,
            StockBalance.on_hand_value
        ).join(
            StockBalance, Item.id == StockBalance.item_id
        ).join(
            UOM, Item.base_uom_id == UOM.id
        ).join(
            Warehouse, StockBalance.warehouse_id == Warehouse.id
        ).filter(
            StockBalance.company_id == company_id,
            StockBalance.on_hand_qty > 0
        )
        
        if warehouse_id:
            query = query.filter(StockBalance.warehouse_id == warehouse_id)
        
        if item_id:
            query = query.filter(Item.id == item_id)
        
        results = []
        for row in query.all():
            results.append({
                'item_code': row.code,
                'item_name_ar': row.name_ar,
                'item_name_en': row.name_en,
                'uom': row.uom,
                'warehouse': row.warehouse,
                'qty': float(row.on_hand_qty),
                'avg_cost': float(row.avg_cost),
                'value': float(row.on_hand_value)
            })
        
        return results
    
    @staticmethod
    def inventory_valuation(session: Session, company_id: int,
                           warehouse_id: Optional[int] = None) -> Dict:
        """
        Inventory valuation summary
        ملخص قيمة المخزون
        
        Returns:
            Summary dict with total quantity and value
        """
        query = session.query(
            func.sum(StockBalance.on_hand_qty).label('total_qty'),
            func.sum(StockBalance.on_hand_value).label('total_value'),
            func.count(func.distinct(StockBalance.item_id)).label('item_count')
        ).filter(
            StockBalance.company_id == company_id,
            StockBalance.on_hand_qty > 0
        )
        
        if warehouse_id:
            query = query.filter(StockBalance.warehouse_id == warehouse_id)
        
        result = query.first()
        
        return {
            'total_qty': float(result.total_qty or 0),
            'total_value': float(result.total_value or 0),
            'item_count': result.item_count or 0
        }
    
    @staticmethod
    def movement_summary(session: Session, company_id: int,
                        from_date: date, to_date: date,
                        item_id: Optional[int] = None,
                        warehouse_id: Optional[int] = None) -> List[Dict]:
        """
        Movement summary by item
        ملخص حركة الأصناف
        
        Returns:
            List of dict with item movements
        """
        query = session.query(
            Item.code,
            Item.name_ar,
            Item.name_en,
            func.sum(InventoryLedger.qty_in).label('total_in'),
            func.sum(InventoryLedger.qty_out).label('total_out'),
            func.sum(InventoryLedger.value_in).label('value_in'),
            func.sum(InventoryLedger.value_out).label('value_out')
        ).join(
            Item, InventoryLedger.item_id == Item.id
        ).filter(
            InventoryLedger.company_id == company_id,
            InventoryLedger.posting_date >= from_date,
            InventoryLedger.posting_date <= to_date
        ).group_by(
            Item.id, Item.code, Item.name_ar, Item.name_en
        )
        
        if warehouse_id:
            query = query.filter(InventoryLedger.warehouse_id == warehouse_id)
        
        if item_id:
            query = query.filter(Item.id == item_id)
        
        results = []
        for row in query.all():
            net_qty = (row.total_in or 0) - (row.total_out or 0)
            net_value = (row.value_in or 0) - (row.value_out or 0)
            
            results.append({
                'item_code': row.code,
                'item_name_ar': row.name_ar,
                'item_name_en': row.name_en,
                'qty_in': float(row.total_in or 0),
                'qty_out': float(row.total_out or 0),
                'net_qty': float(net_qty),
                'value_in': float(row.value_in or 0),
                'value_out': float(row.value_out or 0),
                'net_value': float(net_value)
            })
        
        return results
    
    @staticmethod
    def item_card(session: Session, company_id: int, item_id: int,
                 warehouse_id: Optional[int] = None,
                 from_date: Optional[date] = None,
                 to_date: Optional[date] = None) -> List[Dict]:
        """
        Item card (ledger) report
        كرت صنف
        
        Returns:
            List of all transactions for an item
        """
        query = session.query(
            InventoryLedger.posting_date,
            InventoryLedger.doc_type,
            InventoryLedger.doc_no,
            Warehouse.name_ar.label('warehouse'),
            InventoryLedger.qty_in,
            InventoryLedger.qty_out,
            InventoryLedger.unit_cost,
            InventoryLedger.value_in,
            InventoryLedger.value_out
        ).join(
            Warehouse, InventoryLedger.warehouse_id == Warehouse.id
        ).filter(
            InventoryLedger.company_id == company_id,
            InventoryLedger.item_id == item_id
        ).order_by(
            InventoryLedger.posting_date,
            InventoryLedger.id
        )
        
        if warehouse_id:
            query = query.filter(InventoryLedger.warehouse_id == warehouse_id)
        
        if from_date:
            query = query.filter(InventoryLedger.posting_date >= from_date)
        
        if to_date:
            query = query.filter(InventoryLedger.posting_date <= to_date)
        
        results = []
        running_qty = Decimal(0)
        running_value = Decimal(0)
        
        for row in query.all():
            running_qty += (row.qty_in - row.qty_out)
            running_value += (row.value_in - row.value_out)
            
            results.append({
                'posting_date': row.posting_date.strftime('%Y-%m-%d'),
                'doc_type': row.doc_type.value,
                'doc_no': row.doc_no,
                'warehouse': row.warehouse,
                'qty_in': float(row.qty_in),
                'qty_out': float(row.qty_out),
                'unit_cost': float(row.unit_cost or 0),
                'value_in': float(row.value_in),
                'value_out': float(row.value_out),
                'balance_qty': float(running_qty),
                'balance_value': float(running_value)
            })
        
        return results
    
    @staticmethod
    def reorder_report(session: Session, company_id: int) -> List[Dict]:
        """
        Items below reorder point
        الأصناف التي وصلت لنقطة إعادة الطلب
        
        Returns:
            List of items that need reordering
        """
        query = session.query(
            Item.code,
            Item.name_ar,
            Item.name_en,
            Item.reorder_point,
            Item.min_qty,
            Item.max_qty,
            UOM.code.label('uom'),
            func.sum(StockBalance.on_hand_qty).label('current_qty')
        ).join(
            StockBalance, Item.id == StockBalance.item_id
        ).join(
            UOM, Item.base_uom_id == UOM.id
        ).filter(
            Item.company_id == company_id,
            Item.reorder_point > 0
        ).group_by(
            Item.id, Item.code, Item.name_ar, Item.name_en,
            Item.reorder_point, Item.min_qty, Item.max_qty, UOM.code
        ).having(
            func.sum(StockBalance.on_hand_qty) <= Item.reorder_point
        )
        
        results = []
        for row in query.all():
            shortage = float(row.max_qty - (row.current_qty or 0))
            
            results.append({
                'item_code': row.code,
                'item_name_ar': row.name_ar,
                'item_name_en': row.name_en,
                'uom': row.uom,
                'current_qty': float(row.current_qty or 0),
                'reorder_point': float(row.reorder_point),
                'min_qty': float(row.min_qty),
                'max_qty': float(row.max_qty),
                'shortage': shortage,
                'order_qty': shortage  # Suggested order quantity
            })
        
        return results
    
    @staticmethod
    def lot_traceability(session: Session, company_id: int,
                        lot_id: int) -> List[Dict]:
        """
        Lot traceability report
        تتبع رقم التشغيلة
        
        Returns:
            All transactions for a specific lot
        """
        query = session.query(
            InventoryLedger.posting_date,
            InventoryLedger.doc_type,
            InventoryLedger.doc_no,
            Item.code.label('item_code'),
            Item.name_ar.label('item_name'),
            Warehouse.name_ar.label('warehouse'),
            InventoryLedger.qty_in,
            InventoryLedger.qty_out
        ).join(
            Item, InventoryLedger.item_id == Item.id
        ).join(
            Warehouse, InventoryLedger.warehouse_id == Warehouse.id
        ).filter(
            InventoryLedger.company_id == company_id,
            InventoryLedger.lot_id == lot_id
        ).order_by(
            InventoryLedger.posting_date,
            InventoryLedger.id
        )
        
        results = []
        for row in query.all():
            results.append({
                'posting_date': row.posting_date.strftime('%Y-%m-%d'),
                'doc_type': row.doc_type.value,
                'doc_no': row.doc_no,
                'item_code': row.item_code,
                'item_name': row.item_name,
                'warehouse': row.warehouse,
                'qty_in': float(row.qty_in),
                'qty_out': float(row.qty_out)
            })
        
        return results
