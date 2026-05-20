import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

# OpenRouter 클라이언트 설정
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data)
        user_message = body.get("message")

        try:
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=[
                    {"role": "system", "content": "너는 GeMi 웹명함의 AI 비서야. 제공된 가이드라인을 바탕으로 친절하고 전문적으로 답변해."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply_text = response.choices[0].message.content
            
            # 응답 전송
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply_text}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))