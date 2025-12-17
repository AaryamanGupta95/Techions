from datetime import datetime
from typing import Dict, Any
from app.core.database import get_database
from app.models.security import AgentLog

async def log_agent_action(
    agent_name: str,
    action: str,
    input_data: Dict[str, Any] = None,
    output_data: Dict[str, Any] = None,
    execution_time_ms: float = 0.0,
    status: str = "success",
    error_message: str = None,
    anomaly_score: float = 0.0,
    is_anomaly: bool = False
) -> None:
    """Log agent action for UEBA analysis"""
    db = get_database()
    log_entry = AgentLog(
        agent_name=agent_name,
        action=action,
        timestamp=datetime.utcnow(),
        input_data=input_data or {},
        output_data=output_data or {},
        execution_time_ms=execution_time_ms,
        status=status,
        error_message=error_message,
        anomaly_score=anomaly_score,
        is_anomaly=is_anomaly
    )
    await db.agent_logs.insert_one(log_entry.dict(by_alias=True))

