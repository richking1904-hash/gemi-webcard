import json
import os
import urllib.request

def handler(request):
    try:
        # 1. 환경 변수 확인 (가장 먼저 수행)
        sb_url = os.environ.get("SUPABASE_URL")
        sb_key = os.environ.get("SUPABASE_KEY")
        or_key = os.environ.get("OPENROUTER_API_KEY")

        if not sb_url or not sb_key or not or_key:
            return send_json(request, {"reply": f"환경 변수 누락 확인 - URL:{bool(sb_url)}, KEY:{bool(sb_key)}, AI:{bool(or_key)}"}, 500)

        # 2. 요청 읽기
        content_length = int(request.headers.get('Content-Length', 0))
        body = json.loads(request.rfile.read(content_length).decode('utf-8'))
        
        # 3. 테스트 응답 (로직 진입 성공 여부 확인)
        return send_json(request, {"reply": "서버 정상 인식 및 로직 시작"})

    except Exception as e:
        return send_json(request, {"reply": f"에러: {str(e)}"}, 500)

def send_json(request, data, status=200):
    request.send_response(status)
    request.send_header('Content-Type', 'application/json')
    request.send_header('Access-Control-Allow-Origin', '*')
    request.end_headers()
    request.wfile.write(json.dumps(data).encode('utf-8'))