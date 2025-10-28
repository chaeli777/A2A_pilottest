"""
5개 A2A 에이전트 실행 스크립트 (Attacker Agent 포함)
각 에이전트를 별도 프로세스로 실행합니다.

Usage:
    python start_agents_5.py

종료:
    Ctrl+C를 누르면 모든 에이전트가 종료됩니다.
"""
import sys
import os
import subprocess
import time
import signal

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# 에이전트 설정 (5개 버전 - Attacker Agent 포함)
AGENTS = [
    {"name": "Research Agent", "mode": "research", "port": 9201},
    {"name": "Writer Agent", "mode": "writer", "port": 9202},
    {"name": "Reviewer Agent", "mode": "reviewer", "port": 9203},
    {"name": "Reporter Agent", "mode": "reporter", "port": 9204},
    {"name": "Attacker Agent", "mode": "attacker", "port": 9205},
]


class AgentManager:
    """에이전트 프로세스 관리자"""
    
    def __init__(self):
        self.processes = []
    
    def start_all(self):
        """모든 에이전트 시작"""
        print("=" * 80)
        print("🚀 A2A 에이전트 시스템 시작 (5 Agents)")
        print("=" * 80)
        print()
        
        for agent_config in AGENTS:
            self.start_agent(agent_config)
        
        print()
        print("=" * 80)
        print("✅ 모든 에이전트가 실행되었습니다!")
        print("=" * 80)
        print()
        print("에이전트 목록:")
        for agent_config in AGENTS:
            print(f"  • {agent_config['name']:20s} - http://localhost:{agent_config['port']}")
        print()
        print("Agent Card 확인:")
        for agent_config in AGENTS:
            print(f"  • http://localhost:{agent_config['port']}/.well-known/agent.json")
        print()
        print("─" * 80)
        print("💡 이제 다른 터미널에서 파이프라인을 실행하세요:")
        print("   python run_dynamic_pipeline_5.py \"쿼리 입력\"")
        print()
        print("또는 Discovery 데모 실행:")
        print("   python examples/agent_discovery_demo.py smart")
        print("─" * 80)
        print()
        print("종료하려면 Ctrl+C를 누르세요...")
        print()
    
    def start_agent(self, agent_config):
        """개별 에이전트 시작"""
        name = agent_config['name']
        mode = agent_config['mode']
        port = agent_config['port']
        
        print(f"🔄 {name} 시작 중... (Port {port})")
        
        # Python 실행 파일 경로
        python_exe = sys.executable
        
        # 에이전트 실행 명령
        cmd = [python_exe, "examples/adk_with_gemini.py", mode]
        
        try:
            # 서브프로세스로 실행
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8'
            )
            
            self.processes.append({
                'name': name,
                'process': process,
                'port': port
            })
            
            # 시작 대기
            time.sleep(1)
            
            # 프로세스가 살아있는지 확인
            if process.poll() is None:
                print(f"✅ {name} 실행 완료")
            else:
                print(f"❌ {name} 실행 실패")
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"   오류: {stderr[:200]}")
        
        except Exception as e:
            print(f"❌ {name} 실행 중 오류: {e}")
    
    def stop_all(self):
        """모든 에이전트 종료"""
        print()
        print("=" * 80)
        print("🛑 모든 에이전트 종료 중...")
        print("=" * 80)
        print()
        
        for agent_info in self.processes:
            name = agent_info['name']
            process = agent_info['process']
            
            try:
                print(f"  • {name} 종료 중...")
                process.terminate()
                process.wait(timeout=5)
                print(f"    ✅ 종료 완료")
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  강제 종료 중...")
                process.kill()
                print(f"    ✅ 강제 종료 완료")
            except Exception as e:
                print(f"    ❌ 종료 실패: {e}")
        
        print()
        print("✅ 모든 에이전트가 종료되었습니다.")
    
    def wait(self):
        """프로세스가 종료될 때까지 대기"""
        try:
            while True:
                time.sleep(1)
                # 프로세스 상태 체크
                for agent_info in self.processes:
                    if agent_info['process'].poll() is not None:
                        print(f"⚠️  {agent_info['name']}가 예상치 않게 종료되었습니다.")
        except KeyboardInterrupt:
            print()
            print("Ctrl+C 감지됨. 종료합니다...")


def main():
    """메인 함수"""
    manager = AgentManager()
    
    # Signal handler 등록 (Ctrl+C)
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 에이전트 시작
    manager.start_all()
    
    # 대기
    manager.wait()
    
    # 종료
    manager.stop_all()


if __name__ == "__main__":
    main()

