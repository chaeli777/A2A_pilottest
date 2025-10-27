"""
A2A Agent Development Kit - Agent Base Class
데코레이터 기반의 간편한 에이전트 개발
"""
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, field
import inspect


@dataclass
class AgentSkill:
    """에이전트 스킬 정의"""
    name: str
    description: str
    handler: Callable
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


def agent_skill(name: str, description: str, 
                input_schema: Optional[Dict] = None,
                output_schema: Optional[Dict] = None):
    """
    에이전트 스킬을 정의하는 데코레이터
    
    Usage:
        @agent_skill("research", "주제를 분석하고 요약합니다")
        def research(self, query: str) -> str:
            return "..."
    """
    def decorator(func: Callable) -> Callable:
        # 함수에 스킬 메타데이터 추가
        func._agent_skill = AgentSkill(
            name=name,
            description=description,
            handler=func,
            input_schema=input_schema,
            output_schema=output_schema
        )
        return func
    return decorator


class A2AAgent:
    """
    A2A Protocol Agent Base Class
    
    Usage:
        class MyAgent(A2AAgent):
            def __init__(self):
                super().__init__(
                    agent_id="my_agent",
                    name="My Custom Agent",
                    description="This is my agent"
                )
            
            @agent_skill("process", "데이터를 처리합니다")
            def process(self, data: str) -> str:
                return f"Processed: {data}"
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        version: str = "1.0",
        provider_name: str = "ADK Lab",
        provider_email: str = "lab@example.com"
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.version = version
        self.provider_name = provider_name
        self.provider_email = provider_email
        
        # 스킬 자동 수집
        self._skills: List[AgentSkill] = []
        self._collect_skills()
    
    def _collect_skills(self):
        """클래스에서 @agent_skill 데코레이터가 붙은 메서드 찾기"""
        for name in dir(self):
            if name.startswith('_'):
                continue
            
            attr = getattr(self, name)
            if hasattr(attr, '_agent_skill'):
                skill = attr._agent_skill
                # handler를 bound method로 업데이트
                skill.handler = attr
                self._skills.append(skill)
    
    def get_skills(self) -> List[AgentSkill]:
        """등록된 스킬 목록 반환"""
        return self._skills
    
    def get_skill(self, skill_name: str) -> Optional[AgentSkill]:
        """특정 스킬 찾기"""
        for skill in self._skills:
            if skill.name == skill_name:
                return skill
        return None
    
    def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        스킬 실행
        
        Args:
            skill_name: 실행할 스킬 이름
            **kwargs: 스킬에 전달할 파라미터
        
        Returns:
            스킬 실행 결과
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        return skill.handler(**kwargs)
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        A2A Agent Card 생성
        """
        skills_schema = []
        for skill in self._skills:
            skill_info = {
                "name": skill.name,
                "description": skill.description
            }
            if skill.input_schema:
                skill_info["inputSchema"] = skill.input_schema
            if skill.output_schema:
                skill_info["outputSchema"] = skill.output_schema
            skills_schema.append(skill_info)
        
        return {
            "protocolVersion": "1.0",
            "name": self.name,
            "description": self.description,
            "provider": {
                "name": self.provider_name,
                "contactEmail": self.provider_email
            },
            "version": self.version,
            "capabilities": {
                "streaming": False,
                "push": False
            },
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": skills_schema,
            "supportsAuthenticatedExtendedCard": False
        }
    
    def __repr__(self):
        skills_str = ', '.join([s.name for s in self._skills])
        return f"<{self.__class__.__name__}(id='{self.agent_id}', skills=[{skills_str}])>"

