import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            user_message = body.get("message", "")

            # API 키가 환경변수에서 잘 읽히는지 확인
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise Exception("API Key Missing")

            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            # 이제 에러 내용을 직접 응답으로 보내서 왜 안 되는지 화면에서 바로 확인할 수 있습니다.
            reply = f"오류 발생: {str(e)}"

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))