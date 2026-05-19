import customtkinter as ctk
from tkinter import filedialog
import os
import requests  # 💡 인터넷에 주소가 이미 존재하는지 몰래 스캔하기 위해 필요합니다.

# 파일 목록을 누적해서 저장할 전역 변수 리스트
dropped_files = []
final_payload = None  # 메인 서버로 넘겨줄 최종 데이터 저장소

# [자료 파일 추가하기] 버튼 액션
def browse_files_manual():
    global dropped_files
    
    file_paths = filedialog.askopenfilenames(
        title="포트폴리오 이미지 또는 자료 선택 (다중 선택 가능)",
        filetypes=[("지원하는 모든 파일", "*.png *.jpg *.jpeg *.gif *.xlsx *.pdf"), 
                   ("이미지 파일", "*.png *.jpg *.jpeg *.gif")]
    )
    
    if file_paths:
        for path in file_paths:
            if path not in dropped_files:
                dropped_files.append(path)
        
        drop_zone_label.configure(
            text=f"📊 총 {len(dropped_files)}개의 파일이 안전하게 로드되었습니다.", 
            text_color="#64B5F6"
        )
        
        file_names = [os.path.basename(f) for f in dropped_files]
        main_image_combobox.configure(values=file_names)
        
        if file_names:
            main_image_combobox.set(file_names[-1])
            
        status_label.configure(text=f"➕ {len(file_paths)}개의 파일이 정상적으로 추가되었습니다.", text_color="#A5D6A7")

# [비우기] 버튼 액션
def reset_file_list():
    global dropped_files
    dropped_files.clear()
    drop_zone_label.configure(text="아래 버튼을 눌러 파일들을 추가하세요\n(png, jpg, xlsx, pdf 다중 선택 지원)", text_color="#888888")
    main_image_combobox.configure(values=["먼저 파일을 추가해 주세요"])
    main_image_combobox.set("먼저 파일을 추가해 주세요")
    status_label.configure(text="🧹 로드된 파일 목록이 초기화되었습니다.", text_color="#FFB74D")


# 🚀 [철벽 방어 업그레이드] 빌드 시작 버튼을 눌렀을 때 작동하는 배포 액션
def on_submit_click():
    global final_payload
    
    if not name_entry.get().strip() or not brand_name_entry.get().strip():
        status_label.configure(text="❌ 필수 정보(디렉터 이름, 브랜드명)를 입력해야 빌드가 시작됩니다.", text_color="#FF5252")
        return

    # 🔍 [형규님 맞춤형 핵심 교정] 실시간 주소 중복 사전 차단 엔진 가동
    input_url = url_name_entry.get().strip()
    clean_url = "".join(c.lower() for c in input_url if c.isalnum() or c in ["-", "_"]).strip()

    if clean_url:  # 주소창에 뭔가를 적었을 때만 중복 검사를 실행합니다 (비워두면 기존 덮어쓰기라 패스)
        status_label.configure(text="🔍 전 세계 Vercel 주소 장부에서 중복 여부를 실시간 조회 중...", text_color="#FFB74D")
        app.update_idletasks() # UI 실시간 갱신
        
        check_url = f"https://{clean_url}.vercel.app"
        try:
            # 주소로 가볍게 노크(head)해 봅니다.
            response = requests.head(check_url, timeout=3)
            
            # 만약 인터넷에 이미 사이트가 열려있다면 (상태코드가 200이거나 300번대 유효할 때)
            if response.status_code < 400:
                print(f"❌ [안전장치] 중복 주소 감지 차단: {check_url} 은 이미 사용 중입니다.")
                status_label.configure(
                    text=f"❌ 중복 주소! [{clean_url}]은 이미 다른 사람이 쓰고 있습니다. 이름을 변경해 주세요.", 
                    text_color="#FF5252"
                )
                return  # 💡 여기서 return을 때려버려서 창이 닫히지 않고 배포 진행을 완전히 막아버립니다!
                
        except Exception:
            # 통신 에러가 나거나 사이트가 없어서 연결이 안 되면 (404 Not Found 등) 사용 가능한 주소로 판단합니다.
            pass

    selected_main_name = main_image_combobox.get()
    main_image_full_path = ""
    for path in dropped_files:
        if os.path.basename(path) == selected_main_name:
            main_image_full_path = path
            break

    # 의뢰자가 입력한 정보 패키징
    final_payload = {
        "user_info": {
            "name": name_entry.get().strip(),
            "brand_name": brand_name_entry.get().strip(),
            "introduction": introduction_entry.get().strip(),
            "custom_url_name": clean_url
        },
        "contact_info": {
            "phone": phone_entry.get().strip(),
            "email": email_entry.get().strip(),
            "instagram": insta_entry.get().strip(),
            "naver_blog": blog_entry.get().strip()
        },
        "faq_info": {
            "faq1_q": faq_q1_entry.get().strip(),
            "faq1_a": faq_a1_entry.get().strip(),
            "faq2_q": faq_q2_entry.get().strip(),
            "faq2_a": faq_a2_entry.get().strip(),
            "faq3_q": faq_q3_entry.get().strip(),
            "faq3_a": faq_a3_entry.get().strip()
        },
        "design_preference": {
            "style": design_style_combobox.get()
        },
        "assets": {
            "all_dropped_files": dropped_files,
            "main_image_path": main_image_full_path
        },
        "ai_custom_requests": {
            "special_notes": ai_requests_textbox.get("1.0", "end").strip()
        }
    }
    
    print("\n📦 [gui_module.py] 주소 안전성 검사 통과! 리모컨을 닫고 마스터 공장을 가동합니다.")
    app.quit()
    app.destroy()


