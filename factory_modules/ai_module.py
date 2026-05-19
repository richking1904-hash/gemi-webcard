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

    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": "You are a premium branding copywriter. Refine the given brand introduction into a luxury, minimalist presentation phrase (in Korean). Return ONLY the refined phrase without quotes."},
                {"role": "user", "content": f"원문: {introduction}"}
            ]
        )
        refined_intro = response.choices[0].message.content.strip()
    except: refined_intro = introduction

    rendered_code = template_code
    rendered_code = rendered_code.replace("${user_name}", director_name)
    rendered_code = rendered_code.replace("${brand_name}", brand_name)
    rendered_code = rendered_code.replace("${BRAND_NAME}", brand_name)
    rendered_code = rendered_code.replace("${DIRECTOR_NAME}", director_name)
    rendered_code = rendered_code.replace("${INTRODUCTION}", refined_intro)
    
    # 👑 [명함 웹 변수 영역에 마스터 메모장 주소 주입]
    rendered_code = rendered_code.replace("${GUIDELINE_TXT_URL}", guideline_txt_url if guideline_txt_url else "")
    
    default_img = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
    final_img_url = main_image_url if main_image_url else default_img
    rendered_code = rendered_code.replace("${main_image_url}", final_img_url)
    
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

    return rendered_code

def get_chatbot_response(gui_payload: dict, question: str) -> str:
    user_info = gui_payload.get("user_info", {})
    faq_info = gui_payload.get("faq_info", {})
    
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    guideline_url = gui_payload.get("guideline_txt_url", "")
    
    # 👑 [슈파베이스 창고에서 가이드라인 메모장을 다운로드해 정독하는 실시간 RAG 기동단]
    fetched_guideline_text = "제공된 특별 운영 가이드라인 지침서 없음."
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
        f"브랜드: {brand_name}, 대표 디렉터 자격: {director_name}, 소개: {user_info.get('introduction')}\n"
        f"📜 [슈파베이스 창고 연동 가이드라인 지침 본문 문서]:\n{fetched_guideline_text}\n"
        f"고정FAQ1: {faq_info.get('faq1_q')} -> {faq_info.get('faq1_a')}\n"
        f"고정FAQ2: {faq_info.get('faq2_q')} -> {faq_info.get('faq2_a')}"
    )

    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": f"너는 {brand_name}의 대표 디렉터 {director_name}를 대변하는 영리하고 세련된 AI 비서야. 제공된 가이드라인 운영 장부 문서를 철저히 정독하고 질문에 완벽하게 답변해라.\n\n--- 마스터 가이드라인 문서 장부 ---\n{client_info_str}\n\n🎯 [운영 및 대화 규칙]\n1. 비즈니스 비용, 작업 견적, 마감 스케줄 등 비즈니스 전문 질문은 문서 가이드라인에 적힌 팩트에 철저히 입각하여 신뢰감 있게 대답하세요.\n2. 가이드라인 문서에 아예 적혀있지 않은 엉뚱한 일상 질문, 농담, 사적인 위트 질문이 들어오면 거부하지 말고, 대표님의 고급스러운 이미지(Quiet Luxury)에 맞게 세련되고 위트 있게 농담으로 맞받아치세요.\n3. 답변 끝난 맨 마지막 줄에는 무조건 아래 의뢰서 전송 버튼 웹코드를 단 한 번만 삽입해라.\n<br><br><button onclick='switchPage(\"contactPage\")' style='background-color:#2563eb; color:white; font-weight:bold; font-size:12px; padding:10px 16px; border-radius:12px; width:100%; display:block; text-align:center;'>🚀 정식 프로젝트 의뢰하러 가기</button>"} ,
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        try: supabase_client.table(SUPABASE_TABLE).insert({"question": combined_question, "answer": answer}).execute()
        except: pass
        return answer
    except Exception as e: return "안녕하세요 디렉터 관제 비서입니다. 현재 일시적인 무전 혼선이 있으니 하단의 의뢰서 작성란을 이용해 주시면 대단히 감사하겠습니다."