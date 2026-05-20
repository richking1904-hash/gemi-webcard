import json
import os
import urllib.request

def handler(request):
    try:
        # 1. 요청 처리
        content_length = int(request.headers.get('Content-Length', 0))
        body = json.loads(request.rfile.read(content_length).decode('utf-8'))
        user_message = body.get("message", "")
        client_id = body.get("client_id", "default_user")

        # 2. 환경 변수 체크
        if not os.environ.get("SUPABASE_URL") or not os.environ.get("OPENROUTER_API_KEY"):
            return send_json(request, {"reply": "환경 변수 오류"}, 500)

        # 3. 데이터 로직 (Supabase REST)
        headers = {
            "apikey": os.environ.get("SUPABASE_KEY"),
            "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}",
            "Content-Type": "application/json"
        }
        
        # 가이드라인 가져오기
        g_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_clients?client_id=eq.{client_id}&select=guideline_txt_url"
        with urllib.request.urlopen(urllib.request.Request(g_url, headers=headers)) as res:
            res_g = json.loads(res.read().decode('utf-8'))
            
        guideline_text = ""
        if isinstance(res_g, list) and len(res_g) > 0 and res_g[0].get("guideline_txt_url"):
            try:
                with urllib.request.urlopen(res_g[0]["guideline_txt_url"], timeout=5) as res_txt:
                    guideline_text = res_txt.read().decode('utf-8')
            except: guideline_text = "로드 실패"

        # 질문 횟수
        c_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache?client_id=eq.{client_id}&select=irrelevant_count"
        with urllib.request.urlopen(urllib.request.Request(c_url, headers=headers)) as res:
            res_c = json.loads(res.read().decode('utf-8'))
        count = res_c[0]["irrelevant_count"] if isinstance(res_c, list) and len(res_c) > 0 else 0
        
        # 4. AI 호출
        if count >= 10:
            reply = "어이쿠, 10번을 다 쓰셨네요! 이제는 업무 문의만 부탁드려요. 😅"
        else:
            payload = {
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {"role": "system", "content": f"당신은 GeMi 어시스턴트입니다. [가이드라인]: {guideline_text}\n\n질문이 업무와 무관하면 위트 있게 거절하고 '관련 없는 질문'이라는 표현을 꼭 써주세요."},
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
            
            # 관련 없는 질문 시 카운트 증가
            if "관련 없는 질문" in reply:
                new_count = count + 1
                u_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/gemi_chat_cache"
                u_data = json.dumps({"client_id": client_id, "irrelevant_count": new_count}).encode('utf-8')
                u_req = urllib.request.Request(u_url, data=u_data, headers={**headers, "Prefer": "resolution=merge-duplicates"})
                urllib.request.urlopen(u_req)
                reply += f" (제한: {new_count}/10)"
                
        return send_json(request, {"reply": reply})

    except Exception as e:
        return send_json(request, {"reply": f"에러: {str(e)}"}, 500)

def send_json(request, data, status=200):
    request.send_response(status)
    request.send_header('Content-Type', 'application/json')
    request.send_header('Access-Control-Allow-Origin', '*')
    request.end_headers()
    request.wfile.write(json.dumps(data).encode('utf-8'))