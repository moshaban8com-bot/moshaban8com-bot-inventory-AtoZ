"""
Authentication and session management service
خدمة المصادقة وإدارة الجلسات
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from data import session_scope, User, AuditLog
from config import SECURITY_CONFIG


class AuthenticationError(Exception):
    """خطأ في المصادقة"""
    pass


class AuthService:
    """Authentication service for user login and session management"""
    
    def __init__(self):
        self.current_user: Optional[User] = None
        self.current_company_id: Optional[int] = None
        self.current_warehouse_id: Optional[int] = None
        self.session_start: Optional[datetime] = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=SECURITY_CONFIG['bcrypt_rounds'])
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def login(self, username: str, password: str, ip_address: str = None) -> User:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Plain text password
            ip_address: IP address of the login attempt
            
        Returns:
            User object if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        with session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            
            if not user:
                # Log failed attempt
                self._log_failed_login(session, username, ip_address, 'User not found')
                raise AuthenticationError('اسم المستخدم أو كلمة المرور غير صحيحة')
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                raise AuthenticationError(f'الحساب مقفل حتى {user.locked_until.strftime("%Y-%m-%d %H:%M")}')
            
            # Check if account is active
            if not user.is_active:
                raise AuthenticationError('الحساب غير نشط')
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                # Increment failed attempts
                user.failed_login_attempts += 1
                
                # Lock account if max attempts reached
                if user.failed_login_attempts >= SECURITY_CONFIG['max_login_attempts']:
                    user.locked_until = datetime.utcnow() + timedelta(
                        seconds=SECURITY_CONFIG['lockout_duration']
                    )
                    session.commit()
                    raise AuthenticationError(
                        f'تم تجاوز عدد المحاولات المسموح بها. الحساب مقفل حتى {user.locked_until.strftime("%Y-%m-%d %H:%M")}'
                    )
                
                self._log_failed_login(session, username, ip_address, 'Invalid password')
                session.commit()
                raise AuthenticationError('اسم المستخدم أو كلمة المرور غير صحيحة')
            
            # Successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Create audit log
            audit = AuditLog(
                user_id=user.id,
                action='LOGIN',
                description=f'تسجيل دخول ناجح من {ip_address or "Unknown"}',
                ip_address=ip_address
            )
            session.add(audit)
            session.commit()
            
            # Set current session
            self.current_user = user
            self.session_start = datetime.utcnow()
            
            # Refresh user object to avoid detached instance
            session.refresh(user)
            return user
    
    def _log_failed_login(self, session, username: str, ip_address: str, reason: str):
        """Log failed login attempt"""
        audit = AuditLog(
            user_id=None,
            action='LOGIN_FAILED',
            description=f'محاولة تسجيل دخول فاشلة: {username} - {reason}',
            ip_address=ip_address
        )
        session.add(audit)
    
    def logout(self):
        """End current session"""
        if self.current_user:
            with session_scope() as session:
                audit = AuditLog(
                    user_id=self.current_user.id,
                    company_id=self.current_company_id,
                    action='LOGOUT',
                    description='تسجيل خروج'
                )
                session.add(audit)
        
        self.current_user = None
        self.current_company_id = None
        self.current_warehouse_id = None
        self.session_start = None
    
    def set_current_company(self, company_id: int):
        """Set the current company for the session"""
        if not self.current_user:
            raise AuthenticationError('لا يوجد مستخدم مسجل دخول')
        
        # TODO: Verify user has access to this company
        self.current_company_id = company_id
        
        with session_scope() as session:
            audit = AuditLog(
                user_id=self.current_user.id,
                company_id=company_id,
                action='COMPANY_CHANGE',
                description=f'تغيير الشركة الحالية إلى {company_id}'
            )
            session.add(audit)
    
    def set_current_warehouse(self, warehouse_id: int):
        """Set the current warehouse for the session"""
        if not self.current_user:
            raise AuthenticationError('لا يوجد مستخدم مسجل دخول')
        
        # TODO: Verify user has access to this warehouse
        self.current_warehouse_id = warehouse_id
        
        with session_scope() as session:
            audit = AuditLog(
                user_id=self.current_user.id,
                company_id=self.current_company_id,
                action='WAREHOUSE_CHANGE',
                description=f'تغيير المخزن الحالي إلى {warehouse_id}'
            )
            session.add(audit)
    
    def is_session_valid(self) -> bool:
        """Check if the current session is still valid"""
        if not self.current_user or not self.session_start:
            return False
        
        session_duration = (datetime.utcnow() - self.session_start).total_seconds()
        return session_duration < SECURITY_CONFIG['session_timeout']
    
    def check_permission(self, permission_code: str) -> bool:
        """
        Check if current user has a specific permission
        
        Args:
            permission_code: Permission code to check
            
        Returns:
            True if user has permission, False otherwise
        """
        if not self.current_user:
            return False
        
        # Admin users have all permissions
        if self.current_user.is_admin:
            return True
        
        # TODO: Implement permission checking logic
        # Query user roles and their permissions
        
        return False


# Global authentication service instance
auth_service = AuthService()
