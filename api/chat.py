import json
import os
import urllib.request

def handler(request):
    # 1. 환경 변수 확인 (에러 발생 시 JSON 응답)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return send_res(request, {"reply": "API Key가 설정되지 않았습니다."}, 500)

    try:
        # 2. 요청 읽기
        content_length = int(request.headers.get('Content-Length', 0))
        body = json.loads(request.rfile.read(content_length).decode('utf-8'))
        user_message = body.get("message", "테스트")

        # 3. 아주 간단한 AI 응답 (오직 이것만 실행)
        payload = {"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": user_message}]}
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            reply = res_data["choices"][0]["message"]["content"]
            
        return send_res(request, {"reply": reply})

    except Exception as e:
        return send_res(request, {"reply": f"서버 실행 오류: {str(e)}"}, 500)

def send_res(request, data, code):
    request.send_response(code)
    request.send_header('Content-Type', 'application/json')
    request.send_header('Access-Control-Allow-Origin', '*')
    request.end_headers()
    request.wfile.write(json.dumps(data).encode('utf-8'))