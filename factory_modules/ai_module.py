import os
import requests
import supabase
import base64
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
    
    # 👑 [수정] Base64로 안전하게 인코딩
    guideline_text = "error"
    if guideline_txt_url:
        try:
            res = requests.get(guideline_txt_url, timeout=5)
            if res.status_code == 200:
                guideline_text = base64.b64encode(res.text.encode('utf-8')).decode('utf-8')
        except:
            guideline_text = "error"

    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    introduction = user_info.get("introduction", "")

    template_path = os.path.join("factory_modules", "template.html")
    if not os.path.exists(template_path): template_path = "template.html"

    with open(template_path, "r", encoding="utf-8") as f: template_code = f.read()

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
    rendered_code = rendered_code.replace("${GUIDELINE_TXT_URL}", guideline_text)
    
    default_img = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
    rendered_code = rendered_code.replace("${main_image_url}", main_image_url if main_image_url else default_img)
    rendered_code = rendered_code.replace("${MAIN_IMAGE_URL}", main_image_url if main_image_url else default_img)
    
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