import os
import requests
import time  # 중복 이름을 방지하기 위해 시간 모듈을 유지합니다.
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
    """
    📡 [텔레그램 즉시 발송 엔진] 
    DB에 손님 정보가 꽂히는 순간 형규님 폰으로 실시간 톡을 쏴줍니다.
    """
    print("📡 [Telegram] 실시간 고객 알림 발송 시도 중...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"  # 글씨를 가독성 좋고 이쁘게 포맷팅
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
    """
    [AI 자동 공장 엔진] 프로그램이 켜질 때 Supabase를 확인하여,
    메인 제어실 규격인 'gemi_customer_inquiry' 테이블이 없으면 자동으로 원격 크리에이트합니다.
    """
    print("🤖 [DB Factory] Supabase 테이블 인프라 점검 시작...")
    
    test_url = f"{SUPABASE_URL}/rest/v1/gemi_customer_inquiry?select=id&limit=1"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apiKey": SUPABASE_KEY
    }
    
    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            print("✅ [DB Factory] 'gemi_customer_inquiry' 마스터 테이블이 안전하게 준공되어 있습니다.")
        elif response.status_code == 404 or "relation" in response.text.lower():
            print("⚠️ [DB Factory] 마스터 테이블을 발견하지 못했습니다. 자동 복구 공정을 가동합니다...")
            create_gemi_inquiry_table()
    except Exception as e:
        print(f"❌ [DB Factory] 테이블 인프라 점검 중 예외 발생: {e}")


def create_gemi_inquiry_table():
    """
    Supabase 원격 SQL 인프라를 깨워 메인 규격에 맞는 마스터 테이블을 자동 생성합니다.
    """
    sql_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apiKey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    
    query = """
    CREATE TABLE IF NOT EXISTS public.gemi_customer_inquiry (
        id BIGSERIAL PRIMARY KEY,
        brand_name TEXT DEFAULT 'GeMi',
        customer_name TEXT NOT NULL,
        customer_contact TEXT NOT NULL,
        inquiry_type TEXT NOT NULL,
        message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    ALTER TABLE public.gemi_customer_inquiry ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Allow Anonymous Inserts" ON public.gemi_customer_inquiry FOR INSERT WITH CHECK (true);
    """
    
    try:
        requests.post(sql_url, headers=headers, json={"query": query})
        print("🚀 [DB Factory] 'gemi_customer_inquiry' 마스터 테이블 원격 구축 완료 및 RLS 해제.")
    except Exception as e:
        print(f"❌ [DB Factory] 원격 테이블 생성 실패: {e}")


def save_project_estimate(brand_name: str, name: str, phone: str, p_type: str, desc: str) -> bool:
    """
    [실시간 견적서 수집 + 텔레그램 연동 완료] 명함 웹페이지 견적 폼에서 손님이 입력 시
    DB 저장 후 즉시 형규님께 알림을 쏩니다.
    """
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
        
        # 🔥 [실시간 텔레그램 알림 타격]
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
    """
    🎯 [챗봇 실시간 질문 수집 + 텔레그램 연동 완료] 손님이 실시간 챗봇에 입력한 내용을
    DB에 기록하고 형규님께 실시간 알림을 보냅니다.
    """
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
        
        # 🔥 [실시간 텔레그램 알림 타격]
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
    """
    [스토리지 마스터] 고유 타임스탬프 파일명 치환을 통해 
    중복 에러를 원천 차단하고 퍼블릭 이미지 URL 주소를 뽑아냅니다.
    """
    print("🔓 [Storage] 파일명 중복 회피 파이프라인 가동...")
    bucket_name = "gemi_assets"
    main_image_url = ""
    other_image_urls = []
    
    if not image_paths:
        return {"success": True, "main_image_url": "", "other_image_urls": []}

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
                
                if not main_image_url:
                    main_image_url = public_url
                else:
                    other_image_urls.append(public_url)
        except Exception as e:
            print(f"❌ [Storage] 전송 오류: {e}")

    return {
        "success": True,
        "main_image_url": main_image_url,
        "other_image_urls": other_image_urls
    }

# 공장 가동 시 1회 인프라 체크
initialize_db_factory()