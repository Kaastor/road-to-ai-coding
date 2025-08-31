"""Audit logging models and functionality."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json


class AuditAction(str, Enum):
    """Types of auditable actions."""
    CREATE_MODEL = "create_model"
    UPDATE_MODEL = "update_model"
    DELETE_MODEL = "delete_model"
    CREATE_VERSION = "create_version"
    UPDATE_VERSION_STATUS = "update_version_status"
    UPDATE_VERSION_METADATA = "update_version_metadata"
    UPLOAD_ARTIFACT = "upload_artifact"
    DOWNLOAD_ARTIFACT = "download_artifact"
    DELETE_ARTIFACT = "delete_artifact"
    PROMOTE_MODEL = "promote_model"


@dataclass
class AuditLog:
    """Represents an audit log entry."""
    id: UUID
    action: AuditAction
    resource_type: str  # "model" or "model_version"
    resource_id: UUID
    user_id: Optional[str]  # For future authentication integration
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        action: AuditAction,
        resource_type: str,
        resource_id: UUID,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create a new audit log entry."""
        return cls(
            id=uuid4(),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details=details or {},
            previous_state=previous_state,
            new_state=new_state
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary for serialization."""
        return {
            "id": str(self.id),
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id),
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "previous_state": self.previous_state,
            "new_state": self.new_state
        }
    
    def to_json(self) -> str:
        """Convert audit log to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """Simple audit logger that logs to standard logging."""
    
    def __init__(self):
        import logging
        self.logger = logging.getLogger("audit")
        
    async def log(self, audit_entry: AuditLog) -> None:
        """Log an audit entry."""
        self.logger.info(f"AUDIT: {audit_entry.to_json()}")
    
    async def log_model_operation(
        self,
        action: AuditAction,
        model_id: UUID,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a model-related operation."""
        audit_entry = AuditLog.create(
            action=action,
            resource_type="model",
            resource_id=model_id,
            user_id=user_id,
            details=details,
            previous_state=previous_state,
            new_state=new_state
        )
        await self.log(audit_entry)
    
    async def log_version_operation(
        self,
        action: AuditAction,
        version_id: UUID,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a model version-related operation."""
        audit_entry = AuditLog.create(
            action=action,
            resource_type="model_version",
            resource_id=version_id,
            user_id=user_id,
            details=details,
            previous_state=previous_state,
            new_state=new_state
        )
        await self.log(audit_entry)