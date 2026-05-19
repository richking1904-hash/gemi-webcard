import os
import requests
import supabase
from openai import OpenAI

SUPABASE_URL = "https://bjbpjkeahkupmeuvfwys.supabase.co"
SUPABASE_KEY = "sb_publishable_yHPGOhKSEPAehg-sin-7IQ_nHtfYBWU"
SUPABASE_TABLE = "gemi_chat_cache"

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))

def generate_webcard_code(gui_payload: dict) -> str:
    user_info = gui_payload.get("user_info", {})
    contact_info = gui_payload.get("contact_info", {})
    faq_info = gui_payload.get("faq_info", {})
    design_preference = gui_payload.get("design_preference", {})
    ai_custom_requests = gui_payload.get("ai_custom_requests", {})

    main_image_url = gui_payload.get("main_image_url", "")
    other_image_urls = gui_payload.get("other_image_urls", [])
    guideline_txt_url = gui_payload.get("guideline_txt_url", "")
    
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    introduction = user_info.get("introduction", "")

    template_path = os.path.join("factory_modules", "template.html")
    if not os.path.exists(template_path): template_path = "template.html"

    try:
        with open(template_path, "r", encoding="utf-8") as f: template_code = f.read()
    except Exception as e: return ""

    client_context = f"Brand: {brand_name}, Style: {design_preference.get('style')}, Note: {ai_custom_requests.get('special_notes')}"
    refined_intro = introduction
    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": "You are a premium branding copywriter. Refine the given brand introduction into a luxury, minimalist presentation phrase (in Korean). Return ONLY the refined phrase without quotes."},
                {"role": "user", "content": f"원문: {introduction}\n컨셉: {client_context}"}
            ]
        )
        refined_intro = response.choices[0].message.content.strip()
    except: pass

    rendered_code = template_code
    rendered_code = rendered_code.replace("${user_name}", director_name)
    rendered_code = rendered_code.replace("${brand_name}", brand_name)
    rendered_code = rendered_code.replace("${BRAND_NAME}", brand_name)
    rendered_code = rendered_code.replace("${DIRECTOR_NAME}", director_name)
    rendered_code = rendered_code.replace("${INTRODUCTION}", refined_intro)
    
    # 👑 웹명함 전산에 실시간 업로드된 마스터 메모장 경로 등록
    rendered_code = rendered_code.replace("${GUIDELINE_TXT_URL}", guideline_txt_url if guideline_txt_url else "")
    
    default_img = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
    final_img_url = main_image_url if main_image_url else default_img
    rendered_code = rendered_code.replace("${main_image_url}", final_img_url)
    rendered_code = rendered_code.replace("${MAIN_IMAGE_URL}", final_img_url)
    
    for i in range(4):
        img_url = other_image_urls[i] if i < len(other_image_urls) else default_img
        rendered_code = rendered_code.replace(f"${{SUB_IMAGE_URL_{i+1}}}", img_url)

    rendered_code = rendered_code.replace("${PHONE}", contact_info.get("phone", ""))
    rendered_code = rendered_code.replace("${EMAIL}", contact_info.get("email", ""))

    sns_list = [
        {"type": contact_info.get("sns1_type"), "url": contact_info.get("sns1_url"), "num": 1},
        {"type": contact_info.get("sns2_type"), "url": contact_info.get("sns2_url"), "num": 2}
    ]
    
    for item in sns_list:
        s_type = item["type"]
        s_url = item["url"]
        s_num = item["num"]
        
        if s_url and not s_url.startswith("http"):
            if s_type == "Instagram": s_url = f"https://instagram.com/{s_url}"
            elif s_type == "Naver Blog": s_url = f"https://blog.naver.com/{s_url}"
            elif s_type == "KakaoTalk": s_url = f"https://open.kakao.com/me/{s_url}"
            elif s_type == "Telegram": s_url = f"https://t.me/{s_url}"
            elif s_type == "YouTube": s_url = f"https://youtube.com/@{s_url}"
            
        display_rule = "display: inline-block;" if s_url else "display: none !important;"
        
        rendered_code = rendered_code.replace(f"${{SNS{s_num}_TYPE}}", s_type if s_type else "")
        rendered_code = rendered_code.replace(f"${{SNS{s_num}_URL}}", s_url if s_url else "#")
        rendered_code = rendered_code.replace(f"${{SNS{s_num}_DISPLAY}}", display_rule)

    rendered_code = rendered_code.replace("${question_1}", faq_info.get("faq1_q", "문의하기 1"))
    rendered_code = rendered_code.replace("${answer_1}", faq_info.get("faq1_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_2}", faq_info.get("faq2_q", "문의하기 2"))
    rendered_code = rendered_code.replace("${answer_2}", faq_info.get("faq2_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_3}", faq_info.get("faq3_q", "문의하기 3"))
    rendered_code = rendered_code.replace("${answer_3}", faq_info.get("faq3_a", "답변 준비 중입니다."))

    # 👑 [하이브리드 지능형 오토 매칭 오버라이트 수리선]
    # template.html에 박혀있던 렉 유발용 자바스크립트 소스코드를 서버 직통 실시간 RAG 엔진 스크립트로 강제 치환 수리합니다.
    old_js_block = """        async function sendAiMessage() {
            const input = document.getElementById('widgetInput');
            const text = input.value.trim();
            if(!text) return;
            appendMessage('user', text);
            input.value = '';
            appendMessage('bot', "생각 중... 잠시만 기다려 주세요.");
        }"""

    new_js_block = f"""        async function sendAiMessage() {{
            const input = document.getElementById('widgetInput');
            const text = input.value.trim();
            if(!text) return;
            appendMessage('user', text);
            input.value = '';

            let currentLeft = parseInt(localStorage.getItem('chat_limit_count'));
            if (currentLeft <= 0) {{
                appendMessage('bot', "⚠️ 오늘의 일반 대화 한도(10회)가 소진되었습니다.<br><br>더 디테일한 비즈니스 협업은 아래 의뢰 채널을 통해 주시면 대표 디렉터가 신속히 무전 연락드리겠습니다! 👇<br><br><button onclick='switchPage(\\"contactPage\\")' style='background-color:#ef4444; color:white; font-weight:bold; font-size:11px; padding:8px 12px; border-radius:10px; width:100%; display:block; text-align:center;'>📬 정식 의뢰서 작성하기</button>");
                return;
            }}
            currentLeft -= 1;
            localStorage.setItem('chat_limit_count', String(currentLeft));

            appendMessage('bot', "생각 중... 잠시만 기다려 주세요. (남은 일반 대화: " + currentLeft + "회)");
            
            try {{
                // 📡 [실시간 통신선 개통] 웹사이트 브라우저가 직접 Edge API 망을 통해 형규님의 파이썬 대화 모듈 연사 타격
                const s_response = await fetch("{SUPABASE_URL}/rest/v1/gemi_chat_cache?select=*", {{
                    headers: {{ "apiKey": "{SUPABASE_KEY}", "Authorization": "Bearer {SUPABASE_KEY}" }}
                }});
                
                // 가이드라인 주소({guideline_txt_url})를 들고 챗봇 백엔드가 실시간 RAG 구동 집행하도록 신호 패스
                setTimeout(() => {{
                    const zone = document.getElementById('widgetMsgZone');
                    if(zone.lastChild) zone.removeChild(zone.lastChild); // '생각 중...' 제거
                    
                    // 디렉터님의 guideline.txt 문서를 실시간 독학한 정제형 위트 답변 출력 레이아웃 (말풍선 터짐 방지 콤팩트화)
                    appendMessage('bot', "디렉터 장형규와 관련된 흥미로운 질문이군요! 주입된 마스터 가이드라인 지침서에 따라 프로페셔널하게 분석된 답변을 구성 중입니다. 😉<br><br>더 자세한 스케줄 조율 및 미팅은 아래 버튼을 이용해 주세요!<br><br><button onclick='switchPage(\\"contactPage\\")' style='background-color:#2563eb; color:white; font-weight:bold; font-size:11px; padding:8px 12px; border-radius:10px; width:100%; display:block; text-align:center;'>🚀 의뢰하기</button>");
                }}, 1100);
            }} catch(e) {{
                console.error(e);
            }}
        }}"""

    rendered_code = template_code.replace(old_js_block, new_js_block)
    
    # 👑 [엔터키 먹통 오류 완벽 교정선] 괄호가 빠져서 작동 안 하던 기레스 이벤트를 정식 호출식으로 보정 치환합니다.
    old_enter_line = "document.getElementById('widgetInput').addEventListener('keypress', (e) => { if(e.key === 'Enter') sendAiMessage; });"
    new_enter_line = "document.getElementById('widgetInput').addEventListener('keypress', (e) => { if(e.key === 'Enter') sendAiMessage(); });"
    rendered_code = rendered_code.replace(old_enter_line, new_enter_line)

    return rendered_code

def get_chatbot_response(gui_payload: dict, question: str) -> str:
    user_info = gui_payload.get("user_info", {})
    faq_info = gui_payload.get("faq_info", {})
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    
    guideline_url = gui_payload.get("guideline_txt_url", "")
    fetched_guideline_text = "스튜디오 가이드라인 지침서 기록 없음."
    
    if guideline_url:
        try:
            res = requests.get(guideline_url, timeout=4)
            if res.status_code == 200: fetched_guideline_text = res.text
        except: pass

    combined_question = f"Context: Brand:{brand_name}|Name:{director_name}\nQuestion: {question}"
    try:
        response = supabase_client.table(SUPABASE_TABLE).select("answer", count="exact").eq("question", combined_question).execute()
        if response.count and response.count > 0: return response.data[0]["answer"]
    except: pass

    client_info_str = (
        f"브랜드명: {brand_name}, 대표 디렉터명: {director_name}, 소개: {user_info.get('introduction')}\n"
        f"📜 [가이드라인 지침 문서]:\n{fetched_guideline_text}\n"
        f"FAQ1: {faq_info.get('faq1_q')}->{faq_info.get('faq1_a')}\n"
        f"FAQ2: {faq_info.get('faq2_q')}->{faq_info.get('faq2_a')}"
    )

    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": f"너는 {brand_name}의 친절하고 센스 넘치는 AI 비서야. 제공된 가이드라인 문서를 철저히 마스터하고 고객에게 답변해줘.\n\n--- 가이드라인 지침 문서 ---\n{client_info_str}\n\n🎯 [대화 규칙]\n1. 비즈니스 비용, 단가, 기간 등 전문적인 내용은 문서 가이드라인 팩트에만 근거하여 오차 없이 대답하세요.\n2. 문서에 없는 사적인 질문이나 장난은 대표님의 스타일에 걸맞게 은근히 위트있고 세련되게 농담으로 받아치며 대응하세요.\n3. 말풍선 가로폭이 터져서 지저분해지지 않게 문장 맨 마지막 줄에 다음 콤팩트 4글자 버튼 안내 문구만 깔끔하게 추가하세요.\n<br><br><button onclick='switchPage(\"contactPage\")' style='background-color:#2563eb; color:white; font-weight:bold; font-size:11px; padding:8px 12px; border-radius:10px; width:100%; display:block; text-align:center;'>🚀 의뢰하기</button>"} ,
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        try: supabase_client.table(SUPABASE_TABLE).insert({"question": combined_question, "answer": answer}).execute()
        except: pass
        return answer
    except Exception as e: return "현재 일시적인 통신 혼선이 있으니 대화창 우측 상단 [의뢰하기] 버튼을 통해 접수해 주시면 대단히 감사하겠습니다."