# 메인 제어실(main.py)이 호출했을 때 리모컨을 띄우고 붙잡아두는 함수
def export_gui_data():
    global app, final_payload
    print("🖥️ [GUI] 리모컨 창 가동 시작...")
    app.mainloop()
    return final_payload


# --- UI 레이아웃 빌드 ---
app = ctk.CTk()
app.title("GeMi WebCard Director v1.0")
app.geometry("620x840")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

scroll_frame = ctk.CTkScrollableFrame(app, width=590, height=820, fg_color="transparent")
scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

title_label = ctk.CTkLabel(scroll_frame, text="GeMi WebCard Director v1.0", font=("Helvetica", 22, "normal"), text_color="#E0E0E0")
title_label.pack(pady=(10, 15))

ctk.CTkLabel(scroll_frame, text="디렉터 이름 (필수):", font=("Arial", 12)).pack(anchor="w", padx=25)
name_entry = ctk.CTkEntry(scroll_frame, width=500, placeholder_text="예: 장형규", fg_color="#2A2A2A")
name_entry.pack(pady=(2, 8))

ctk.CTkLabel(scroll_frame, text="브랜드명 (필수):", font=("Arial", 12)).pack(anchor="w", padx=25)
brand_name_entry = ctk.CTkEntry(scroll_frame, width=500, placeholder_text="예: GeMi", fg_color="#2A2A2A")
brand_name_entry.pack(pady=(2, 8))

ctk.CTkLabel(scroll_frame, text="브랜드 한줄 소개:", font=("Arial", 12)).pack(anchor="w", padx=25)
introduction_entry = ctk.CTkEntry(scroll_frame, width=500, placeholder_text="예: 미니멀리즘과 프리미엄 감성을 담은 디자인 공간", fg_color="#2A2A2A")
introduction_entry.pack(pady=(2, 8))

# 원하는 웹사이트 주소창 배치
ctk.CTkLabel(scroll_frame, text="🌐 원하는 웹사이트 주소 이름 (선택):", font=("Arial", 12, "bold"), text_color="#64B5F6").pack(anchor="w", padx=25)
url_name_entry = ctk.CTkEntry(scroll_frame, width=500, placeholder_text="비워두면 기존 주소 덮어쓰기 / 입력 시 '입력값.vercel.app' 새 사이트 개설", fg_color="#1E293B", border_color="#3B82F6")
url_name_entry.pack(pady=(2, 12))

contact_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
contact_frame.pack(fill="x", padx=25, pady=5)

ctk.CTkLabel(contact_frame, text="📞 휴대폰 번호:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=(0,2))
ctk.CTkLabel(contact_frame, text="✉️ 이메일 주소:", font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=(20, 0), pady=(0,2))

phone_entry = ctk.CTkEntry(contact_frame, width=240, placeholder_text="010-1234-5678", fg_color="#2A2A2A")
phone_entry.grid(row=1, column=0, sticky="w")
email_entry = ctk.CTkEntry(contact_frame, width=240, placeholder_text="richbab@naver.com", fg_color="#2A2A2A")
email_entry.grid(row=1, column=1, sticky="w", padx=(20, 0))

ctk.CTkLabel(contact_frame, text="📸 인스타그램 ID:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=(8,2))
ctk.CTkLabel(contact_frame, text="🌐 네이버 블로그 URL:", font=("Arial", 12)).grid(row=2, column=1, sticky="w", padx=(20, 0), pady=(8,2))

insta_entry = ctk.CTkEntry(contact_frame, width=240, placeholder_text="gemi_design", fg_color="#2A2A2A")
insta_entry.grid(row=3, column=0, sticky="w")
blog_entry = ctk.CTkEntry(contact_frame, width=240, placeholder_text="https://blog.naver.com/...", fg_color="#2A2A2A")
blog_entry.grid(row=3, column=1, sticky="w", padx=(20, 0))

ctk.CTkLabel(scroll_frame, text="✨ 디자인 스타일 컨셉 고르기:", font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
design_style_combobox = ctk.CTkComboBox(
    scroll_frame, 
    values=["[차분한 미니멀]", "[고급스러운 호텔 타월 감성]", "[모던 스튜디오]", "[네추럴 그린]"], 
    width=500,
    fg_color="#2A2A2A"
)
design_style_combobox.pack(pady=(2, 15))
design_style_combobox.set("[차분한 미니멀]")

ctk.CTkLabel(scroll_frame, text="💬 챗봇 버튼용 의뢰인 FAQ 설정 (최대 3개):", font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(10, 0))
faq_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
faq_frame.pack(fill="x", padx=25, pady=5)

# FAQ 1
ctk.CTkLabel(faq_frame, text="질문 1:", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
faq_q1_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="버튼 텍스트 (예: 제작 기간은?)", fg_color="#2A2A2A")
faq_q1_entry.grid(row=1, column=0, sticky="w", pady=(0, 5))

ctk.CTkLabel(faq_frame, text="답변 1:", font=("Arial", 11)).grid(row=0, column=1, sticky="w", padx=(20, 0))
faq_a1_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="눌렀을 때 답변 (예: 3~5일 소요)", fg_color="#2A2A2A")
faq_a1_entry.grid(row=1, column=1, sticky="w", padx=(20, 0), pady=(0, 5))

# FAQ 2
ctk.CTkLabel(faq_frame, text="질문 2:", font=("Arial", 11)).grid(row=2, column=0, sticky="w")
faq_q2_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="버튼 텍스트 (예: 수정 횟수는?)", fg_color="#2A2A2A")
faq_q2_entry.grid(row=3, column=0, sticky="w", pady=(0, 5))

ctk.CTkLabel(faq_frame, text="답변 2:", font=("Arial", 11)).grid(row=2, column=1, sticky="w", padx=(20, 0))
faq_a2_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="눌렀을 때 답변 (예: 기본 2회 제공)", fg_color="#2A2A2A")
faq_a2_entry.grid(row=3, column=1, sticky="w", padx=(20, 0), pady=(0, 5))

