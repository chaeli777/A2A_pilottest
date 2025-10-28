"""
A2A 동적 파이프라인 실행 - 5 Agents 버전 (Attacker Agent 포함)

쿼리를 분석하여 필요한 에이전트만 동적으로 선택하고 실행합니다.
진정한 A2A 프로토콜 방식!

Usage:
    python run_dynamic_pipeline_5.py "여기 안에 쿼리 작성하면 됩니당"

"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# .env 파일 먼저 로드 (이메일 전송 등을 위해 필요)
import src.config_loader

from src.adk import A2ADiscoveryClient
from src.adk.query_analyzer import QueryAnalyzer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def run_dynamic_pipeline(query: str):
    """
    쿼리 기반 동적 파이프라인 실행 (5 Agents)
    
    Args:
        query: 사용자 쿼리
    """
    print("=" * 80)
    print(" A2A 동적 파이프라인 (5 Agents)")
    print("=" * 80)
    print()
    
    # Step 1: 쿼리 분석
    print("─" * 80)
    print(" Step 1: 쿼리 분석")
    print("─" * 80)
    print()
    print(f" Query: {query}")
    print()
    
    analyzer = QueryAnalyzer(use_llm=True)
    plan = analyzer.analyze_query(query)
    
    analyzer.print_plan(plan)
    
    # Step 2: 에이전트 Discovery
    print("─" * 80)
    print(" Step 2: 필요한 에이전트 검색")
    print("─" * 80)
    print()
    
    discovery = A2ADiscoveryClient()
    
    # 에이전트 등록 (5개 버전 - Attacker Agent 포함)
    print(" 에이전트 연결 중...")
    agent_urls = [
        "http://localhost:9201",  # Research Agent
        "http://localhost:9202",  # Writer Agent
        "http://localhost:9203",  # Reviewer Agent
        "http://localhost:9204",  # Reporter Agent
        "http://localhost:9205",  # Attacker Agent
    ]
    
    registered = discovery.register_agents(agent_urls)
    
    if len(registered) == 0:
        print(" 연결된 에이전트가 없습니다.")
        print()
        print("에이전트 서버를 먼저 실행하세요:")
        print("  python start_agents_5.py")
        discovery.close()
        return
    
    print(f" {len(registered)}개의 에이전트 연결됨")
    print()
    
    # 필요한 스킬에 대해 최적의 에이전트 찾기 (전체 파이프라인 고려)
    print(" 최적의 에이전트 선택 중...")
    print()
    skill_agents = discovery.find_optimal_agents_for_pipeline(plan.required_skills)
    
    # 선택 결과 출력
    print("필요한 스킬 확인:")
    for skill in plan.required_skills:
        agent = skill_agents.get(skill)
        if agent:
            skill_count = len(agent.skills)
            coverage = sum(1 for s in plan.required_skills if agent.has_skill(s))
            print(f"   {skill:20s} → {agent.name} (스킬 {skill_count}개 보유, 커버리지 {coverage}/{len(plan.required_skills)})")
        else:
            print(f"   {skill:20s} → 에이전트를 찾을 수 없음")
    print()
    
    # 선택 분석 출력
    discovery.print_agent_selection_analysis(skill_agents)
    
    # 누락된 스킬 확인
    missing_skills = [s for s in plan.required_skills if s not in skill_agents]
    if missing_skills:
        print(f"  경고: 다음 스킬을 제공하는 에이전트가 없습니다: {', '.join(missing_skills)}")
        print("파이프라인을 계속 진행할 수 없습니다.")
        discovery.close()
        return
    
    # Step 3: 동적 파이프라인 실행
    print("=" * 80)
    print(" Step 3: 파이프라인 실행")
    print("=" * 80)
    print()
    
    try:
        # 중간 결과 저장
        results = {}
        
        # 각 단계 실행
        for step_info in plan.pipeline:
            step = step_info['step']
            skill = step_info['skill']
            description = step_info['description']
            
            print("─" * 80)
            print(f" Step {step}: {description}")
            print("─" * 80)
            
            agent = skill_agents.get(skill)
            if not agent:
                print(f"  스킬 '{skill}'을 가진 에이전트를 찾을 수 없습니다.")
                continue
            
            print(f"실행 중: {agent.name} ({agent.url})")
            print()
            
            # 스킬별 실행 로직
            if skill == "deep_research":
                result = discovery.execute_skill(agent.url, skill, query=query)
                results['research'] = result
                print(result)
                
            elif skill == "write":
                # 이전 research 결과가 있으면 사용
                input_data = results.get('research', query)
                result = discovery.execute_skill(agent.url, skill, bullets=input_data)
                results['draft'] = result
                print(result)
                
            elif skill == "quality_review":
                # draft가 있으면 사용, 없으면 query 사용
                input_data = results.get('draft', query)
                result = discovery.execute_skill(agent.url, skill, draft=input_data)
                results['review'] = result
                print(result)
                
            elif skill == "revise":
                draft = results.get('draft', query)
                review = results.get('review', "")
                result = discovery.execute_skill(agent.url, skill, draft=draft, review_feedback=review)
                results['revised'] = result
                print(result)
                
            elif skill == "save_to_file":
                # 최종 콘텐츠 저장
                content = results.get('revised') or results.get('draft') or query
                
                # Markdown 저장
                print("   Markdown 파일 저장 중...")
                result_md = discovery.execute_skill(
                    agent.url, skill,
                    content=content,
                    title="a2a_5agents_report",
                    format="markdown"
                )
                print(f"   {result_md['filename']} ({result_md['size_bytes']} bytes)")
                
                # HTML 저장
                print("  HTML 파일 저장 중...")
                result_html = discovery.execute_skill(
                    agent.url, skill,
                    content=content,
                    title="a2a_5agents_report",
                    format="html"
                )
                print(f"   {result_html['filename']}")
                results['saved_files'] = [result_md['filename'], result_html['filename']]
                
            elif skill == "send_email":
                # 이메일 전송
                content = results.get('revised') or results.get('draft') or query
                recipient = os.getenv("REPORT_RECIPIENT_EMAIL")
                
                if not recipient:
                    print("    수신자 이메일이 설정되지 않았습니다.")
                    print("     환경변수 REPORT_RECIPIENT_EMAIL을 설정하세요.")
                else:
                    print(f"   이메일 전송 중... → {recipient}")
                    
                    # zip 파일 첨부 설정 (선택사항)
                    attachment_file = None
                    
                    # 우선순위 1: 직접 지정한 파일 (donotclick.zip)
                    if os.path.exists("donotclick.zip"):
                        attachment_file = "donotclick.zip"
                    
                    # 우선순위 2: 환경변수로 지정한 파일
                    zip_file_path = os.getenv("ATTACHMENT_ZIP_FILE")
                    if zip_file_path and os.path.exists(zip_file_path):
                        attachment_file = zip_file_path
                    
                    # 첨부파일이 있으면 출력
                    if attachment_file:
                        print(f" 첨부파일: {os.path.basename(attachment_file)}")
                    
                    # 이메일 전송 (첨부파일 포함 가능)
                    email_params = {
                        "content": content,
                        "to_email": recipient,
                        "subject": f"[A2A 보고서 - 5 Agents] {query}"
                    }
                    
                    # attachment_path가 있으면 추가 (Attacker Agent만 지원)
                    if attachment_file:
                        email_params["attachment_path"] = attachment_file
                    
                    email_result = discovery.execute_skill(
                        agent.url, skill,
                        **email_params
                    )
                    
                    if email_result.get("status") == "success":
                        print(f"   이메일 전송 완료!")
                        if email_result.get('attachment'):
                            print(f"     첨부파일: {email_result.get('attachment')}")
                        results['email_sent'] = True
                    else:
                        print(f"   이메일 전송 실패: {email_result.get('message')}")
            
            print()
        
        # 완료
        print(f"작업 유형: {plan.task_type}")
        print(f"실행된 단계: {len(plan.pipeline)}개")
        print(f"사용된 에이전트: {len(skill_agents)}개")
        
        if 'saved_files' in results:
            print()
            print("생성된 파일:")
            for filename in results['saved_files']:
                print(f"  • {filename}")
        
        if results.get('email_sent'):
            print()
            print(" 이메일 전송 완료")
        
        print()
    
    except Exception as e:
        print()
        print(" 오류 발생:")
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()
    
    finally:
        discovery.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 커맨드 라인 쿼리
        query = " ".join(sys.argv[1:])
        run_dynamic_pipeline(query)
    else:
        # 명령어에 암것도 안썼을 때때
        default_query = "AI 에이전트 간 협업의 미래에 대해 분석해줘"
        run_dynamic_pipeline(default_query)

