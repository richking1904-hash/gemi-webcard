import json
import os
import requests
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
from supabase import create_client

# Supabase 초기화
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            user_message = body.get("message", "")
            client_id = body.get("client_id", "default_user")

            # 1. 스토리지에서 가이드라인 파일 URL 가져오기 (gemi_clients 테이블 조회)
            client_data = supabase.table("gemi_clients").select("guideline_txt_url").eq("client_id", client_id).execute()
            guideline_text = ""
            if client_data.data and client_data.data[0].get("guideline_txt_url"):
                file_url = client_data.data[0]["guideline_txt_url"]
                try:
                    # 스토리지에서 텍스트 직접 다운로드
                    resp = requests.get(file_url, timeout=5)
                    guideline_text = resp.text
                except:
                    guideline_text = "가이드라인을 불러오는 중 오류 발생"

            # 2. 질문 횟수 제한 로직
            cache = supabase.table("gemi_chat_cache").select("irrelevant_count").eq("client_id", client_id).execute()
            count = cache.data[0]["irrelevant_count"] if cache.data else 0
            
            if count >= 10:
                reply = "어이쿠, 10번을 다 쓰셨네요! 이제는 업무 문의만 부탁드려요. 😅"
            else:
                # 3. AI 답변 (가이드라인 주입)
                api_key = os.environ.get("OPENROUTER_API_KEY")
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                
                system_prompt = f"당신은 GeMi 어시스턴트입니다. 아래 가이드라인을 참조하세요.\n\n[가이드라인]: {guideline_text}\n\n질문이 업무와 무관하면 위트 있게 거절하고 '관련 없는 질문'이라는 표현을 꼭 써주세요."
                
                response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
                )
                reply = response.choices[0].message.content

                # 4. 관련 없는 질문 카운트 증가
                if "관련 없는 질문" in reply:
                    new_count = count + 1
                    supabase.table("gemi_chat_cache").upsert({"client_id": client_id, "irrelevant_count": new_count}).execute()
                    reply += f" (제한: {new_count}/10)"

        except Exception as e:
            reply = f"오류 발생: {str(e)}"

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))