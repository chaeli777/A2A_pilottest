"""
A2A Agent Development Kit - Simple HTTP Client
"""
import httpx
from typing import Dict, Any, Optional


class A2AClient:
    """간단한 A2A HTTP 클라이언트"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=30.0)
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Agent Card 가져오기"""
        response = self.client.get(f"{self.base_url}/.well-known/agent.json")
        response.raise_for_status()
        return response.json()
    
    def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """스킬 실행"""
        response = self.client.post(
            f"{self.base_url}/rpc",
            json={
                "jsonrpc": "2.0",
                "method": skill_name,
                "params": kwargs,
                "id": 1
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            raise Exception(f"RPC Error: {result['error']}")
        
        return result.get("result")
    
    def close(self):
        """클라이언트 종료"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


__all__ = ['A2AClient']

