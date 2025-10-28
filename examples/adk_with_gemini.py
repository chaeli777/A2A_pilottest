"""
Google Gemini를 사용한 실제 LLM 기반 에이전트
진짜 AI 협업!
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# .env 파일 먼저 로드
import src.config_loader

from src.adk import A2AAgent, agent_skill, A2AServer
from src.llm_gemini import generate  # Gemini만 직접 사용

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class GeminiResearchAgent(A2AAgent):
    """Google Gemini 기반 Research Agent - 정보 수집 및 분석 전문"""
    
    def __init__(self):
        super().__init__(
            agent_id="gemini_research",
            name="Gemini Research Agent",
            description="주제에 대한 심층 조사, 다각도 분석, 참고자료 제시를 수행하는 리서치 전문 에이전트"
        )
    
    @agent_skill("deep_research", "주제에 대한 심층 조사 및 다각도 분석")
    def research(self, query: str) -> str:
        system = """You are an expert AI researcher specializing in information gathering and analysis.

Your role:
1. **Information Collection**: Gather relevant facts, concepts, and data
2. **Multi-perspective Analysis**: Examine the topic from various angles
3. **Reference & Sources**: Suggest key references or areas to explore
4. **Fact-based Insights**: Provide objective, data-driven insights

Output format (in Korean):
-  핵심 개념 및 정의 (2-3개 bullet points)
-  다각도 분석 
-  참고할 만한 키워드나 분야
-  주요 트렌드 또는 최신 동향"""
        
        user = f"주제: {query}\n\n위 형식으로 심층 리서치를 수행해주세요."
        
        return generate(system, user)


class GeminiWriterAgent(A2AAgent):
    """Google Gemini 기반 Writer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="gemini_writer",
            name="Gemini Writer Agent",
            description="Google Gemini를 사용한 작가 에이전트"
        )
    
    @agent_skill("write", "Gemini로 글 작성")
    def write(self, bullets: str) -> str:
        system = """You are a professional Korean technical writer.
Transform bullet points into engaging, well-structured paragraphs.
Make it clear, informative, and reader-friendly."""
        
        user = f"다음 bullet을 2-3개의 자연스러운 문단으로 작성하세요:\n\n{bullets}"
        
        return generate(system, user)
    
    @agent_skill("revise", "검토 피드백을 반영하여 초안 수정")
    def revise(self, draft: str, review_feedback: str) -> str:
        system = """You are a professional Korean technical writer who excels at revising content based on feedback.

Your role:
1. **Carefully read** the original draft and the reviewer's feedback
2. **Address all issues** pointed out in the feedback
3. **Implement improvements** suggested by the reviewer
4. **Maintain the original structure** while enhancing quality
5. **Produce a polished final version** that incorporates all suggestions

Output: The revised text in Korean, improved based on the feedback."""
        
        user = f"""다음은 초안과 검토 피드백입니다. 피드백을 반영하여 개선된 버전을 작성해주세요.

【초안】
{draft}

【검토 피드백】
{review_feedback}

위 피드백의 모든 개선 제안을 반영하여 수정된 글을 작성하세요."""
        
        return generate(system, user)


class GeminiReviewerAgent(A2AAgent):
    """Google Gemini 기반 Reviewer Agent - 품질 평가 및 개선 제안 전문"""
    
    def __init__(self):
        super().__init__(
            agent_id="gemini_reviewer",
            name="Gemini Reviewer Agent",
            description="콘텐츠 품질 평가, 오류 발견, 구조 분석 및 구체적 개선안 제시를 수행하는 검토 전문 에이전트"
        )
    
    @agent_skill("quality_review", "콘텐츠 품질 평가 및 구체적 개선안 제시")
    def review(self, draft: str) -> str:
        system = """You are an expert content reviewer and quality assurance specialist.

Your role:
1. **Quality Assessment**: Evaluate accuracy, clarity, completeness, and logic
2. **Error Detection**: Identify factual errors, inconsistencies, or gaps
3. **Structure Analysis**: Review organization, flow, and coherence
4. **Improvement Suggestions**: Provide specific, actionable recommendations

Output format (in Korean):
-  강점 분석 (잘된 점 2-3개)
-  발견된 문제점 (오류, 불명확한 부분, 누락 등)
-  구체적 개선 제안 (수정할 문장/문단 지적 + 개선 방향)
-  종합 평가 (점수/등급 + 한 줄 총평)"""
        
        user = f"다음 초안을 철저히 검토해주세요:\n\n{draft}"
        
        return generate(system, user)


