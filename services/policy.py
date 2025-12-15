"""
Policy resolution service - Hierarchical policy resolution
خدمة حل السياسات - حل السياسات الهرمية
"""

from typing import Optional

from sqlalchemy.orm import Session

from data import Policy, PolicyScope


class PolicyService:
    """Service for resolving policies with hierarchy"""
    
    def get_policy_value(self, session: Session, policy_name: str,
                        company_id: int,
                        warehouse_id: Optional[int] = None,
                        doc_type: Optional[str] = None,
                        category_id: Optional[int] = None,
                        item_id: Optional[int] = None) -> bool:
        """
        Get policy value with hierarchical resolution
        
        Policy hierarchy (most specific to least specific):
        ITEM → CATEGORY → DOCTYPE → WAREHOUSE → COMPANY → GLOBAL
        
        Args:
            session: Database session
            policy_name: Name of the policy
            company_id: Company ID
            warehouse_id: Warehouse ID (optional)
            doc_type: Document type (optional)
            category_id: Item category ID (optional)
            item_id: Item ID (optional)
            
        Returns:
            Policy value (True/False)
        """
        # Try ITEM level
        if item_id:
            policy = session.query(Policy).filter_by(
                scope_type=PolicyScope.ITEM,
                item_id=item_id,
                policy_name=policy_name
            ).first()
            if policy:
                return policy.policy_value
        
        # Try CATEGORY level
        if category_id:
            policy = session.query(Policy).filter_by(
                scope_type=PolicyScope.CATEGORY,
                category_id=category_id,
                policy_name=policy_name
            ).first()
            if policy:
                return policy.policy_value
        
        # Try DOCTYPE level
        if doc_type:
            policy = session.query(Policy).filter_by(
                scope_type=PolicyScope.DOCTYPE,
                company_id=company_id,
                doc_type=doc_type,
                policy_name=policy_name
            ).first()
            if policy:
                return policy.policy_value
        
        # Try WAREHOUSE level
        if warehouse_id:
            policy = session.query(Policy).filter_by(
                scope_type=PolicyScope.WAREHOUSE,
                warehouse_id=warehouse_id,
                policy_name=policy_name
            ).first()
            if policy:
                return policy.policy_value
        
        # Try COMPANY level
        policy = session.query(Policy).filter_by(
            scope_type=PolicyScope.COMPANY,
            company_id=company_id,
            policy_name=policy_name
        ).first()
        if policy:
            return policy.policy_value
        
        # Try GLOBAL level
        policy = session.query(Policy).filter_by(
            scope_type=PolicyScope.GLOBAL,
            policy_name=policy_name
        ).first()
        if policy:
            return policy.policy_value
        
        # Default values for known policies
        return self._get_default_policy_value(policy_name)
    
    def _get_default_policy_value(self, policy_name: str) -> bool:
        """Get default value for a policy if not configured"""
        defaults = {
            'BLOCK_NEGATIVE_STOCK': True,
            'ALLOW_NEGATIVE_WITH_APPROVAL': False,
            'BLOCK_ISSUE_FROM_EMPTY_LOCATION': False,
            'ENFORCE_SERIAL_TRACKING': True,
            'ENFORCE_LOT_TRACKING': True,
            'ENFORCE_EXPIRY_TRACKING': True,
            'FEFO_PICKING': False,
            'LOCK_POSTED_DOCUMENTS': True,
            'ENABLE_WORKFLOW_SEPARATION': False,
            'REQUIRE_REASON_CODE_FOR_ADJUSTMENTS': True,
        }
        return defaults.get(policy_name, False)
    
    def create_policy(self, session: Session, policy_name: str,
                     policy_value: bool, scope_type: PolicyScope,
                     company_id: Optional[int] = None,
                     warehouse_id: Optional[int] = None,
                     doc_type: Optional[str] = None,
                     category_id: Optional[int] = None,
                     item_id: Optional[int] = None,
                     override_allowed: bool = False,
                     override_requires_approval: bool = False,
                     approval_role_id: Optional[int] = None,
                     reason_required: bool = False) -> Policy:
        """Create or update a policy"""
        # Check if policy already exists
        query = session.query(Policy).filter_by(
            policy_name=policy_name,
            scope_type=scope_type
        )
        
        if company_id:
            query = query.filter_by(company_id=company_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if doc_type:
            query = query.filter_by(doc_type=doc_type)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        
        policy = query.first()
        
        if policy:
            # Update existing policy
            policy.policy_value = policy_value
            policy.override_allowed = override_allowed
            policy.override_requires_approval = override_requires_approval
            policy.approval_role_id = approval_role_id
            policy.reason_required = reason_required
        else:
            # Create new policy
            policy = Policy(
                policy_name=policy_name,
                policy_value=policy_value,
                scope_type=scope_type,
                company_id=company_id,
                warehouse_id=warehouse_id,
                doc_type=doc_type,
                category_id=category_id,
                item_id=item_id,
                override_allowed=override_allowed,
                override_requires_approval=override_requires_approval,
                approval_role_id=approval_role_id,
                reason_required=reason_required
            )
            session.add(policy)
        
        return policy
