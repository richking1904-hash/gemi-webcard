import os
import requests
import subprocess
import webbrowser  # 💡 완공된 주소로 인터넷 브라우저를 자동 가동하는 부품
from tkinter import messagebox  # 💡 배포 완료 팝업창을 띄우는 부품
from supabase import create_client, Client

# =====================================================================
# 📂 [경로 동기화] factory_modules 폴더 안의 부품들 수입
# =====================================================================
from factory_modules.gui_module import export_gui_data
from factory_modules.db_module import save_client_data_v2, initialize_db_factory
from factory_modules.ai_module import generate_webcard_code

# =====================================================================
# ⚙️ [GeMi 마스터 제어실] 핵심 자격 증명 주입 완료
# =====================================================================
SUPABASE_URL = "https://bjbpjkeahkupmeuvfwys.supabase.co"
SUPABASE_KEY = "sb_publishable_yHPGOhKSEPAehg-sin-7IQ_nHtfYBWU"

TELEGRAM_BOT_TOKEN = "8634715913:AAFViFIFDLaj-WsSvvuGUXmK1KMvjWOjNyE"
TELEGRAM_CHAT_ID = "859745575"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_supabase_tables_automatically():
    """🧱 슈파베이스 마스터 테이블 자동 체크"""
    print("📡 [Supabase] 테이블 상태 검사 및 자동 인프라 구축 중...")
    try:
        initialize_db_factory()
        print("✅ [Supabase] 마스터 테이블 진단 완료.")
    except Exception as e:
        print(f"ℹ️ [Supabase] 진단 중 참조 오류 발생: {e}")


def auto_git_push_hybrid(url_name):
    """
    🎯 [하이브리드 배포 엔진] 
    - 주소 이름이 없으면: 기존 메인 주소에 덮어쓰기 (main)
    - 주소 이름이 있으면: 완전히 독립된 새 인터넷 주소 단독 배포 (branch)
    """
    clean_url = "".join(c.lower() for c in url_name if c.isalnum() or c in ["-", "_"]).strip()
    
    # 💡 형규님에게 최종 안내해 드릴 인터넷 주소 매칭 분기
    if not clean_url:
        final_deployed_url = "https://gemi.vercel.app"  # 형규님의 기존 메인 버셀 주소 규격
    else:
        final_deployed_url = f"https://{clean_url}.vercel.app"

    try:
        # 1. 파일 포장 및 커밋
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. 🔍 분기 처리: 주소 이름을 안 적었을 때 (기존 주소 덮어쓰기)
        if not clean_url:
            print("\n🚚 5단계: [기존 주소 덮어쓰기] 메인 웹명함 업데이트 전송 시작...")
            subprocess.run(["git", "commit", "-m", "feat: 기존 메인 주소 덮어쓰기 빌드"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print(f"🚀 [Auto Git] 기존 주소 업로드 완료: {final_deployed_url}")
        
        # 3. 🔍 분기 처리: 주소 이름을 적었을 때 (새로운 독립 사이트 개설)
        else:
            print(f"\n🚚 5단계: [새로운 독립 웹사이트 생성] 주소명: {final_deployed_url} 배포 준비...")
            subprocess.run(["git", "commit", "-m", f"feat: 새 독립 사이트 배포 ({clean_url})"], check=True)
            
            subprocess.run(["git", "checkout", "-b", clean_url], check=False)
            subprocess.run(["git", "push", "origin", clean_url], check=True)
            subprocess.run(["git", "checkout", "main"], check=False)
            print(f"🚀 [Auto Git] 독립 라인 전송 완료: {final_deployed_url}")
            
        # 🔥 [오늘의 마스터피스] 모든 배포 전송 공정이 완벽하게 종료되면 형규님 화면에 알림창 팝업!
        show_completion_dialog(final_deployed_url)
        return True
        
    except Exception as e:
        print(f"❌ [Auto Git] 하이브리드 배포 전송 중 에러 발생: {e}")
        messagebox.showerror("배포 에러", f"자동 배포 전송 중 오류가 발생했습니다.\n에러 내용: {e}")
        return False


def show_completion_dialog(url):
    """🎉 전송 완료 후 형규님 눈앞에 완성된 주소를 직관적으로 띄우고 사이트를 열어주는 함수"""
    msg = f"축하합니다! GeMi 모바일 웹명함 공정이 완벽하게 끝났습니다.\n\n🌐 완성된 주소:\n{url}\n\n[확인]을 누르시면 잠시 후 Vercel 배포 갱신과 함께 인터넷 창이 자동으로 열립니다."
    
    # 알림창을 맨 앞으로 띄우기
    messagebox.showinfo("🎉 GeMi Factory 공정 완공 완료!", msg)
    
    # 🔗 형규님 컴퓨터의 기본 브라우저(크롬 등)를 켜서 완성된 명함 주소로 바로 다이렉트 접속!
    webbrowser.open(url)


def main_pipeline():
    print("🏭 [GeMi 마스터 스위치] 모바일 반응형 웹명함 공장 가동 시작...")
    
    # 0단계: 슈파베이스 원격 테이블 자동 진단
    init_supabase_tables_automatically()
    
    # 1단계: GUI 리모컨 팝업
    print("🖥️ [GUI] 리모컨 입력 창을 화면에 표시합니다. 입력을 완료하고 배포를 눌러주세요...")
    gui_payload = export_gui_data()
    
    if not gui_payload:
        print("❌ [Main] 리모컨이 입력 없이 닫혀 빌드를 중단합니다.")
        return

    # 리모컨에서 형규님이 입력한 주소 앞글자 가져오기
    user_info = gui_payload.get("user_info", {})
    custom_url_name = user_info.get("custom_url_name", "").strip()

    # 2단계: Supabase 스토리지 이미지 업로드
    local_images = gui_payload["assets"]["all_dropped_files"]
    print("\n📦 2단계: Supabase 스토리지 업로드 파이프라인 가동...")
    upload_result = save_client_data_v2(gui_payload, local_images)
    
    gui_payload["main_image_url"] = upload_result.get("main_image_url", "")
    gui_payload["other_image_urls"] = upload_result.get("other_image_urls", [])

    # 3단계: Gemini 2.0 Flash AI 코딩 가동
    print("\n🤖 3단계: Gemini 2.0 Flash AI 완전 동적 코딩 가동...")
    final_html_code = generate_webcard_code(gui_payload)
    
    if not final_html_code:
        print("❌ [Main] AI 소스코드 생성에 실패했습니다.")
        return

    # 4단계: 완성된 코드를 출력 폴더(dist)에 index.html 파일로 생성
    output_dir = "dist"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html_code)
        
    print(f"\n✨ [Main] 프리미엄 웹명함 소스코드 완제품 생성 성공.")

    # 🔥 5단계: [하이브리드 배포 및 완료 팝업 가동]
    auto_git_push_hybrid(custom_url_name)
    print("\n🏁 [GeMi Factory] 모든 하이브리드 공정이 완벽하게 종료되었습니다!")


if __name__ == "__main__":
    main_pipeline()