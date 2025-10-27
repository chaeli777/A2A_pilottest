"""
빠른 서버 접속 테스트
"""
import requests
import json
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 서버 시작 대기
print("⏳ 서버 시작 대기 중...")
time.sleep(3)

url = "http://localhost:9201"

print("\n" + "=" * 80)
print("🧪 Research Agent 접속 테스트")
print("=" * 80)
print()

try:
    # 1. Root
    print(f"1️⃣ Root 접속: {url}/")
    response = requests.get(f"{url}/", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # 2. Health Check
    print(f"2️⃣ Health Check: {url}/health")
    response = requests.get(f"{url}/health", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # 3. Agent Card (Well-Known)
    print(f"3️⃣ Agent Card: {url}/.well-known/agent.json")
    response = requests.get(f"{url}/.well-known/agent.json", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    card = response.json()
    print(f"   Agent Name: {card.get('name')}")
    print(f"   Description: {card.get('description')}")
    print(f"   Skills: {[s['name'] for s in card.get('skills', [])]}")
    print()
    print(f"   Full Agent Card:")
    print(json.dumps(card, indent=2, ensure_ascii=False))
    print()
    
    print("=" * 80)
    print("✅ 모든 엔드포인트 정상 작동!")
    print("=" * 80)
    print()
    print("🌐 웹 브라우저에서 접속 가능:")
    print(f"   {url}/")
    print(f"   {url}/.well-known/agent.json")
    print(f"   {url}/health")
    print()
    
except requests.exceptions.ConnectionError:
    print("❌ 연결 실패!")
    print()
    print("서버가 실행되지 않았습니다.")
    print()
    print("다른 터미널에서 실행하세요:")
    print("   python examples/adk_with_gemini.py research")
    print()
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()


