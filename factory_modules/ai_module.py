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

    # 🎯 꼬여있던 대표 이미지 수집 파이프라인 완벽 청소
    main_image_url = gui_payload.get("main_image_url", "")
    other_image_urls = gui_payload.get("other_image_urls", [])
    
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
    
    # 📸 대소문자 엑박 억까 방어벽 수립
    default_img = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
    final_img_url = main_image_url if main_image_url else default_img
    rendered_code = rendered_code.replace("${main_image_url}", final_img_url)
    rendered_code = rendered_code.replace("${MAIN_IMAGE_URL}", final_img_url)
    rendered_code = rendered_code.replace("${PROFILE_IMAGE_URL}", final_img_url)
    
    for i, img_url in enumerate(other_image_urls):
        rendered_code = rendered_code.replace(f"${{SUB_IMAGE_URL_{i+1}}}", img_url)

    rendered_code = rendered_code.replace("${PHONE}", contact_info.get("phone", ""))
    rendered_code = rendered_code.replace("${EMAIL}", contact_info.get("email", ""))
    rendered_code = rendered_code.replace("${INSTAGRAM}", contact_info.get("instagram", ""))
    rendered_code = rendered_code.replace("${NAVER_BLOG}", contact_info.get("naver_blog", ""))

    rendered_code = rendered_code.replace("${INSTAGRAM_DISPLAY}", "display: inline-block;" if contact_info.get("instagram") else "display: none !important;")
    rendered_code = rendered_code.replace("${BLOG_DISPLAY}", "display: inline-block;" if contact_info.get("naver_blog") else "display: none !important;")

    rendered_code = rendered_code.replace("${question_1}", faq_info.get("faq1_q", "문의하기 1"))
    rendered_code = rendered_code.replace("${answer_1}", faq_info.get("faq1_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_2}", faq_info.get("faq2_q", "문의하기 2"))
    rendered_code = rendered_code.replace("${answer_2}", faq_info.get("faq2_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_3}", faq_info.get("faq3_q", "문의하기 3"))
    rendered_code = rendered_code.replace("${answer_3}", faq_info.get("faq3_a", "답변 준비 중입니다."))

    return rendered_code

def get_chatbot_response(gui_payload: dict, question: str) -> str:
    user_info = gui_payload.get("user_info", {})
    contact_info = gui_payload.get("contact_info", {})
    faq_info = gui_payload.get("faq_info", {})
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    
    combined_question = f"Context: Brand:{brand_name}|Name:{director_name}\nQuestion: {question}"
    try:
        response = supabase_client.table(SUPABASE_TABLE).select("answer", count="exact").eq("question", combined_question).execute()
        if response.count and response.count > 0: return response.data[0]["answer"]
    except: pass

    client_info_str = f"브랜드: {brand_name}, 대표: {director_name}, 소개: {user_info.get('introduction')}, FAQ1: {faq_info.get('faq1_q')}->{faq_info.get('faq1_a')}, FAQ2: {faq_info.get('faq2_q')}->{faq_info.get('faq2_a')}"

    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": f"너는 {brand_name}의 친절한 AI 비서야. 제공된 정보에 기반해서 정중하게 한국어로 답변해줘.\n--- 정보 ---\n{client_info_str}\n---\n🎯 [비즈니스 규칙] 답변 끝난 뒤 맨 마지막 줄에 무조건 한 번만 아래 링크 버튼을 포함해라.\n더 자세한 프로젝트 의뢰는 아래 버튼을 눌러 남겨주시면 대표 디렉터가 연락드리겠습니다! 👇<br><br><button onclick='switchPage(\"contactPage\")' style='background-color:#2563eb; color:white; font-weight:bold; font-size:12px; padding:10px 16px; border-radius:12px; width:100%; display:block; text-align:center;'>🚀 정식 프로젝트 의뢰하러 가기</button>"} ,
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        try: supabase_client.table(SUPABASE_TABLE).insert({"question": combined_question, "answer": answer}).execute()
        except: pass
        return answer
    except Exception as e: return "죄송합니다. 답변 생성 중 오류가 발생했습니다."