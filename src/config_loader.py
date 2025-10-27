"""
환경 변수 및 .env 파일 자동 로드
"""
import os
import sys
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# .env 파일 자동 로드 시도
try:
    from dotenv import load_dotenv
    
    # 프로젝트 루트에서 .env 찾기
    root = Path(__file__).parent.parent
    env_file = root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[Config] ✅ .env 파일 로드: {env_file}")
    else:
        print(f"[Config] ⚠️  .env 파일 없음: {env_file}")
        print(f"[Config]    env_template.txt를 .env로 복사하세요")
        
except ImportError:
    print("[Config] ⚠️  python-dotenv not installed")
    print("[Config]    pip install python-dotenv")
    print("[Config]    환경 변수를 직접 설정하세요:")
    print("[Config]    $env:GEMINI_API_KEY='your-key'")


def get_api_key(service: str) -> str:
    """API 키 가져오기"""
    key_name = f"{service.upper()}_API_KEY"
    return os.getenv(key_name, "")


def is_api_key_set(service: str) -> bool:
    """API 키 설정 여부 확인"""
    return bool(get_api_key(service))


def show_status():
    """현재 API 키 설정 상태"""
    print("\n" + "=" * 60)
    print("🔑 API Key Status")
    print("=" * 60)
    
    keys = {
        "Google Gemini": "GEMINI",
        "OpenAI": "OPENAI",
        "Ollama": "OLLAMA_BASE_URL"
    }
    
    for name, env_var in keys.items():
        key = os.getenv(f"{env_var}_API_KEY") if env_var != "OLLAMA_BASE_URL" else os.getenv(env_var)
        if key:
            masked = key[:8] + "..." if len(key) > 8 else "***"
            print(f"  ✅ {name:<20} : {masked}")
        else:
            print(f"  ❌ {name:<20} : Not set")
    
    print("=" * 60)
    print()


if __name__ == "__main__":
    show_status()

