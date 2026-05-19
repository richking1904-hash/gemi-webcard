import os
import requests
import supabase
from openai import OpenAI

# =====================================================================
# ⚙️ [GeMi AI 제어실] 핵심 자격 증명 및 상자 동기화 완료
# =====================================================================
SUPABASE_URL = "https://bjbpjkeahkupmeuvfwys.supabase.co"
SUPABASE_KEY = "sb_publishable_yHPGOhKSEPAehg-sin-7IQ_nHtfYBWU"
SUPABASE_TABLE = "gemi_chat_cache"

# 형규님 핸드폰 실시간 텔레그램 알림용 자산 바인딩
TELEGRAM_BOT_TOKEN = "8634715913:AAFViFIFDLaj-WsSvvuGUXmK1KMvjWOjNyE"
TELEGRAM_CHAT_ID = "859745575"

# 슈파베이스 및 오픈라우터 클라이언트 초기화
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)


def generate_webcard_code(gui_payload: dict) -> str:
    """
    형규님의 template.html 기반으로 소문자/대문자 치환자들을 
    자석처럼 정교하게 매칭하여 데이터를 주입하는 하이브리드 엔진
    """
    user_info = gui_payload.get("user_info", {})
    contact_info = gui_payload.get("contact_info", {})
    faq_info = gui_payload.get("faq_info", {})
    design_preference = gui_payload.get("design_preference", {})
    ai_custom_requests = gui_payload.get("ai_custom_requests", {})

    main_image_url = gui_payload.get("main_image_url", "")
    other_image_urls = gui_payload.get("other_image_urls", [])
    
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    introduction = user_info.get("introduction", "")

    template_path = os.path.join("factory_modules", "template.html")
    if not os.path.exists(template_path):
        template_path = "template.html"

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_code = f.read()
    except Exception as e:
        print(f"❌ [AI] template.html 뼈대 파일을 읽어오는데 실패했습니다: {e}")
        return ""

    print("🤖 [AI Engine] 형규님의 디자인 뼈대를 고정하고, 콘텐츠 최적화 및 치환 작업 중...")

    client_context = f"Brand: {brand_name}, Style Preference: {design_preference.get('style')}, Request: {ai_custom_requests.get('special_notes')}"
    refined_intro = introduction
    
    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a premium branding copywriter. Refine the given brand introduction into a luxury, minimalist presentation phrase (in Korean). Return ONLY the refined phrase without any extra text or quotes."
                },
                {"role": "user", "content": f"원문: {introduction}\n컨셉: {client_context}"}
            ]
        )
        refined_intro = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ [AI] 카피라이팅 가공 중 오류 발생 (기본 입력값 사용): {e}")

    rendered_code = template_code
    rendered_code = rendered_code.replace("${user_name}", director_name)
    rendered_code = rendered_code.replace("${brand_name}", brand_name)
    rendered_code = rendered_code.replace("${BRAND_NAME}", brand_name)
    rendered_code = rendered_code.replace("${DIRECTOR_NAME}", director_name)
    rendered_code = rendered_code.replace("${INTRODUCTION}", refined_intro)
    
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

    insta_style = "display: inline-block;" if contact_info.get("instagram") else "display: none !important;"
    blog_style = "display: inline-block;" if contact_info.get("naver_blog") else "display: none !important;"
    rendered_code = rendered_code.replace("${INSTAGRAM_DISPLAY}", insta_style)
    rendered_code = rendered_code.replace("${BLOG_DISPLAY}", blog_style)

    rendered_code = rendered_code.replace("${question_1}", faq_info.get("faq1_q", "문의하기 1"))
    rendered_code = rendered_code.replace("${answer_1}", faq_info.get("faq1_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_2}", faq_info.get("faq2_q", "문의하기 2"))
    rendered_code = rendered_code.replace("${answer_2}", faq_info.get("faq2_a", "답변 준비 중입니다."))
    rendered_code = rendered_code.replace("${question_3}", faq_info.get("faq3_q", "문의하기 3"))
    rendered_code = rendered_code.replace("${answer_3}", faq_info.get("faq3_a", "답변 준비 중입니다."))

    print("✨ [AI Engine] 템플릿 맞춤형 기호($) 매칭 및 데이터 치환 주입 완료.")
    return rendered_code


def send_chatbot_telegram_alert(brand_name, user_name, question_content):
    """💬 손님이 실시간 챗봇에 타이핑 질문을 남겼을 때 형규님 폰으로 즉시 알림을 쏴주는 전용 비서"""
    if not TELEGRAM_BOT_TOKEN:
        return

    text = f"🚨 [GeMi 챗봇] 신규 대화 포착!\n\n" \
           f"🏢 브랜드: {brand_name} ({user_name} 디렉터)\n" \
           f"👤 손님: 📱 실시간 챗봇 대화 중\n" \
           f"✉️ 질문 내용: {question_content}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        print("🔔 [Telegram] 형규님 핸드폰으로 챗봇 실시간 알림 전송 완료!")
    except Exception as e:
        print(f"❌ [Telegram] 챗봇 알림 전송 중 통신 오류: {e}")


def get_chatbot_response(gui_payload: dict, question: str) -> str:
    """
    [3.5단계 완전 납땜] 손님이 직접 질문을 타이핑했을 때 
    답변 생성 + 슈파베이스 마스터 테이블 저장 + 형규님 핸드폰 텔레그램 실시간 알림을 동시 트리거
    """
    user_info = gui_payload.get("user_info", {})
    contact_info = gui_payload.get("contact_info", {})
    faq_info = gui_payload.get("faq_info", {})
    
    brand_name = user_info.get("brand_name", "GeMi")
    director_name = user_info.get("name", "장형규")
    
    client_context_brief = f"Brand:{brand_name}|Name:{director_name}"
    combined_question = f"Context: {client_context_brief}\nQuestion: {question}"

    # 1. Supabase 캐시 체크 (기존에 똑같이 물어본 질문인지 확인)
    try:
        response = supabase_client.table(SUPABASE_TABLE).select("answer", count="exact").eq("question", combined_question).execute()
        if response.count is not None and response.count > 0:
            print("💡 [Supabase] 기존 캐시에서 답변을 찾아왔습니다.")
            return response.data[0]["answer"]
    except Exception as e:
        print(f"Error querying Supabase: {e}")

    # 2. 캐시가 없으면 진짜 '새로운 질문'이므로 파이프라인 가동!
    print("🤖 [OpenRouter] Real-time Chatbot Response Generating...")
    
    client_info_str = (
        f"브랜드이름: {brand_name}, 대표자: {director_name}, "
        f"소개글: {user_info.get('introduction')}, 연락처: {contact_info.get('phone')}, 이메일: {contact_info.get('email')}, "
        f"FAQ1: {faq_info.get('faq1_q')} -> {faq_info.get('faq1_a')}, "
        f"FAQ2: {faq_info.get('faq2_q')} -> {faq_info.get('faq2_a')}, "
        f"FAQ3: {faq_info.get('faq3_q')} -> {faq_info.get('faq3_a')}"
    )

    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"너는 {brand_name} 브랜드의 친절한 인공지능 비서야.\n"
                        f"오직 아래 제공된 의뢰인의 정보에 기반해서만 고객의 질문에 정중하게 한국어로 답변해야 해.\n"
                        f"--- 제공된 정보 ---\n{client_info_str}\n---------------------\n"
                        f"만약 질문에 대한 정답이 제공된 정보 안에 없거나 모르는 내용이라면, 절대 할루시네이션을 지어내지 말고 "
                        f"'죄송합니다. 그 부분은 명함 주인에게 직접 문의해 주세요.'라고 답변해라."
                    )
                },
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content

        # 3. 답변 캐싱 저장
        try:
            supabase_client.table(SUPABASE_TABLE).insert({"question": combined_question, "answer": answer}).execute()
            print("💾 [Supabase] 새로운 답변 데이터베이스 캐싱 완료.")
        except Exception as e:
            print(f"Error storing answer in Supabase: {e}")

        # 🎯 [3.5단계 핵심 납땜] 챗봇용 실시간 알림 파이프라인 듀얼 트리거!
        # 1) 마스터 테이블(gemi_customer_inquiry)에 질문 영구 누적
        from factory_modules.db_module import save_chatbot_question
        save_chatbot_question(brand_name=brand_name, question_content=question)

        # 2) 형규님 스마트폰으로 텔레그램 실시간 푸시 알림 발송
        send_chatbot_telegram_alert(brand_name=brand_name, user_name=director_name, question_content=question)

        return answer
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."


if __name__ == '__main__':
    pass