from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from app.utils.logger import log_agent_action

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic with logging"""
        start_time = time.time()
        status = "success"
        error_message = None
        output_data = {}
        
        try:
            output_data = await self._execute(input_data)
        except Exception as e:
            status = "error"
            error_message = str(e)
            output_data = {"error": str(e)}
            raise
        
        finally:
            execution_time_ms = (time.time() - start_time) * 1000
            await log_agent_action(
                agent_name=self.agent_name,
                action=self.__class__.__name__,
                input_data=input_data,
                output_data=output_data,
                execution_time_ms=execution_time_ms,
                status=status,
                error_message=error_message
            )
        
        return output_data
    
    @abstractmethod
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-specific execution logic"""
        pass

