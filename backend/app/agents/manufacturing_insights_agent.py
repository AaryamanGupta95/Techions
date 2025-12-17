from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.manufacturing import FailurePattern, RCACAPAInsight, RCACAPAAction
import uuid

class ManufacturingInsightsAgent(BaseAgent):
    """Generates RCA/CAPA insights for manufacturing teams"""
    
    def __init__(self):
        super().__init__("ManufacturingInsightsAgent")
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "generate_insights")
        
        if action == "generate_insights":
            return await self._generate_insights(input_data)
        elif action == "get_patterns":
            return await self._get_failure_patterns(input_data)
        else:
            return {"status": "error", "message": "Unknown action"}
    
    async def _generate_insights(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RCA/CAPA insights from failure patterns"""
        db = get_database()
        
        manufacturer = input_data.get("manufacturer")
        
        # Get failure patterns that need analysis
        query = {
            "occurrence_count": {"$gte": 3}  # Patterns with 3+ occurrences
        }
        if manufacturer:
            query["manufacturer"] = manufacturer
        
        patterns = await db.failure_patterns.find(query).to_list(100)
        
        if not patterns:
            return {"status": "success", "insights": [], "message": "No patterns requiring analysis"}
        
        insights = []
        for pattern in patterns:
            insight = await self._create_insight(pattern)
            insights.append(insight)
        
        return {
            "status": "success",
            "insights": insights,
            "count": len(insights)
        }
    
    async def _create_insight(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Create RCA/CAPA insight from failure pattern"""
        db = get_database()
        
        pattern_id = pattern["pattern_id"]
        
        # Check if insight already exists
        existing = await db.rcacapa_insights.find_one({"failure_pattern_id": pattern_id})
        if existing and existing.get("status") != "new":
            return existing
        
        # Analyze pattern to generate insights
        component = pattern.get("component", "Unknown")
        failure_type = pattern.get("failure_type", "Unknown")
        error_codes = pattern.get("error_codes", [])
        occurrence_count = pattern.get("occurrence_count", 0)
        severity = pattern.get("severity", "medium")
        
        # Generate root causes based on pattern
        root_causes = self._identify_root_causes(component, failure_type, error_codes)
        
        # Generate corrective actions
        corrective_actions = self._generate_corrective_actions(component, failure_type, root_causes)
        
        # Generate preventive actions
        preventive_actions = self._generate_preventive_actions(component, failure_type, root_causes)
        
        # Create insight
        insight_id = f"INSIGHT_{uuid.uuid4().hex[:8].upper()}"
        
        insight = RCACAPAInsight(
            insight_id=insight_id,
            failure_pattern_id=pattern_id,
            manufacturer=pattern.get("manufacturer", "Unknown"),
            title=f"RCA/CAPA Analysis: {component} {failure_type}",
            root_causes=root_causes,
            contributing_factors=self._identify_contributing_factors(component, failure_type),
            analysis_summary=self._generate_analysis_summary(pattern),
            corrective_actions=corrective_actions,
            preventive_actions=preventive_actions,
            affected_vehicles_count=occurrence_count,
            estimated_impact=self._estimate_impact(occurrence_count, severity),
            recommendation_priority=severity,
            manufacturing_team_notified=False,
            status="new"
        )
        
        # Upsert insight
        await db.rcacapa_insights.update_one(
            {"failure_pattern_id": pattern_id},
            {"$set": insight.dict(by_alias=True)},
            upsert=True
        )
        
        return insight.dict(by_alias=True)
    
    def _identify_root_causes(self, component: str, failure_type: str, error_codes: List[str]) -> List[str]:
        """Identify root causes based on component and failure type"""
        causes = []
        
        # Component-specific root causes
        if "engine" in component.lower():
            causes.append("Insufficient lubrication leading to excessive wear")
            causes.append("Overheating due to cooling system inefficiency")
        elif "battery" in component.lower():
            causes.append("Battery degradation over time")
            causes.append("Electrical system overload")
        elif "oil" in component.lower() or "pressure" in failure_type.lower():
            causes.append("Oil degradation and contamination")
            causes.append("Inadequate maintenance intervals")
        
        # Error code specific causes
        if "P0217" in error_codes:
            causes.append("Thermostat malfunction causing overheating")
        if "P0521" in error_codes:
            causes.append("Oil pump inefficiency or blockage")
        
        return causes if causes else ["Root cause analysis pending detailed investigation"]
    
    def _identify_contributing_factors(self, component: str, failure_type: str) -> List[str]:
        """Identify contributing factors"""
        return [
            "Environmental conditions (temperature extremes)",
            "Driving patterns and usage intensity",
            "Maintenance schedule adherence",
            "Component manufacturing variations"
        ]
    
    def _generate_corrective_actions(self, component: str, failure_type: str, root_causes: List[str]) -> List[RCACAPAAction]:
        """Generate corrective actions"""
        actions = []
        
        if "lubrication" in " ".join(root_causes).lower():
            actions.append(RCACAPAAction(
                action_type="corrective",
                description="Review and update lubrication specifications",
                priority="high",
                responsible_team="Engineering",
                status="pending"
            ))
        
        if "overheating" in " ".join(root_causes).lower():
            actions.append(RCACAPAAction(
                action_type="corrective",
                description="Enhance cooling system design",
                priority="high",
                responsible_team="Design",
                status="pending"
            ))
        
        actions.append(RCACAPAAction(
            action_type="corrective",
            description="Implement improved quality control measures",
            priority="medium",
            responsible_team="Quality",
            status="pending"
        ))
        
        return actions
    
    def _generate_preventive_actions(self, component: str, failure_type: str, root_causes: List[str]) -> List[RCACAPAAction]:
        """Generate preventive actions"""
        actions = [
            RCACAPAAction(
                action_type="preventive",
                description="Enhance predictive maintenance algorithms",
                priority="medium",
                responsible_team="Data Science",
                status="pending"
            ),
            RCACAPAAction(
                action_type="preventive",
                description="Develop early warning indicators for field monitoring",
                priority="medium",
                responsible_team="IoT Engineering",
                status="pending"
            ),
            RCACAPAAction(
                action_type="preventive",
                description="Update service guidelines and customer communication",
                priority="low",
                responsible_team="After-sales",
                status="pending"
            )
        ]
        return actions
    
    def _generate_analysis_summary(self, pattern: Dict[str, Any]) -> str:
        """Generate analysis summary"""
        return f"Analysis of {pattern.get('occurrence_count', 0)} occurrences of {pattern.get('failure_type', 'failure')} in {pattern.get('component', 'component')}. Pattern indicates systematic issue requiring manufacturing attention. Root cause analysis completed with identified contributing factors and recommended actions."
    
    def _estimate_impact(self, occurrence_count: int, severity: str) -> str:
        """Estimate impact"""
        if occurrence_count > 50:
            return "High impact - affects significant number of vehicles"
        elif occurrence_count > 20:
            return "Medium impact - affects multiple vehicles"
        else:
            return "Low impact - limited occurrences but requires monitoring"
    
    async def _get_failure_patterns(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get failure patterns"""
        db = get_database()
        manufacturer = input_data.get("manufacturer")
        
        query = {}
        if manufacturer:
            query["manufacturer"] = manufacturer
        
        patterns = await db.failure_patterns.find(query).sort("occurrence_count", -1).to_list(100)
        
        return {
            "status": "success",
            "patterns": patterns,
            "count": len(patterns)
        }
    
    async def _update_failure_patterns(self, vin: str, error_codes: List[str], component: str = None) -> None:
        """Update failure patterns from telemetry data"""
        db = get_database()
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin})
        if not vehicle:
            return
        
        manufacturer = vehicle.get("manufacturer")
        model = vehicle.get("model")
        
        # Update patterns for each error code
        for error_code in error_codes:
            pattern_key = f"{manufacturer}_{model}_{error_code}"
            
            # Determine failure type and component from error code
            failure_type = self._map_error_to_failure_type(error_code)
            component = component or self._map_error_to_component(error_code)
            
            # Update or create pattern
            await db.failure_patterns.update_one(
                {
                    "manufacturer": manufacturer,
                    "model": model,
                    "error_codes": error_code,
                    "component": component
                },
                {
                    "$setOnInsert": {
                        "pattern_id": f"PAT_{uuid.uuid4().hex[:8].upper()}",
                        "failure_type": failure_type,
                        "component": component,
                        "manufacturer": manufacturer,
                        "model": model,
                        "error_codes": [error_code],
                        "occurrence_count": 0,
                        "first_seen": datetime.utcnow(),
                        "severity": "medium",
                        "created_at": datetime.utcnow()
                    },
                    "$inc": {"occurrence_count": 1},
                    "$set": {
                        "last_seen": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
    
    def _map_error_to_failure_type(self, error_code: str) -> str:
        """Map error code to failure type"""
        mapping = {
            "P0217": "Engine Overheating",
            "P0521": "Oil Pressure Low",
            "P0300": "Engine Misfire",
            "P0420": "Catalyst Efficiency",
        }
        return mapping.get(error_code, "General Failure")
    
    def _map_error_to_component(self, error_code: str) -> str:
        """Map error code to component"""
        mapping = {
            "P0217": "Engine Cooling System",
            "P0521": "Engine Oil System",
            "P0300": "Engine Ignition System",
            "P0420": "Exhaust System",
        }
        return mapping.get(error_code, "Unknown Component")

