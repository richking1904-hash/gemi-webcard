import json
import os
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. 요청 데이터 읽기
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode('utf-8'))
            user_message = body.get("message", "")
            client_id = body.get("client_id", "default_user")

            # 2. 환경 변수 체크
            required_envs = ["SUPABASE_URL", "SUPABASE_KEY", "OPENROUTER_API_KEY"]
            for env in required_envs:
                if not os.environ.get(env):
                    raise Exception(f"환경 변수 설정 오류: {env}가 없습니다.")

            # 3. Supabase 접속 헤더
            headers = {
                "apikey": os.environ.get("SUPABASE_KEY"),
                "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}",
                "Content-Type": "application/json"
            }
            
            # 가이드라인 URL 가져오기
            g_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_clients?client_id=eq.{client_id}&select=guideline_txt_url"
            req_g = urllib.request.Request(g_url, headers=headers)
            with urllib.request.urlopen(req_g) as res:
                res_g = json.loads(res.read().decode('utf-8'))
            
            guideline_text = ""
            if isinstance(res_g, list) and len(res_g) > 0 and res_g[0].get("guideline_txt_url"):
                try: 
                    with urllib.request.urlopen(res_g[0]["guideline_txt_url"], timeout=5) as res_txt:
                        guideline_text = res_txt.read().decode('utf-8')
                except: 
                    guideline_text = "가이드라인 파일을 로드할 수 없습니다."

            # 질문 횟수 가져오기
            c_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache?client_id=eq.{client_id}&select=irrelevant_count"
            req_c = urllib.request.Request(c_url, headers=headers)
            with urllib.request.urlopen(req_c) as res:
                res_c = json.loads(res.read().decode('utf-8'))
            count = res_c[0]["irrelevant_count"] if isinstance(res_c, list) and len(res_c) > 0 else 0
            
            # 4. 로직 처리
            if count >= 10:
                reply = "어이쿠, 10번을 다 쓰셨네요! 이제는 업무 문의만 부탁드려요. 😅"
            else:
                # 3. AI 호출 (urllib 사용)
                payload = {
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {"role": "system", "content": f"당신은 GeMi 어시스턴트입니다. [가이드라인]: {guideline_text}\n\n업무 무관 질문은 위트 있게 거절하고 '관련 없는 질문'이라는 표현을 꼭 써주세요."},
                        {"role": "user", "content": user_message}
                    ]
                }
                ai_req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode('utf-8'),
                    headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(ai_req) as ai_res:
                    reply = json.loads(ai_res.read().decode('utf-8'))["choices"][0]["message"]["content"]

                # 5. 관련 없는 질문 카운트 증가
                if "관련 없는 질문" in reply:
                    new_count = count + 1
                    u_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache"
                    u_req = urllib.request.Request(u_url, data=json.dumps({"client_id": client_id, "irrelevant_count": new_count}).encode('utf-8'), headers={**headers, "Prefer": "resolution=merge-duplicates"})
                    urllib.request.urlopen(u_req)
                    reply += f" (제한: {new_count}/10)"

        except Exception as e:
            reply = f"시스템 오류: {str(e)}"

        # 6. 결과 응답 (무조건 JSON 형태 보장)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))