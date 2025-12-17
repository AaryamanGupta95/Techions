from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.security import SecurityEvent
from sklearn.ensemble import IsolationForest
import numpy as np
import uuid

class UEBASecurityAgent(BaseAgent):
    """Detects abnormal agent behavior using UEBA"""
    
    def __init__(self):
        super().__init__("UEBASecurityAgent")
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_fitted = False
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "analyze_logs")
        
        if action == "analyze_logs":
            return await self._analyze_agent_logs()
        elif action == "check_specific_agent":
            return await self._check_agent(input_data.get("agent_name"))
        else:
            return {"status": "error", "message": "Unknown action"}
    
    async def _analyze_agent_logs(self) -> Dict[str, Any]:
        """Analyze agent logs for anomalies"""
        db = get_database()
        
        # Get recent logs (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        logs = await db.agent_logs.find({
            "timestamp": {"$gte": cutoff_time}
        }).to_list(1000)
        
        if not logs:
            return {"status": "success", "anomalies": [], "message": "No logs to analyze"}
        
        # Extract features for analysis
        features = []
        for log in logs:
            features.append([
                log.get("execution_time_ms", 0),
                1 if log.get("status") == "error" else 0,
                len(log.get("input_data", {})),
                len(log.get("output_data", {})),
            ])
        
        # Train model if needed
        if not self.is_fitted or len(features) > 100:
            if len(features) >= 10:
                X = np.array(features)
                self.model.fit(X)
                self.is_fitted = True
        
        # Detect anomalies
        anomalies = []
        if self.is_fitted and len(features) > 0:
            X = np.array(features)
            predictions = self.model.predict(X)
            anomaly_scores = self.model.score_samples(X)
            
            # Normalize scores to 0-1 range
            min_score = anomaly_scores.min()
            max_score = anomaly_scores.max()
            normalized_scores = (anomaly_scores - min_score) / (max_score - min_score) if max_score != min_score else [0.5] * len(anomaly_scores)
            
            for i, log in enumerate(logs):
                is_anomaly = predictions[i] == -1
                score = float(1 - normalized_scores[i])  # Invert so higher = more anomalous
                
                # Update log with anomaly detection
                await db.agent_logs.update_one(
                    {"_id": log["_id"]},
                    {"$set": {"anomaly_score": score, "is_anomaly": is_anomaly}}
                )
                
                if is_anomaly or score > 0.7:
                    anomalies.append({
                        "agent_name": log.get("agent_name"),
                        "action": log.get("action"),
                        "timestamp": log.get("timestamp"),
                        "anomaly_score": round(score, 3),
                        "status": log.get("status"),
                        "execution_time_ms": log.get("execution_time_ms"),
                    })
                    
                    # Create security event for critical anomalies
                    if score > 0.8:
                        await self._create_security_event(log, score)
        
        return {
            "status": "success",
            "anomalies": anomalies,
            "total_logs_analyzed": len(logs),
            "anomaly_count": len(anomalies)
        }
    
    async def _check_agent(self, agent_name: str) -> Dict[str, Any]:
        """Check specific agent for anomalies"""
        db = get_database()
        
        # Get recent logs for this agent
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        logs = await db.agent_logs.find({
            "agent_name": agent_name,
            "timestamp": {"$gte": cutoff_time}
        }).sort("timestamp", -1).limit(100).to_list(100)
        
        if not logs:
            return {"status": "success", "message": "No recent activity for this agent"}
        
        # Calculate statistics
        error_count = sum(1 for log in logs if log.get("status") == "error")
        avg_execution_time = sum(log.get("execution_time_ms", 0) for log in logs) / len(logs)
        anomaly_count = sum(1 for log in logs if log.get("is_anomaly", False))
        avg_anomaly_score = sum(log.get("anomaly_score", 0) for log in logs) / len(logs)
        
        # Check for patterns
        actions = [log.get("action") for log in logs]
        action_counts = Counter(actions)
        most_common_action = action_counts.most_common(1)[0] if action_counts else None
        
        return {
            "status": "success",
            "agent_name": agent_name,
            "statistics": {
                "total_actions": len(logs),
                "error_count": error_count,
                "error_rate": round(error_count / len(logs) * 100, 2),
                "average_execution_time_ms": round(avg_execution_time, 2),
                "anomaly_count": anomaly_count,
                "average_anomaly_score": round(avg_anomaly_score, 3),
                "most_common_action": most_common_action[0] if most_common_action else None,
                "action_frequency": dict(action_counts)
            },
            "risk_level": self._assess_risk(error_count, avg_anomaly_score, len(logs))
        }
    
    def _assess_risk(self, error_count: int, avg_anomaly_score: float, total_actions: int) -> str:
        """Assess risk level"""
        error_rate = error_count / total_actions if total_actions > 0 else 0
        
        if error_rate > 0.3 or avg_anomaly_score > 0.7:
            return "high"
        elif error_rate > 0.1 or avg_anomaly_score > 0.5:
            return "medium"
        else:
            return "low"
    
    async def _create_security_event(self, log: Dict[str, Any], anomaly_score: float) -> None:
        """Create security event for critical anomalies"""
        db = get_database()
        
        event_id = f"SEC_{uuid.uuid4().hex[:8].upper()}"
        
        # Determine severity
        if anomaly_score > 0.9:
            severity = "critical"
        elif anomaly_score > 0.8:
            severity = "high"
        else:
            severity = "medium"
        
        event = SecurityEvent(
            event_id=event_id,
            event_type="anomaly",
            severity=severity,
            agent_name=log.get("agent_name"),
            description=f"Anomalous behavior detected in {log.get('agent_name')}: {log.get('action')}",
            details={
                "anomaly_score": anomaly_score,
                "execution_time_ms": log.get("execution_time_ms"),
                "status": log.get("status"),
                "input_data": log.get("input_data"),
            },
            detected_at=log.get("timestamp", datetime.utcnow()),
            resolved=False
        )
        
        await db.security_events.insert_one(event.dict(by_alias=True))