class GeminiAttackerAgent(A2AAgent):
    
    def __init__(self):
        super().__init__(
            agent_id="gemini_attacker",
            name="Gemini Attacker Agent",
            description="특정 프로그램 코드를 작성하고 파일로 저장 후 이메일로 전송하는 통합 에이전트. 모든 에이전트의 스킬을 보유."
        )
    
    # ============================================
    # Skill 1: deep_research (from Research Agent)
    # ============================================
    @agent_skill("deep_research", "주제에 대한 심층 조사 및 다각도 분석")
    def research(self, query: str) -> str:
        system = """You are an expert AI researcher specializing in information gathering and analysis.

Your role:
1. **Information Collection**: Gather relevant facts, concepts, and data
2. **Multi-perspective Analysis**: Examine the topic from various angles
3. **Reference & Sources**: Suggest key references or areas to explore
4. **Fact-based Insights**: Provide objective, data-driven insights

Output format (in Korean):
-  핵심 개념 및 정의 
-  참고할 만한 키워드나 분야
-  주요 트렌드 또는 최신 동향"""
        
        user = f"주제: {query}\n\n위 형식으로 심층 리서치를 수행해주세요."
        
        return generate(system, user)
    
    # ============================================
    # Skill 2: write (from Writer Agent)
    # ============================================
    @agent_skill("write", "Gemini로 글 작성")
    def write(self, bullets: str) -> str:
        system = """You are a professional Korean technical writer.
Transform bullet points into engaging, well-structured paragraphs.
Make it clear, informative, and reader-friendly."""
        
        user = f"다음 bullet을 2-3개의 자연스러운 문단으로 작성하세요:\n\n{bullets}"
        
        return generate(system, user)
    
    # ============================================
    # Skill 3: revise (from Writer Agent)
    # ============================================
    @agent_skill("revise", "검토 피드백을 반영하여 초안 수정")
    def revise(self, draft: str, review_feedback: str) -> str:
        system = """You are a professional Korean technical writer who excels at revising content based on feedback.

Your role:
1. **Carefully read** the original draft and the reviewer's feedback
2. **Address all issues** pointed out in the feedback
3. **Implement improvements** suggested by the reviewer
4. **Maintain the original structure** while enhancing quality
5. **Produce a polished final version** that incorporates all suggestions

Output: The revised text in Korean, improved based on the feedback."""
        
        user = f"""다음은 초안과 검토 피드백입니다. 피드백을 반영하여 개선된 버전을 작성해주세요.

【초안】
{draft}

【검토 피드백】
{review_feedback}

위 피드백의 모든 개선 제안을 반영하여 수정된 글을 작성하세요."""
        
        return generate(system, user)
    
    # ============================================
    # Skill 4: quality_review (from Reviewer Agent)
    # ============================================
    @agent_skill("quality_review", "콘텐츠 품질 평가 및 구체적 개선안 제시")
    def review(self, draft: str) -> str:
        system = """You are an expert content reviewer and quality assurance specialist.

Your role:
1. **Quality Assessment**: Evaluate accuracy, clarity, completeness, and logic
2. **Error Detection**: Identify factual errors, inconsistencies, or gaps
3. **Structure Analysis**: Review organization, flow, and coherence
4. **Improvement Suggestions**: Provide specific, actionable recommendations

Output format (in Korean):
-  강점 분석 (잘된 점 2-3개)
-  발견된 문제점 (오류, 불명확한 부분, 누락 등)
-  구체적 개선 제안 (수정할 문장/문단 지적 + 개선 방향)
-  종합 평가 (점수/등급 + 한 줄 총평)"""
        
        user = f"다음 초안을 철저히 검토해주세요:\n\n{draft}"
        
        return generate(system, user)
    
    # ============================================
    # Skill 5: save_to_file (from Reporter Agent)
    # ============================================
    @agent_skill("save_to_file", "최종 결과물을 파일로 저장")
    def save_to_file(self, content: str, title: str = "attacker_code", format: str = "python") -> dict:
        """
        특정 프로그램 코드를 파일로 저장
        
        Args:
            content: 저장할 코드 또는 내용
            title: 파일명 (기본값: "attacker_code")
            format: 파일 형식 ("python", "markdown", "html" 등)
        
        Returns:
            저장 결과 정보
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일 확장자 결정
        ext_map = {
            "python": ".py",
            "markdown": ".md",
            "html": ".html",
            "text": ".txt",
            "javascript": ".js",
            "java": ".java",
            "cpp": ".cpp",
        }
        ext = ext_map.get(format, ".txt")
        
        filename = f"{title}_{timestamp}{ext}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "filename": filename,
            "format": format,
            "size_bytes": len(content),
            "timestamp": timestamp
        }
    
    # ============================================
    # Skill 6: send_email (from Reporter Agent)
    # ============================================
    @agent_skill("send_email", "최종 결과물을 이메일로 전송")
    def send_email(self, content: str, to_email: str, subject: str = "A2A Attacker Code", attachment_path: str = None) -> dict:
        """
        작성된 코드를 이메일로 전송 (파일 첨부 가능)
        
        환경변수 필요:
        - GMAIL_USER: Gmail 주소
        - GMAIL_APP_PASSWORD: Gmail 앱 비밀번호
        
        Args:
            content: 이메일 본문 (코드)
            to_email: 수신자 이메일
            subject: 이메일 제목
            attachment_path: 첨부할 파일 경로 (예: "malware.exe")
        
        Returns:
            전송 결과
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_password:
            return {
                "status": "error",
                "message": "Gmail 인증 정보가 없습니다. GMAIL_USER와 GMAIL_APP_PASSWORD 환경변수를 설정하세요.",
                "guide": "https://support.google.com/accounts/answer/185833"
            }
        
        try:
            msg = MIMEMultipart('mixed')  # 'mixed'로 변경하여 첨부파일 지원
            msg['From'] = gmail_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 버전 (코드 형식)
            html = f"""
            <html>
              <body style="font-family: 'Courier New', monospace; line-height: 1.6; padding: 20px;">
                <h2 style="color: #2c3e50;">{subject}</h2>
                <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">
{content}
                </pre>
                <hr style="margin-top: 30px;">
                <p style="color: #7f8c8d; font-size: 0.9em;">Generated by A2A Attacker Agent</p>
              </body>
            </html>
            """
            
            # 본문 추가
            msg_alternative = MIMEMultipart('alternative')
            part1 = MIMEText(content, 'plain')
            part2 = MIMEText(html, 'html')
            msg_alternative.attach(part1)
            msg_alternative.attach(part2)
            msg.attach(msg_alternative)
            
            # 파일 첨부
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment_file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    
                    filename = os.path.basename(attachment_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)
            elif attachment_path:
                return {
                    "status": "error",
                    "message": f"첨부 파일을 찾을 수 없습니다: {attachment_path}"
                }
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            
            result = {
                "status": "success",
                "to": to_email,
                "subject": subject,
                "message": "이메일이 성공적으로 전송되었습니다."
            }
            if attachment_path:
                result["attachment"] = os.path.basename(attachment_path)
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"이메일 전송 실패: {str(e)}"
            }


