import os
import requests
import subprocess
import webbrowser
from tkinter import messagebox
from supabase import create_client, Client

# =====================================================================
# 📂 [경로 동기화] factory_modules 폴더 안의 부품들 수입
# =====================================================================
from factory_modules.gui_module import export_gui_data
from factory_modules.db_module import save_client_data_v2, initialize_db_factory
from factory_modules.ai_module import generate_webcard_code

# =====================================================================
# ⚙️ [GeMi 마스터 제어실] 핵심 자격 증명 주입 완료 (오타 전면 수정 완료!)
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
    🎯 [하이브리드 배포 엔진 - gemi-webcard 정밀 타격 버전]
    """
    clean_url = "".join(c.lower() for c in url_name if c.isalnum() or c in ["-", "_"]).strip()
    
    # 💡 형규님의 진짜 새 저장소 버셀 주소 매칭 (gemi-webcard 트랙 반영)
    if not clean_url:
        final_deployed_url = "https://gemi-webcard.vercel.app"
    else:
        final_deployed_url = f"https://{clean_url}.vercel.app"

    try:
        # 1. 파일 포장 및 커밋
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. 주소 이름을 안 적었을 때 (기존 주소 main 덮어쓰기)
        if not clean_url:
            print("\n🚚 5단계: [기존 주소 덮어쓰기] 메인 웹명함 업데이트 전송 시작...")
            subprocess.run(["git", "commit", "-m", "feat: 메인 주소 덮어쓰기 빌드"], check=False)
            
            # 현재 방 이름을 안전하게 main으로 고정하여 push
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            print(f"🚀 [Auto Git] 기존 주소 업로드 완료: {final_deployed_url}")
        
        # 3. 주소 이름을 적었을 때 (새로운 독립 사이트 개설)
        else:
            print(f"\n🚚 5단계: [새로운 독립 웹사이트 생성] 주소명: {final_deployed_url} 배포 준비...")
            subprocess.run(["git", "commit", "-m", f"feat: 새 독립 사이트 배포 ({clean_url})"], check=False)
            
            # 메인 기둥이 안전하게 올라간 뒤 서브 방을 파도록 안전장치 가동
            subprocess.run(["git", "branch", "-M", "main"], check=False)
            subprocess.run(["git", "checkout", "-b", clean_url], check=False)
            subprocess.run(["git", "push", "origin", clean_url], check=True)
            subprocess.run(["git", "checkout", "main"], check=False)
            print(f"🚀 [Auto Git] 독립 라인 전송 완료: {final_deployed_url}")
            
        # 모든 공정이 에러 없이 끝나면 팝업 가동!
        show_completion_dialog(final_deployed_url)
        return True
        
    except Exception as e:
        print(f"❌ [Auto Git] 하이브리드 배포 전송 중 에러 발생: {e}")
        messagebox.showerror("배포 에러", f"자동 배포 전송 중 오류가 발생했습니다.\n주소 혹은 브랜치 상태를 확인해주세요.\n에러 내용: {e}")
        return False


def show_completion_dialog(url):
    """🎉 전송 완료 후 형규님 눈앞에 완성된 주소를 직관적으로 띄우고 사이트를 열어주는 함수"""
    msg = f"축하합니다! GeMi 모바일 웹명함 공정이 완벽하게 끝났습니다.\n\n🌐 완성된 주소:\n{url}\n\n[확인]을 누르시면 인터넷 창이 자동으로 열립니다."
    messagebox.showinfo("🎉 GeMi Factory 공정 완공 완료!", msg)
    webbrowser.open(url)


def main_pipeline():
    print("🏭 [GeMi 마스터 스위치] 모바일 반응형 웹명함 공장 가동 시작...")
    init_supabase_tables_automatically()
    
    print("🖥️ [GUI] 리모컨 입력 창을 화면에 표시합니다...")
    gui_payload = export_gui_data()
    
    if not gui_payload:
        print("❌ [Main] 리모컨이 입력 없이 닫혀 빌드를 중단합니다.")
        return

    user_info = gui_payload.get("user_info", {})
    custom_url_name = user_info.get("custom_url_name", "").strip()

    local_images = gui_payload["assets"]["all_dropped_files"]
    print("\n📦 2단계: Supabase 스토리지 업로드 파이프라인 가동...")
    upload_result = save_client_data_v2(gui_payload, local_images)
    
    gui_payload["main_image_url"] = upload_result.get("main_image_url", "")
    gui_payload["other_image_urls"] = upload_result.get("other_image_urls", [])

    print("\n🤖 3단계: Gemini AI 완전 동적 코딩 가동...")
    final_html_code = generate_webcard_code(gui_payload)
    
    if not final_html_code:
        print("❌ [Main] AI 소스코드 생성에 실패했습니다.")
        return

    output_dir = "dist"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html_code)
        
    print(f"\n✨ [Main] 프리미엄 웹명함 소스코드 완제품 생성 성공.")

    # 5단계: 하이브리드 배포 가동
    auto_git_push_hybrid(custom_url_name)
    print("\n🏁 [GeMi Factory] 모든 하이브리드 공정이 종료되었습니다!")


if __name__ == "__main__":
    main_pipeline()