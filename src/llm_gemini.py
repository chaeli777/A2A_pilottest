"""
Google Gemini API 클라이언트
공식 Google LLM 사용
"""
import os
import google.generativeai as genai

_model = None
_configured_key = None

def _get_model():
    """Gemini 모델 초기화"""
    global _model, _configured_key
    
    # 매번 환경변수에서 새로 읽기
    current_key = os.getenv("GEMINI_API_KEY")
    current_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    if not current_key:
        return None
    
    # API 키가 변경되면 모델 재생성
    if _model is None or _configured_key != current_key:
        genai.configure(api_key=current_key)
        _model = genai.GenerativeModel(current_model)
        _configured_key = current_key
    
    return _model


def generate(system: str, user: str) -> str:
    """
    Gemini로 텍스트 생성
    
    Args:
        system: 시스템 프롬프트 (Gemini는 system role 없음, user에 통합)
        user: 사용자 입력
    
    Returns:
        LLM 응답
    """
    model = _get_model()
    
    if model is None:
        print("[LLM] Gemini API key not set. Use: $env:GEMINI_API_KEY='your-key'")
        return f"[No Gemini API Key] System: {system[:50]}..."
    
    try:
        # Gemini는 system role이 없으므로 프롬프트에 통합
        full_prompt = f"""Role: {system}

Task: {user}

Response:"""
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"[LLM] Gemini error: {e}")
        return f"[Gemini Error] {str(e)}"


def generate_stream(system: str, user: str):
    """
    Gemini 스트리밍
    """
    model = _get_model()
    
    if model is None:
        response = generate(system, user)
        for char in response:
            yield char
        return
    
    try:
        full_prompt = f"""Role: {system}

Task: {user}

Response:"""
        
        response = model.generate_content(full_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        error_msg = f"[Gemini Error] {str(e)}"
        for char in error_msg:
            yield char


# 편의 함수
def is_available() -> bool:
    """Gemini API 사용 가능 여부"""
    return os.getenv("GEMINI_API_KEY") is not None

