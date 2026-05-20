import json
import os
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            user_message = body.get("message", "")
            client_id = body.get("client_id", "default_user")

            # 1. Supabase 데이터 조회 (라이브러리 없이 직접 REST API 호출)
            headers = {"apikey": os.environ.get("SUPABASE_KEY"), "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}"}
            
            # 가이드라인 URL 가져오기
            g_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_clients?client_id=eq.{client_id}&select=guideline_txt_url"
            res_g = requests.get(g_url, headers=headers).json()
            guideline_text = ""
            if res_g and res_g[0].get("guideline_txt_url"):
                try: guideline_text = requests.get(res_g[0]["guideline_txt_url"], timeout=5).text
                except: guideline_text = "가이드라인 로드 실패"

            # 질문 횟수 가져오기
            c_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache?client_id=eq.{client_id}&select=irrelevant_count"
            res_c = requests.get(c_url, headers=headers).json()
            count = res_c[0]["irrelevant_count"] if res_c else 0
            
            # 2. 로직 처리
            if count >= 10:
                reply = "어이쿠, 10번을 다 쓰셨네요! 이제는 업무 문의만 부탁드려요. 😅"
            else:
                # 3. OpenRouter 직접 호출
                payload = {
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {"role": "system", "content": f"당신은 GeMi 어시스턴트입니다. 아래 가이드라인을 참조하세요.\n\n[가이드라인]: {guideline_text}\n\n질문이 업무와 무관하면 위트 있게 거절하고 '관련 없는 질문'이라는 표현을 꼭 써주세요."},
                        {"role": "user", "content": user_message}
                    ]
                }
                res_ai = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"}, json=payload).json()
                reply = res_ai["choices"][0]["message"]["content"]

                # 4. 관련 없는 질문 카운트 증가
                if "관련 없는 질문" in reply:
                    new_count = count + 1
                    u_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache"
                    requests.post(u_url, headers={**headers, "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}, json={"client_id": client_id, "irrelevant_count": new_count})
                    reply += f" (제한: {new_count}/10)"

        except Exception as e:
            reply = f"오류 발생: {str(e)}"

        # 결과 응답 (무조건 JSON 형태)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))