# FAQ 3
ctk.CTkLabel(faq_frame, text="질문 3:", font=("Arial", 11)).grid(row=4, column=0, sticky="w")
faq_q3_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="버튼 텍스트 (예: 주말 작업 가능?)", fg_color="#2A2A2A")
faq_q3_entry.grid(row=5, column=0, sticky="w")

ctk.CTkLabel(faq_frame, text="답변 3:", font=("Arial", 11)).grid(row=4, column=1, sticky="w", padx=(20, 0))
faq_a3_entry = ctk.CTkEntry(faq_frame, width=240, placeholder_text="눌렀을 때 답변 (예: 협의 후 가능)", fg_color="#2A2A2A")
faq_a3_entry.grid(row=5, column=1, sticky="w", padx=(20, 0))

ctk.CTkLabel(scroll_frame, text="📥 포트폴리오 및 고유 데이터 자산 보관 상자:", font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
drop_zone_frame = ctk.CTkFrame(scroll_frame, width=500, height=65, fg_color="#1E1E1E", border_width=2, border_color="#444444")
drop_zone_frame.pack_propagate(False)
drop_zone_frame.pack(pady=(2, 5))

drop_zone_label = ctk.CTkLabel(
    drop_zone_frame, 
    text="아래 버튼을 눌러 파일들을 추가하세요\n(png, jpg, xlsx, pdf 다중 선택 지원)", 
    font=("Arial", 11),
    text_color="#888888"
)
drop_zone_label.pack(expand=True)

btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
btn_frame.pack(pady=(0, 12), fill="x", padx=25)

select_btn = ctk.CTkButton(btn_frame, text="📁 자료 파일 추가하기", command=browse_files_manual, width=360, fg_color="#2563EB", hover_color="#1D4ED8")
select_btn.pack(side="left", padx=(0, 10))

reset_btn = ctk.CTkButton(btn_frame, text="🧹 비우기", command=reset_file_list, width=130, fg_color="#333333", hover_color="#444444")
reset_btn.pack(side="left")

ctk.CTkLabel(scroll_frame, text="🎯 이 중 어떤 사진을 명함 메인 배경으로 쓰시겠습니까?", font=("Arial", 12)).pack(anchor="w", padx=25)
main_image_combobox = ctk.CTkComboBox(scroll_frame, values=["먼저 파일을 추가해 주세요"], width=500, fg_color="#2A2A2A")
main_image_combobox.pack(pady=(2, 15))

ctk.CTkLabel(scroll_frame, text="✍️ 추가 문의 및 AI 상세 요청 사항 (선택):", font=("Arial", 12)).pack(anchor="w", padx=25)
ai_requests_textbox = ctk.CTkTextbox(scroll_frame, width=500, height=65, fg_color="#2A2A2A", border_width=1, border_color="#444444")
ai_requests_textbox.pack(pady=(2, 8))

status_label = ctk.CTkLabel(scroll_frame, text="공장 가동 준비 중... 세팅 완료 후 아래 빌드 스위치를 가동하세요.", font=("Arial", 11), text_color="#888888")
status_label.pack(pady=3)

submit_button = ctk.CTkButton(
    scroll_frame, 
    text="🚀 모바일 반응형 웹명함 빌드 및 자동 배포 시작", 
    command=on_submit_click, 
    width=500, 
    height=45, 
    font=("Arial", 14, "bold"),
    fg_color="#1E3A8A",
    hover_color="#2563EB"
)
submit_button.pack(pady=(2, 15))

if __name__ == "__main__":
    app.mainloop()