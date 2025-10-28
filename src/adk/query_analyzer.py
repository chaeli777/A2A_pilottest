"""
A2A Query Analyzer
쿼리를 분석하여 필요한 에이전트와 스킬을 동적으로 결정
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class TaskPlan:
    """작업 계획"""
    task_type: str  # "research", "review", "write", "summarize", "report", etc.
    required_skills: List[str]  # 필요한 스킬 목록
    pipeline: List[Dict[str, Any]]  # 실행할 파이프라인 단계
    description: str  # 계획 설명


class QueryAnalyzer:
    """
    쿼리를 분석하여 필요한 에이전트와 실행 계획을 결정
    
    A2A 표준에 맞게 동적으로 에이전트를 선택합니다.
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Args:
            use_llm: LLM을 사용한 고급 분석 여부 (False면 키워드 기반)
        """
        self.use_llm = use_llm
    
    def analyze_query(self, query: str) -> TaskPlan:
        """
        쿼리를 분석하여 작업 계획 생성
        
        Args:
            query: 사용자 쿼리
        
        Returns:
            TaskPlan: 실행 계획
        """
        if self.use_llm:
            return self._analyze_with_llm(query)
        else:
            return self._analyze_with_keywords(query)
    
    def _analyze_with_llm(self, query: str) -> TaskPlan:
        """LLM을 사용한 고급 쿼리 분석"""
        try:
            from src.llm_gemini import generate
            
            system = """You are an AI task analyzer for an Agent-to-Agent (A2A) system.

Analyze the user query and determine what tasks need to be performed.

Available agent skills:
- deep_research: Research and analyze topics in depth
- write: Write articles, documents, or content
- revise: Revise and improve existing text
- quality_review: Review content quality and provide feedback
- save_to_file: Save results to files (markdown/html)
- send_email: Send results via email

Respond ONLY with a JSON object (no markdown, no explanation):
{
  "task_type": "research_and_write|review_only|write_only|full_pipeline|custom",
  "required_skills": ["skill1", "skill2"],
  "pipeline": [
    {"step": 1, "skill": "deep_research", "description": "Research the topic"},
    {"step": 2, "skill": "write", "description": "Write content"}
  ],
  "description": "Brief description of the plan"
}

Examples:
- "양자컴퓨팅 분석해줘" → research + write
- "이 글 검토해줘" → quality_review only
- "보고서 작성 후 이메일 보내" → research + write + send_email
- "요약해줘" → write only
"""
            
            user = f"Query: {query}\n\nProvide the task analysis in JSON format."
            
            response = generate(system, user)
            
            # JSON 파싱
            import json
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            plan_data = json.loads(response)
            
            return TaskPlan(
                task_type=plan_data["task_type"],
                required_skills=plan_data["required_skills"],
                pipeline=plan_data["pipeline"],
                description=plan_data["description"]
            )
        
        except Exception as e:
            print(f"⚠️  LLM 분석 실패, 키워드 기반으로 전환: {e}")
            return self._analyze_with_keywords(query)
    
    def _analyze_with_keywords(self, query: str) -> TaskPlan:
        """키워드 기반 쿼리 분석 (fallback)"""
        query_lower = query.lower()
        
        # 검토만 필요한 경우
        if any(kw in query_lower for kw in ["검토", "리뷰", "review", "피드백", "평가"]):
            return TaskPlan(
                task_type="review_only",
                required_skills=["quality_review"],
                pipeline=[
                    {"step": 1, "skill": "quality_review", "description": "콘텐츠 품질 검토"}
                ],
                description="콘텐츠 검토 작업"
            )
        
        # 요약/작성만 필요한 경우
        if any(kw in query_lower for kw in ["요약", "작성", "써줘", "write"]) and \
           not any(kw in query_lower for kw in ["분석", "조사", "research"]):
            return TaskPlan(
                task_type="write_only",
                required_skills=["write"],
                pipeline=[
                    {"step": 1, "skill": "write", "description": "콘텐츠 작성"}
                ],
                description="콘텐츠 작성 작업"
            )
        
        # 이메일 전송이 포함된 경우
        has_email = any(kw in query_lower for kw in ["이메일", "메일", "email", "보내"])
        has_file = any(kw in query_lower for kw in ["저장", "파일", "save"])
        
        # 리서치 + 작성
        if any(kw in query_lower for kw in ["분석", "조사", "연구", "research", "알아봐"]):
            pipeline = [
                {"step": 1, "skill": "deep_research", "description": "주제 심층 조사"},
                {"step": 2, "skill": "write", "description": "콘텐츠 작성"}
            ]
            skills = ["deep_research", "write"]
            
            if has_email:
                pipeline.append({"step": 3, "skill": "send_email", "description": "이메일 전송"})
                skills.append("send_email")
            elif has_file:
                pipeline.append({"step": 3, "skill": "save_to_file", "description": "파일 저장"})
                skills.append("save_to_file")
            
            return TaskPlan(
                task_type="research_and_write",
                required_skills=skills,
                pipeline=pipeline,
                description="리서치 및 작성 작업"
            )
        
        # 기본: 전체 파이프라인
        return TaskPlan(
            task_type="full_pipeline",
            required_skills=["deep_research", "write", "quality_review", "revise", "save_to_file"],
            pipeline=[
                {"step": 1, "skill": "deep_research", "description": "주제 심층 조사"},
                {"step": 2, "skill": "write", "description": "초안 작성"},
                {"step": 3, "skill": "quality_review", "description": "품질 검토"},
                {"step": 4, "skill": "revise", "description": "피드백 반영 수정"},
                {"step": 5, "skill": "save_to_file", "description": "파일 저장"}
            ],
            description="전체 파이프라인 실행"
        )
    
    def print_plan(self, plan: TaskPlan):
        """작업 계획을 보기 좋게 출력"""
        print("=" * 80)
        print("📋 작업 계획 (Task Plan)")
        print("=" * 80)
        print()
        print(f"작업 유형: {plan.task_type}")
        print(f"설명: {plan.description}")
        print(f"필요한 스킬: {', '.join(plan.required_skills)}")
        print()
        print("실행 단계:")
        for step_info in plan.pipeline:
            print(f"  {step_info['step']}. {step_info['skill']}: {step_info['description']}")
        print()


__all__ = ['QueryAnalyzer', 'TaskPlan']

