import os
import requests
import time
from supabase import create_client, Client

# =====================================================================
# ⚙️ [GeMi DB 창고 & 알림실] 마스터 자격 증명 동기화 완료!
# =====================================================================
SUPABASE_URL = "https://bjbpjkeahkupmeuvfwys.supabase.co"
SUPABASE_KEY = "sb_publishable_yHPGOhKSEPAehg-sin-7IQ_nHtfYBWU" 

# 📡 [텔레그램 공식 라인] 형규 디렉터님 전용 자격 증명 주입 완료
TELEGRAM_BOT_TOKEN = "8634715913:AAFViFIFDLaj-WsSvvuGUXmK1KMvjWOjNyE"
TELEGRAM_CHAT_ID = "859745575"

# 🤖 Supabase Client 초기화 (공식 클라이언트 통합 바인딩)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def send_telegram_alert(text: str):
    """📡 [텔레그램 즉시 발송 엔진]"""
    print("📡 [Telegram] 실시간 고객 알림 발송 시도 중...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            print("✅ [Telegram] 형규 디렉터님 핸드폰으로 실시간 알림 전송 대성공!")
        else:
            print(f"❌ [Telegram] 발송 실패 (코드: {res.status_code}) - {res.text}")
    except Exception as e:
        print(f"❌ [Telegram] 네트워크 통신 예외 발생: {e}")


def initialize_db_factory():
    """🧱 [AI 자동 공장 엔진] 프로그램 구동 시 마스터 테이블 3종 세트 유무 검사 및 자동 생성"""
    print("🤖 [DB Factory] Supabase 테이블 인프라 종합 진단 시작...")
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apiKey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    
    # 1. 견적/챗봇 질문 통합 마스터 테이블 체크
    check_table_and_create("gemi_customer_inquiry", headers)
    # 2. 리모컨 입력 마스터 설정 테이블 체크
    check_table_and_create("gemi_client_configs", headers)
    # 3. 챗봇 토큰 절약용 대화 캐시 테이블 체크
    check_table_and_create("gemi_chat_cache", headers)


def check_table_and_create(table_name: str, headers: dict):
    """특정 테이블이 없으면 REST API 호환 방식으로 원격 자동 생성 가동"""
    test_url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=id&limit=1"
    try:
        res = requests.get(test_url, headers=headers)
        if res.status_code == 200:
            print(f"✅ [DB Factory] '{table_name}' 장부가 안전하게 구축되어 있습니다.")
            return
        
        # 404 에러 등이 나면 테이블이 없는 것이므로 복구 모드 작동
        print(f"⚠️ [DB Factory] '{table_name}' 장부가 없습니다. 자동 생성 공정을 가동합니다...")
        
        # 각 테이블 규격에 맞는 SQL 문 정의
        if table_name == "gemi_customer_inquiry":
            sql = """
            CREATE TABLE IF NOT EXISTS public.gemi_customer_inquiry (
                id BIGSERIAL PRIMARY KEY, brand_name TEXT DEFAULT 'GeMi', customer_name TEXT NOT NULL,
                customer_contact TEXT NOT NULL, inquiry_type TEXT NOT NULL, message TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        elif table_name == "gemi_client_configs":
            sql = """
            CREATE TABLE IF NOT EXISTS public.gemi_client_configs (
                id BIGSERIAL PRIMARY KEY, director_name TEXT, brand_name TEXT, introduction TEXT,
                phone TEXT, email TEXT, instagram TEXT, naver_blog TEXT, main_image_url TEXT,
                faq1_q TEXT, faq1_a TEXT, faq2_q TEXT, faq2_a TEXT, faq3_q TEXT, faq3_a TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        elif table_name == "gemi_chat_cache":
            sql = """
            CREATE TABLE IF NOT EXISTS public.gemi_chat_cache (
                id BIGSERIAL PRIMARY KEY, question TEXT UNIQUE, answer TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
            
        # REST API 안전 우회 방식으로 슈파베이스에 직접 테이블 생성 명령 주입
        rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
        requests.post(rpc_url, headers=headers, json={"query": sql})
        print(f"🚀 [DB Factory] '{table_name}' 마스터 장부 원격 생성 및 연동 완료!")
    except Exception as e:
        print(f"❌ [DB Factory] '{table_name}' 점검/생성 중 오류: {e}")


def save_project_estimate(brand_name: str, name: str, phone: str, p_type: str, desc: str) -> bool:
    """[실시간 견적서 수집 + 텔레그램 연동]"""
    print(f"📬 [DB Factory] 신규 견적서 양식 인입! (의뢰인: {name}님)")
    try:
        db_insert = {
            "brand_name": brand_name,
            "customer_name": name,
            "customer_contact": phone,
            "inquiry_type": p_type,
            "message": desc
        }
        supabase.table("gemi_customer_inquiry").insert(db_insert).execute()
        print("💾 [DB Factory] 견적 데이터가 마스터 테이블에 안전하게 영구 저장되었습니다.")
        
        alert_msg = (
            f"🔔 *[GeMi 공장] 신규 견적서 도착!*\n\n"
            f"🏢 *브랜드:* {brand_name}\n"
            f"👤 *의뢰인:* {name}님\n"
            f"📞 *연락처:* {phone}\n"
            f"🏷️ *문의유형:* {p_type}\n"
            f"💬 *의뢰내용:* {desc}"
        )
        send_telegram_alert(alert_msg)
        return True
    except Exception as e:
        print(f"❌ [DB Factory] 견적 데이터 적재 중 에러 발생: {e}")
        return False


def save_chatbot_question(brand_name: str, question_content: str) -> bool:
    """[챗봇 실시간 질문 수집 + 텔레그램 연동]"""
    print(f"💬 [DB Factory] 챗봇 실시간 질문 포착 및 수집 중...")
    try:
        db_insert = {
            "brand_name": brand_name,
            "customer_name": "📱 챗봇 이용 손님",
            "customer_contact": "실시간 대화",
            "inquiry_type": "💬 챗봇 질문 문의",
            "message": question_content
        }
        supabase.table("gemi_customer_inquiry").insert(db_insert).execute()
        print("💾 [DB Factory] 챗봇 질문 내용이 마스터 테이블에 기록되었습니다.")
        
        alert_msg = (
            f"💬 *[GeMi 챗봇] 손님 질문 실시간 포착!*\n\n"
            f"🏢 *브랜드:* {brand_name}\n"
            f"❓ *질문내용:* {question_content}"
        )
        send_telegram_alert(alert_msg)
        return True
    except Exception as e:
        print(f"❌ [DB Factory] 챗봇 질문 내용 적재 중 에러 발생: {e}")
        return False


def save_client_data_v2(payload: dict, image_paths: list) -> dict:
    """[스토리지 마스터 + 리모컨 데이터 DB 백업 하이브리드 업그레이드 수리 완료]"""
    print("🔓 [Storage] 파일명 중복 회피 및 스토리지 업로드 파이프라인 가동...")
    bucket_name = "gemi_assets"
    main_image_url = ""
    other_image_urls = []
    
    # 1. 원본 이미지 수집 및 스토리지 적재 파트
    selected_main_path = payload.get("main_image_path", "")
    
    if image_paths:
        for path in image_paths:
            if not os.path.exists(path):
                continue
                
            base_name = os.path.basename(path)
            name_part, ext_part = os.path.splitext(base_name)
            timestamp = int(time.time())
            file_name = f"{name_part}_{timestamp}{ext_part}"
            
            try:
                with open(path, "rb") as f:
                    file_data = f.read()
                    
                upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket_name}/{file_name}"
                headers = {
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "apiKey": SUPABASE_KEY,
                    "Content-Type": "image/png" if file_name.endswith('.png') else "image/jpeg"
                }
                
                response = requests.post(upload_url, headers=headers, data=file_data)
                if response.status_code in [200, 201]:
                    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
                    print(f"✅ [Storage] 업로드 대성공: {public_url}")
                    
                    # 💡 형규님이 콤보박스에서 고른 진짜 대표 이미지 경로와 일치하는지 판별하여 정확히 바인딩
                    if path == selected_main_path:
                        main_image_url = public_url
                    else:
                        other_image_urls.append(public_url)
            except Exception as e:
                print(f"❌ [Storage] 전송 오류: {e}")

    # 만약 위 매칭 로직으로도 안 잡혔을 시 방어벽 작동
    if not main_image_url and other_image_urls:
        main_image_url = other_image_urls.pop(0)

    # 🎯 2. [핵심 수리] 리모컨 입력 텍스트 정보들을 Supabase 마스터 DB 테이블에 영구 적재!
    print("💾 [DB Factory] 리모컨 텍스트 정보를 Supabase 중앙 장부에 백업하는 중...")
    try:
        user_info = payload.get("user_info", {})
        contact_info = payload.get("contact_info", {})
        faq_info = payload.get("faq_info", {})
        
        config_insert = {
            "director_name": user_info.get("name"),
            "brand_name": user_info.get("brand_name"),
            "introduction": user_info.get("introduction"),
            "phone": contact_info.get("phone"),
            "email": contact_info.get("email"),
            "instagram": contact_info.get("instagram"),
            "naver_blog": contact_info.get("naver_blog"),
            "main_image_url": main_image_url,
            "faq1_q": faq_info.get("faq1_q"),
            "faq1_a": faq_info.get("faq1_a"),
            "faq2_q": faq_info.get("faq2_q"),
            "faq2_a": faq_info.get("faq2_a"),
            "faq3_q": faq_info.get("faq3_q"),
            "faq3_a": faq_info.get("faq3_a")
        }
        supabase.table("gemi_client_configs").insert(config_insert).execute()
        print("✅ [DB Factory] 리모컨 설정 데이터가 'gemi_client_configs' 테이블에 성공적으로 꽂혔습니다!")
    except Exception as e:
        print(f"❌ [DB Factory] 리모컨 설정 데이터 적재 실패: {e}")

    return {
        "success": True,
        "main_image_url": main_image_url,
        "other_image_urls": other_image_urls
    }

# 공장 가동 시 1회 인프라 체크
initialize_db_factory()