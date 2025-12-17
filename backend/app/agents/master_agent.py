from typing import Dict, Any, Optional
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.agents.telemetry_agent import TelemetryAgent
from app.agents.failure_prediction_agent import FailurePredictionAgent
from app.agents.customer_engagement_agent import CustomerEngagementAgent
from app.agents.smart_scheduling_agent import SmartSchedulingAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.manufacturing_insights_agent import ManufacturingInsightsAgent
from app.agents.ueba_security_agent import UEBASecurityAgent
from app.utils.logger import log_agent_action

class MasterAgent(BaseAgent):
    """Master Agent orchestrates all worker agents"""
    
    def __init__(self):
        super().__init__("MasterAgent")
        # Initialize worker agents
        self.telemetry_agent = TelemetryAgent()
        self.failure_prediction_agent = FailurePredictionAgent()
        self.customer_engagement_agent = CustomerEngagementAgent()
        self.smart_scheduling_agent = SmartSchedulingAgent()
        self.feedback_agent = FeedbackAgent()
        self.manufacturing_insights_agent = ManufacturingInsightsAgent()
        self.ueba_security_agent = UEBASecurityAgent()
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Master workflow orchestration
        Typical flow:
        1. Telemetry Agent - Ingest vehicle data
        2. Failure Prediction Agent - Predict failures
        3. If risk detected:
           - Customer Engagement Agent - Alert customer
           - Smart Scheduling Agent - Schedule service
        4. Feedback Agent - Track feedback
        5. Manufacturing Insights Agent - Generate insights
        6. UEBA Security Agent - Monitor security
        """
        workflow = input_data.get("workflow", "full_cycle")
        vin = input_data.get("vin")
        customer_id = input_data.get("customer_id")
        
        results = {
            "workflow": workflow,
            "timestamp": datetime.utcnow().isoformat(),
            "steps": []
        }
        
        try:
            if workflow == "full_cycle" or workflow == "monitor_and_predict":
                # Step 1: Collect telemetry
                telemetry_result = await self.telemetry_agent.execute({"vin": vin})
                results["steps"].append({"step": "telemetry", "result": telemetry_result})
                telemetry_data = telemetry_result.get("telemetry", {})
                vin = vin or telemetry_data.get("vin")
                
                # Step 2: Predict failures
                prediction_result = await self.failure_prediction_agent.execute({"vin": vin})
                results["steps"].append({"step": "failure_prediction", "result": prediction_result})
                risk_score = prediction_result.get("risk_score", 0.0)
                
                # Step 3: Engage customer if risk detected
                if risk_score > 0.3:
                    if customer_id:
                        engagement_result = await self.customer_engagement_agent.execute({
                            "action": "send_alert",
                            "vin": vin,
                            "customer_id": customer_id,
                            "risk_score": risk_score,
                            "message_type": "prediction_alert"
                        })
                        results["steps"].append({"step": "customer_engagement", "result": engagement_result})
                        
                        # Step 4: Schedule service if high risk
                        if risk_score > 0.5:
                            schedule_result = await self.smart_scheduling_agent.execute({
                                "action": "schedule",
                                "customer_id": customer_id,
                                "vin": vin,
                                "service_type": "predictive",
                                "priority": "high" if risk_score > 0.7 else "medium",
                                "risk_score": risk_score
                            })
                            results["steps"].append({"step": "smart_scheduling", "result": schedule_result})
                
                # Step 5: Update failure patterns for manufacturing
                if telemetry_data.get("error_codes"):
                    await self.manufacturing_insights_agent._update_failure_patterns(
                        vin, telemetry_data.get("error_codes", [])
                    )
            
            elif workflow == "collect_feedback":
                feedback_result = await self.feedback_agent.execute(input_data)
                results["steps"].append({"step": "feedback", "result": feedback_result})
            
            elif workflow == "generate_manufacturing_insights":
                insights_result = await self.manufacturing_insights_agent.execute({
                    "action": "generate_insights"
                })
                results["steps"].append({"step": "manufacturing_insights", "result": insights_result})
            
            elif workflow == "security_check":
                security_result = await self.ueba_security_agent.execute({
                    "action": "analyze_logs"
                })
                results["steps"].append({"step": "security", "result": security_result})
            
            results["status"] = "success"
            results["message"] = f"Workflow {workflow} completed successfully"
            
        except Exception as e:
            results["status"] = "error"
            results["message"] = str(e)
            results["error"] = str(e)
        
        return results
    
    async def process_service_feedback(
        self, 
        appointment_id: str,
        customer_id: str,
        vin: str,
        rating: int,
        comments: str
    ) -> Dict[str, Any]:
        """Process service feedback workflow"""
        result = await self._execute({
            "workflow": "collect_feedback",
            "action": "collect_feedback",
            "appointment_id": appointment_id,
            "customer_id": customer_id,
            "vin": vin,
            "rating": rating,
            "comments": comments,
            "service_satisfaction": "satisfied" if rating >= 4 else "neutral" if rating == 3 else "dissatisfied",
            "issues_resolved": rating >= 3
        })
        return result

