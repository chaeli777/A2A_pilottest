"""
A2A Agent Development Kit - Simple HTTP Client
단일 에이전트와 통신하는 간단한 클라이언트
"""
import httpx
from typing import Dict, Any, Optional, List


class A2AClient:
    """
    A2A 표준 HTTP 클라이언트
    
    단일 에이전트와 통신할 때 사용
    여러 에이전트를 관리하려면 A2ADiscoveryClient 사용
    
    Usage:
        # 단일 에이전트와 통신
        with A2AClient("http://localhost:9201") as client:
            # Agent Card 조회
            card = client.get_agent_card()
            print(card['skills'])
            
            # 스킬 실행 (JSON-RPC)
            result = client.execute_skill("research", query="AI")
    """
    
    def __init__(self, base_url: str, timeout: float = 120.0):
        """
        Args:
            base_url: 에이전트 서버 URL (예: "http://localhost:9201")
            timeout: 요청 타임아웃 (초). Gemini API 호출을 고려하여 기본값 120초
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=timeout)
        self._agent_card: Optional[Dict[str, Any]] = None
    
    def get_agent_card(self, refresh: bool = False) -> Dict[str, Any]:
        """
        Agent Card 가져오기 (A2A 표준: /.well-known/agent.json)
        
        Args:
            refresh: True면 캐시된 카드를 무시하고 새로 조회
        
        Returns:
            Agent Card 딕셔너리
        """
        if self._agent_card and not refresh:
            return self._agent_card
        
        response = self.client.get(f"{self.base_url}/.well-known/agent.json")
        response.raise_for_status()
        self._agent_card = response.json()
        return self._agent_card
    
    def list_skills(self) -> List[Dict[str, str]]:
        """
        에이전트의 스킬 목록 조회
        
        Returns:
            스킬 목록 [{"name": "...", "description": "..."}, ...]
        """
        card = self.get_agent_card()
        return card.get("skills", [])
    
    def has_skill(self, skill_name: str) -> bool:
        """
        특정 스킬을 가지고 있는지 확인
        
        Args:
            skill_name: 스킬 이름
        
        Returns:
            스킬 존재 여부
        """
        skills = self.list_skills()
        return any(s['name'] == skill_name for s in skills)
    
    def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        스킬 실행 (JSON-RPC 2.0)
        
        Args:
            skill_name: 실행할 스킬 이름
            **kwargs: 스킬 파라미터
        
        Returns:
            스킬 실행 결과
        
        Raises:
            Exception: RPC 에러 발생 시
        """
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
            error = result['error']
            raise Exception(f"RPC Error [{error.get('code')}]: {error.get('message')}")
        
        return result.get("result")
    
    def create_task(self, input_text: str = None, input_data: Dict[str, Any] = None, 
                    metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Task 생성 (A2A 표준 Task-based API)
        
        Args:
            input_text: 입력 텍스트
            input_data: 입력 데이터
            metadata: 메타데이터
        
        Returns:
            Task 생성 결과 {"taskId": "...", "status": "..."}
        """
        payload = {
            "input": {
                "text": input_text,
                "data": input_data
            }
        }
        if metadata:
            payload["metadata"] = metadata
        
        response = self.client.post(f"{self.base_url}/tasks", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Task 상태 조회
        
        Args:
            task_id: Task ID
        
        Returns:
            Task 정보
        """
        response = self.client.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """
        서버 상태 확인
        
        Returns:
            서버 상태 정보
        """
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """클라이언트 종료"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def __repr__(self):
        return f"<A2AClient(url='{self.base_url}')>"


__all__ = ['A2AClient']

