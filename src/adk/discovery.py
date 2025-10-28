"""
A2A Agent Discovery Client
여러 에이전트의 Agent Card를 조회하고, 쿼리에 적합한 에이전트를 선택
"""
import httpx
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AgentInfo:
    """에이전트 정보"""
    url: str
    name: str
    description: str
    skills: List[Dict[str, str]]
    agent_card: Dict[str, Any]
    
    def has_skill(self, skill_name: str) -> bool:
        """특정 스킬을 가지고 있는지 확인"""
        return any(s['name'] == skill_name for s in self.skills)
    
    def skill_names(self) -> List[str]:
        """스킬 이름 목록"""
        return [s['name'] for s in self.skills]


class A2ADiscoveryClient:
    """
    A2A Agent Discovery Client
    
    여러 에이전트를 관리하고, 쿼리에 적합한 에이전트를 찾아주는 클라이언트
    
    Usage:
        discovery = A2ADiscoveryClient()
        
        # 에이전트 등록
        discovery.register_agent("http://localhost:9201")
        discovery.register_agent("http://localhost:9202")
        
        # 특정 스킬을 가진 에이전트 찾기
        agent = discovery.find_agent_by_skill("research")
        
        # 스킬 실행
        result = discovery.execute_skill(agent.url, "research", query="AI")
    """
    
    def __init__(self, timeout: float = 120.0):
        """
        Args:
            timeout: HTTP 요청 타임아웃 (초). Gemini API 호출을 고려하여 기본값 120초
        """
        self.client = httpx.Client(timeout=timeout)
        self.agents: Dict[str, AgentInfo] = {}  # url -> AgentInfo
    
    def register_agent(self, agent_url: str) -> Optional[AgentInfo]:
        """
        에이전트를 등록하고 Agent Card를 조회
        
        Args:
            agent_url: 에이전트 서버 URL (예: "http://localhost:9201")
        
        Returns:
            등록된 AgentInfo 또는 None (실패 시)
        """
        agent_url = agent_url.rstrip('/')
        
        try:
            # Agent Card 조회 (A2A 표준)
            response = self.client.get(f"{agent_url}/.well-known/agent.json")
            response.raise_for_status()
            agent_card = response.json()
            
            # AgentInfo 생성
            agent_info = AgentInfo(
                url=agent_url,
                name=agent_card.get("name", "Unknown Agent"),
                description=agent_card.get("description", ""),
                skills=agent_card.get("skills", []),
                agent_card=agent_card
            )
            
            self.agents[agent_url] = agent_info
            return agent_info
            
        except Exception as e:
            print(f" Failed to register agent {agent_url}: {e}")
            return None
    
    def register_agents(self, agent_urls: List[str]) -> List[AgentInfo]:
        """
        여러 에이전트를 한 번에 등록
        
        Args:
            agent_urls: 에이전트 URL 목록
        
        Returns:
            성공적으로 등록된 AgentInfo 목록
        """
        registered = []
        for url in agent_urls:
            agent_info = self.register_agent(url)
            if agent_info:
                registered.append(agent_info)
        return registered
    
    def list_agents(self) -> List[AgentInfo]:
        """등록된 모든 에이전트 목록"""
        return list(self.agents.values())
    
    def find_agent_by_skill(self, skill_name: str, required_skills: List[str] = None) -> Optional[AgentInfo]:
        """
        특정 스킬을 가진 최적의 에이전트 찾기
        
        최적 선택 기준:
        1. 필요한 스킬(required_skills)을 가장 많이 커버하는 에이전트
        2. 동일한 커버리지면 전문 에이전트(스킬 수가 적은) 우선
        3. 그래도 동일하면 첫 번째 에이전트
        
        Args:
            skill_name: 찾고자 하는 스킬 이름
            required_skills: 전체 파이프라인에서 필요한 스킬 목록 (최적화 힌트)
        
        Returns:
            AgentInfo 또는 None
        """
        candidates = [agent for agent in self.agents.values() if agent.has_skill(skill_name)]
        
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        # 여러 후보가 있을 때 최적의 에이전트 선택
        return self._select_best_agent(candidates, required_skills or [skill_name])
    
    def _select_best_agent(self, candidates: List[AgentInfo], required_skills: List[str]) -> AgentInfo:
        """
        후보 에이전트 중 최적의 에이전트 선택
        
        선택 기준:
        1. 필요한 스킬을 가장 많이 커버
        2. 동일하면 전문 에이전트(스킬 수가 적은) 우선
        3. 그래도 동일하면 첫 번째
        
        Args:
            candidates: 후보 에이전트 목록
            required_skills: 필요한 스킬 목록
        
        Returns:
            선택된 AgentInfo
        """
        def score_agent(agent: AgentInfo) -> tuple:
            # 필요한 스킬 중 몇 개를 커버하는가
            coverage = sum(1 for skill in required_skills if agent.has_skill(skill))
            
            # 전체 스킬 수 (적을수록 전문적)
            total_skills = len(agent.skills)
            
            # 정렬 기준: (커버리지 높을수록, 스킬 수 적을수록) = 더 좋음
            # coverage는 음수로 하여 내림차순, total_skills는 양수로 오름차순
            return (-coverage, total_skills)
        
        # 점수가 가장 좋은 에이전트 선택
        best_agent = min(candidates, key=score_agent)
        
        return best_agent
    
    def find_agents_by_skill(self, skill_name: str) -> List[AgentInfo]:
        """
        특정 스킬을 가진 모든 에이전트 찾기
        
        Args:
            skill_name: 찾고자 하는 스킬 이름
        
        Returns:
            AgentInfo 목록
        """
        return [agent for agent in self.agents.values() if agent.has_skill(skill_name)]
    
    def find_agent_by_skills(self, skill_names: List[str], match_all: bool = False) -> Optional[AgentInfo]:
        """
        여러 스킬을 기준으로 에이전트 찾기
        
        Args:
            skill_names: 찾고자 하는 스킬 이름 목록
            match_all: True면 모든 스킬을 가진 에이전트, False면 하나라도 가진 에이전트
        
        Returns:
            AgentInfo 또는 None
        """
        for agent in self.agents.values():
            if match_all:
                # 모든 스킬을 가지고 있어야 함
                if all(agent.has_skill(skill) for skill in skill_names):
                    return agent
            else:
                # 하나라도 가지고 있으면 됨
                if any(agent.has_skill(skill) for skill in skill_names):
                    return agent
        return None
    
    def find_agent_by_description(self, keywords: List[str]) -> Optional[AgentInfo]:
        """
        설명에서 키워드로 에이전트 찾기
        
        Args:
            keywords: 검색할 키워드 목록
        
        Returns:
            AgentInfo 또는 None
        """
        for agent in self.agents.values():
            description_lower = agent.description.lower()
            if any(keyword.lower() in description_lower for keyword in keywords):
                return agent
        return None
    
    def find_optimal_agents_for_pipeline(self, required_skills: List[str]) -> Dict[str, AgentInfo]:
        """
        파이프라인 전체에 필요한 스킬에 대해 최적의 에이전트 매핑 생성
        
        각 스킬에 대해 전체 필요 스킬 목록을 고려하여 최적의 에이전트를 선택합니다.
        이를 통해 가능한 경우 하나의 에이전트가 여러 스킬을 처리하도록 최적화합니다.
        
        Args:
            required_skills: 필요한 스킬 목록
        
        Returns:
            스킬 → 에이전트 매핑 딕셔너리
        
        Example:
            >>> required_skills = ["deep_research", "write", "send_email"]
            >>> mapping = discovery.find_optimal_agents_for_pipeline(required_skills)
            >>> # Attacker Agent가 모든 스킬을 가지고 있으면:
            >>> # {"deep_research": AttackerAgent, "write": AttackerAgent, "send_email": AttackerAgent}
        """
        skill_agent_map = {}
        
        for skill in required_skills:
            agent = self.find_agent_by_skill(skill, required_skills)
            if agent:
                skill_agent_map[skill] = agent
        
        return skill_agent_map
    
    def print_agent_selection_analysis(self, skill_agent_map: Dict[str, AgentInfo]):
        """에이전트 선택 결과 분석 출력"""
        print("=" * 80)
        print(" 에이전트 선택 분석")
        print("=" * 80)
        print()
        
        # 각 에이전트가 담당하는 스킬 그룹화
        agent_skills = {}
        for skill, agent in skill_agent_map.items():
            agent_name = agent.name
            if agent_name not in agent_skills:
                agent_skills[agent_name] = []
            agent_skills[agent_name].append(skill)
        
        print(f"총 {len(skill_agent_map)}개 스킬 → {len(agent_skills)}개 에이전트 사용")
        print()
        
        for agent_name, skills in agent_skills.items():
            print(f" {agent_name}")
            print(f"   담당 스킬 ({len(skills)}개): {', '.join(skills)}")
        print()
    
    def execute_skill(self, agent_url: str, skill_name: str, **kwargs) -> Any:
        """
        특정 에이전트의 스킬 실행 (JSON-RPC)
        
        Args:
            agent_url: 에이전트 URL
            skill_name: 스킬 이름
            **kwargs: 스킬 파라미터
        
        Returns:
            스킬 실행 결과
        """
        agent_url = agent_url.rstrip('/')
        
        response = self.client.post(
            f"{agent_url}/rpc",
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
    
    def smart_execute(self, skill_name: str, **kwargs) -> Any:
        """
        스킬 이름으로 자동으로 적합한 에이전트를 찾아서 실행
        
        Args:
            skill_name: 스킬 이름
            **kwargs: 스킬 파라미터
        
        Returns:
            스킬 실행 결과
        
        Raises:
            ValueError: 스킬을 가진 에이전트가 없을 때
        """
        agent = self.find_agent_by_skill(skill_name)
        if not agent:
            raise ValueError(f"No agent found with skill '{skill_name}'")
        
        return self.execute_skill(agent.url, skill_name, **kwargs)
    
    def print_agent_registry(self):
        """등록된 에이전트 목록을 보기 좋게 출력"""
        print("=" * 80)
        print(f"📋 Registered Agents ({len(self.agents)})")
        print("=" * 80)
        print()
        
        if not self.agents:
            print("  No agents registered.")
            return
        
        for i, agent in enumerate(self.agents.values(), 1):
            print(f"{i}. {agent.name}")
            print(f"   URL: {agent.url}")
            print(f"   Description: {agent.description}")
            print(f"   Skills: {', '.join(agent.skill_names())}")
            print()
    
    def close(self):
        """클라이언트 종료"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


__all__ = ['A2ADiscoveryClient', 'AgentInfo']

