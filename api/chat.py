import json
import os
import urllib.request
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def handler(request, response):
    # (내부 로직은 그대로 유지하되, response 객체를 활용하는 방식)
    # ... 코드 내용 동일 ...
    # 1. 환경 변수 확인
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return send_res(request, {"reply": "API Key가 설정되지 않았습니다."}, 500)

    try:
        # 2. 요청 읽기
        content_length = int(request.headers.get('Content-Length', 0))
        body = json.loads(request.rfile.read(content_length).decode('utf-8'))
        user_message = body.get("message", "").strip()

        # 3. 캐시 확인 (Supabase에서 질문 검색)
        cache = supabase.table("gemi_chat_cache").select("answer").eq("question", user_message).execute()
        if cache.data and len(cache.data) > 0:
            return send_res(request, {"reply": cache.data[0]["answer"]})

        # 4. 캐시 없으면 AI 응답
        payload = {
            "model": "google/gemini-2.0-flash-001", 
            "messages": [
                {"role": "system", "content": "너는 브랜드 전문 상담원이야. 제공된 가이드라인을 바탕으로 친절하게 답변해."},
                {"role": "user", "content": user_message}
            ]
        }
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            reply = res_data["choices"][0]["message"]["content"]
            
        # 5. 답변 저장 (Supabase에 캐싱)
        supabase.table("gemi_chat_cache").insert({"question": user_message, "answer": reply}).execute()
            
        return send_res(request, {"reply": reply})

    except Exception as e:
        return send_res(request, {"reply": f"서버 실행 오류: {str(e)}"}, 500)

def send_res(request, data, code=200):
    request.send_response(code)
    request.send_header('Content-Type', 'application/json')
    request.send_header('Access-Control-Allow-Origin', '*')
    request.end_headers()
    request.wfile.write(json.dumps(data).encode('utf-8'))