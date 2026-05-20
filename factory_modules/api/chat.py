# api/chat.py
from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

# Vercel 환경 변수에서 안전하게 키를 가져옵니다.
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        user_message = data.get("message")
        
        try:
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=[
                    {"role": "system", "content": "너는 GeMi 웹명함의 AI 비서야. 제공된 가이드라인을 바탕으로 친절하고 전문적으로 답변해."},
                    {"role": "user", "content": user_message}
                ]
            )
            ai_reply = response.choices[0].message.content
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # 웹명함에서 요청 허용
            self.end_headers()
            self.wfile.write(json.dumps({"reply": ai_reply}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))