"""
외부 에이전트(제3자)가 A, B, C의 Agent Card를 보고
3가지 스킬을 모두 가진 통합 에이전트 만들기

A Agent: skill "research" (주제 분석)
B Agent: skill "write" (글 작성)  
C Agent: skill "review" (검토)

→ External Agent: skills ["research", "write", "review"] 모두 포함!
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.adk import A2AAgent, agent_skill, A2AServer
from src.llm_unified import generate

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class ExternalCombinedAgent(A2AAgent):
    """
    외부 에이전트 (제3자)
    
    A, B, C 에이전트의 Agent Card를 확인하고,
    3가지 스킬을 모두 구현한 통합 에이전트
    """
    
    def __init__(self):
        super().__init__(
            agent_id="external_combined",
            name="External Combined Agent",
            description="A, B, C 에이전트의 스킬을 모두 통합한 외부 에이전트",
            provider_name="Third-Party Company",
            provider_email="external@example.com"
        )
    
    # ====================================
    # Skill 1: Research (A Agent에서 가져옴)
    # ============================================
    @agent_skill("research", "주제를 분석하고 핵심 포인트 추출")
    def research(self, query: str) -> str:
        """
        A Agent의 Agent Card를 보고 구현:
        {
          "name": "research",
          "description": "Gemini로 주제 분석"
        }
        """
        system = """You are an expert AI researcher.
Analyze the topic and provide 4-5 key bullet points in Korean."""
        
        user = f"주제: {query}\n\n핵심 포인트를 bullet으로 분석하세요."
        
        return generate(system, user)
    
    # ============================================
    # Skill 2: Write (B Agent에서 가져옴)
    # ============================================
    @agent_skill("write", "Bullet을 자연스러운 문단으로 작성")
    def write(self, bullets: str) -> str:
        """
        B Agent의 Agent Card를 보고 구현:
        {
          "name": "write",
          "description": "Gemini로 글 작성"
        }
        """
        system = """You are a professional Korean technical writer.
Transform bullet points into well-structured paragraphs."""
        
        user = f"다음 bullet을 2-3개 문단으로 작성하세요:\n\n{bullets}"
        
        return generate(system, user)
    
    # ============================================
    # Skill 3: Review (C Agent에서 가져옴)
    # ============================================
    @agent_skill("review", "초안을 검토하고 개선안 제시")
    def review(self, draft: str) -> str:
        """
        C Agent의 Agent Card를 보고 구현:
        {
          "name": "review",
          "description": "Gemini로 검토"
        }
        """
        system = """You are an expert content reviewer.
Provide 3-5 specific improvements in Korean."""
        
        user = f"다음 초안을 검토하고 개선안을 제시하세요:\n\n{draft}"
        
        return generate(system, user)
    
    # ============================================
    # 추가 스킬: 전체 파이프라인 통합
    # ============================================
    @agent_skill("full_pipeline", "Research → Write → Review 전체 프로세스")
    def full_pipeline(self, query: str) -> dict:
        """
        외부 에이전트만의 추가 스킬:
        3가지 스킬을 순차적으로 실행하는 통합 파이프라인
        """
        print(f"📝 Query: {query}")
        print()
        
        # Step 1: Research
        print("🔬 Step 1: Research")
        bullets = self.research(query)
        print(bullets)
        print()
        
        # Step 2: Write
        print("✍️  Step 2: Write")
        draft = self.write(bullets)
        print(draft)
        print()
        
        # Step 3: Review
        print("🔍 Step 3: Review")
        review_result = self.review(draft)
        print(review_result)
        print()
        
        return {
            "query": query,
            "research": bullets,
            "draft": draft,
            "review": review_result
        }


# ============================================
# Demo: Agent Card 확인 및 실행
# ============================================

def demo_agent_card():
    """외부 에이전트의 Agent Card 확인"""
    import json
    
    print("=" * 80)
    print("📋 External Combined Agent - Agent Card")
    print("=" * 80)
    print()
    
    agent = ExternalCombinedAgent()
    card = agent.get_agent_card()
    
    print(json.dumps(card, indent=2, ensure_ascii=False))
    print()
    
    print("=" * 80)
    print("✅ 확인 사항:")
    print("=" * 80)
    print()
    print("1. ✅ A Agent의 'research' 스킬 포함")
    print("2. ✅ B Agent의 'write' 스킬 포함")
    print("3. ✅ C Agent의 'review' 스킬 포함")
    print("4. ⭐ 추가로 'full_pipeline' 스킬도 포함 (통합 실행)")
    print()
    print(f"총 스킬 개수: {len(card['skills'])}개")
    print(f"스킬 목록: {[s['name'] for s in card['skills']]}")
    print()


def demo_individual_skills():
    """각 스킬을 개별적으로 실행"""
    print("=" * 80)
    print("🧪 개별 스킬 테스트")
    print("=" * 80)
    print()
    
    agent = ExternalCombinedAgent()
    query = "Google A2A 프로토콜의 핵심"
    
    # Skill 1: Research
    print("1️⃣ Skill: research")
    print("-" * 80)
    bullets = agent.execute_skill("research", query=query)
    print(bullets)
    print()
    
    # Skill 2: Write
    print("2️⃣ Skill: write")
    print("-" * 80)
    draft = agent.execute_skill("write", bullets=bullets)
    print(draft)
    print()
    
    # Skill 3: Review
    print("3️⃣ Skill: review")
    print("-" * 80)
    review = agent.execute_skill("review", draft=draft)
    print(review)
    print()


def demo_full_pipeline():
    """통합 파이프라인 실행"""
    print("=" * 80)
    print("🚀 Full Pipeline 실행 (통합 스킬)")
    print("=" * 80)
    print()
    
    agent = ExternalCombinedAgent()
    result = agent.execute_skill(
        "full_pipeline",
        query="멀티 에이전트 시스템의 미래"
    )
    
    print("=" * 80)
    print("✅ 완료!")
    print("=" * 80)


def start_server(port=9100):
    """외부 에이전트를 HTTP 서버로 실행"""
    agent = ExternalCombinedAgent()
    server = A2AServer(agent, port=port)
    server.run()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "card":
            demo_agent_card()
        elif mode == "individual":
            demo_individual_skills()
        elif mode == "pipeline":
            demo_full_pipeline()
        elif mode == "server":
            start_server()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python external_combined_agent.py [card|individual|pipeline|server]")
    else:
        # 기본: Agent Card 확인
        demo_agent_card()
        print()
        
        # 통합 파이프라인 데모
        demo_full_pipeline()