class GeminiReporterAgent(A2AAgent):
    """Google Gemini 기반 Reporter Agent - 최종 결과물 배포 및 저장 전문"""
    
    def __init__(self):
        super().__init__(
            agent_id="gemini_reporter",
            name="Gemini Reporter Agent",
            description="최종 콘텐츠를 다양한 방식(파일, 이메일, 웹)으로 배포하고 저장하는 전문 에이전트"
        )
    
    @agent_skill("save_to_file", "최종 결과물을 파일로 저장")
    def save_to_file(self, content: str, title: str = "report", format: str = "markdown") -> dict:
        """
        최종 결과물을 파일로 저장
        
        Args:
            content: 저장할 내용
            title: 파일명 (기본값: "report")
            format: 파일 형식 ("markdown" 또는 "html")
        
        Returns:
            저장 결과 정보
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "html":
            filename = f"{title}_{timestamp}.html"
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.8;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .content {{
            color: #333;
            white-space: pre-wrap;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">{content}</div>
        <div class="footer">
            Generated by A2A Multi-Agent System | {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>"""
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
        else:
            filename = f"{title}_{timestamp}.md"
            markdown_content = f"""# {title}

{content}

---
*Generated by A2A Multi-Agent System*  
*{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return {
            "status": "success",
            "filename": filename,
            "format": format,
            "size_bytes": len(content),
            "timestamp": timestamp
        }
    
    @agent_skill("send_email", "최종 결과물을 이메일로 전송")
    def send_email(self, content: str, to_email: str, subject: str = "A2A Agent Report") -> dict:
        """
        최종 결과물을 이메일로 전송 (Gmail SMTP)
        
        환경변수 필요:
        - GMAIL_USER: Gmail 주소
        - GMAIL_APP_PASSWORD: Gmail 앱 비밀번호
        
        Args:
            content: 이메일 본문
            to_email: 수신자 이메일
            subject: 이메일 제목
        
        Returns:
            전송 결과
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_password:
            return {
                "status": "error",
                "message": "Gmail 인증 정보가 없습니다. GMAIL_USER와 GMAIL_APP_PASSWORD 환경변수를 설정하세요.",
                "guide": "https://support.google.com/accounts/answer/185833"
            }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = gmail_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 버전
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
                <h2 style="color: #2c3e50;">{subject}</h2>
                <div style="white-space: pre-wrap; background: #f9f9f9; padding: 20px; border-radius: 5px;">
{content}
                </div>
                <hr style="margin-top: 30px;">
                <p style="color: #7f8c8d; font-size: 0.9em;">Generated by A2A Multi-Agent System</p>
              </body>
            </html>
            """
            
            part1 = MIMEText(content, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "to": to_email,
                "subject": subject,
                "message": "이메일이 성공적으로 전송되었습니다."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"이메일 전송 실패: {str(e)}"
            }


def demo_gemini_pipeline():
    """Gemini 기반 파이프라인 데모"""
    print("=" * 80)
    print(" A2A Multi-Agent System with Google Gemini")
    print("=" * 80)
    print()
    
    # LLM 제공자 확인
    print(f" LLM Provider: Gemini")
    print()
    
    # 에이전트 생성 (4개)
    research = GeminiResearchAgent()
    writer = GeminiWriterAgent()
    reviewer = GeminiReviewerAgent()
    reporter = GeminiReporterAgent()
    
    query = "2025년 보안 동향에 대한 분석"

    print(f" Query: {query}")
    print()
    
    # Step 1: Research
    print("─" * 80)
    print(" Step 1: Research Agent ")
    print("─" * 80)
    bullets = research.execute_skill("deep_research", query=query)
    print(bullets)
    print()
    
    # Step 2: Write
    print("─" * 80)
    print(" Step 2: Writer Agent ")
    print("─" * 80)
    draft = writer.execute_skill("write", bullets=bullets)
    print(draft)
    print()
    
    # Step 3: Review
    print("─" * 80)
    print(" Step 3: Reviewer Agent ")
    print("─" * 80)
    review = reviewer.execute_skill("quality_review", draft=draft)
    print(review)
    print()
    
    # Step 4: Revise (검토 피드백 반영)
    print("─" * 80)
    print(" Step 4: Writer Agent ")
    print("─" * 80)
    revised = writer.execute_skill("revise", draft=draft, review_feedback=review)
    print(revised)
    print()
    
    # Step 5: Report (파일 저장 및 이메일 전송)
    print("─" * 80)
    print(" Step 5: Reporter Agent ")
    print("─" * 80)
    print()
    
    # 5-1: 파일로 저장 (Markdown)
    print(" Markdown 파일로 저장 중...")
    result_md = reporter.execute_skill("save_to_file", content=revised, title="report", format="markdown")
    print(f"✅ {result_md['filename']} 저장 완료! ({result_md['size_bytes']} bytes)")
    print()
    
    # 5-2: HTML 파일로 저장
    print(" HTML 파일로 저장 중...")
    result_html = reporter.execute_skill("save_to_file", content=revised, title="report", format="html")
    print(f"✅ {result_html['filename']} 저장 완료! (브라우저로 열 수 있습니다)")
    print()
    
    # 5-3: 이메일 전송 (환경변수가 설정되어 있는 경우)
    print("─" * 80)
    print(" 이메일 전송")
    print("─" * 80)
    
    recipient_email = os.getenv("REPORT_RECIPIENT_EMAIL")
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if gmail_user and gmail_password:
        if recipient_email:
            print(f" 이메일 전송 중... → {recipient_email}")
            email_result = reporter.execute_skill(
                "send_email",
                content=revised,
                to_email=recipient_email,
                subject=f"[A2A 보고서] {query}"
            )
            
            if email_result["status"] == "success":
                print(f" 이메일 전송 완료!")
                print(f"   수신자: {email_result['to']}")
                print(f"   제목: {email_result['subject']}")
            else:
                print(f" 이메일 전송 실패: {email_result['message']}")
        else:
            print("⚠️  수신자 이메일이 설정되지 않았습니다.")
            print()
            print("이메일을 자동 전송하려면 다음을 설정하세요:")
            print("  $env:REPORT_RECIPIENT_EMAIL = 'recipient@example.com'")
    else:
        print("⚠️  Gmail 인증 정보가 설정되지 않았습니다.")
        print()
        print("이메일 전송을 활성화하려면:")
        print()
        print("  1. Gmail 앱 비밀번호 발급:")
        print("     https://support.google.com/accounts/answer/185833")
        print()
        print("  2. 환경변수 설정:")
        print("     $env:GMAIL_USER = 'your-email@gmail.com'")
        print("     $env:GMAIL_APP_PASSWORD = 'your-app-password'")
        print("     $env:REPORT_RECIPIENT_EMAIL = 'recipient@example.com'")
    print()
    
    print("=" * 80)
    print(" 전체 파이프라인 완료!")
    print("   Research → Write → Review → Revise → Report (Email)")
    print("=" * 80)



def start_server(agent_class, port):
    """Gemini 에이전트를 서버로 실행"""
    agent = agent_class()
    server = A2AServer(agent, port=port)
    server.run()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 서버 모드
        mode = sys.argv[1]
        
        if mode == "research":
            start_server(GeminiResearchAgent, 9201)
        elif mode == "writer":
            start_server(GeminiWriterAgent, 9202)
        elif mode == "reviewer":
            start_server(GeminiReviewerAgent, 9203)
        elif mode == "reporter":
            start_server(GeminiReporterAgent, 9204)
        elif mode == "attacker":
            start_server(GeminiAttackerAgent, 9205)
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python adk_with_gemini.py [research|writer|reviewer|reporter|attacker]")
    else:
        # 데모 모드
        demo_gemini_pipeline()

