import datetime
from datetime import date
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="관리자 승인형 AI 사주 포털", page_icon="🔮", layout="wide"
)

# 세션 스테이트에 신청 내역 저장소 초기화 (실제 서비스는 DB 연동 필요)
if "saju_requests" not in st.session_state:
    st.session_state.saju_requests = []

# 스타일링 (CSS)
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        color: #4A90E2;
        font-size: 2.3rem;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">🔮 관리자 승인형 AI 사주 포털</p>',
    unsafe_allow_html=True,
)

# 화면 상단 탭 나누기 (사용자 화면 vs 관리자 화면)
tab1, tab2 = st.tabs(["👤 사주 신청하기 (사용자)", "🛠️ 관리자 승인 대시보드"])

# ==========================================
# [탭 1] 사용자: 사주 입력 및 신청
# ==========================================
with tab1:
    st.markdown(
        '<p class="sub-title">생년월일시와 받을 이메일을 남겨주시면, 관리자 검토 후 발송해 드립니다.</p>',
        unsafe_allow_html=True,
    )

    with st.form("user_saju_form"):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("이름", placeholder="예: 홍길동")
        with col2:
            gender = st.selectbox("성별", ["남성", "여성"], key="user_gender")

        birth_date = st.date_input(
            "생년월일",
            min_value=date(1920, 1, 1),
            max_value=datetime.date.today(),
            value=date(1990, 1, 1),
        )

        birth_time = st.time_input(
            "태어난 시간", value=datetime.time(12, 0), key="user_time"
        )
        recipient_email = st.text_input(
            "결과 받을 이메일 주소", placeholder="example@email.com"
        )

        submitted = st.form_submit_button("📩 사주 분석 신청하기")

    if submitted:
        if not user_name:
            st.warning("이름을 입력해주세요!")
        elif not recipient_email:
            st.warning("이메일 주소를 입력해주세요!")
        else:
            # 신청 데이터를 세션 리스트에 추가 (상태: 대기중)
            new_request = {
                "id": len(st.session_state.saju_requests) + 1,
                "name": user_name,
                "gender": gender,
                "birth": f"{birth_date.strftime('%Y-%m-%d')} {birth_time.strftime('%H:%M')}",
                "email": recipient_email,
                "status": "대기중",  # 대기중 / 승인완료
            }
            st.session_state.saju_requests.append(new_request)
            st.success(
                f"✨ **{user_name}**님의 사주 신청이 완료되었습니다! 관리자 승인 후 메일이 발송됩니다."
            )

# ==========================================
# [탭 2] 관리자: 대시보드 및 승인/발송 처리
# ==========================================
with tab2:
    st.subheader("🛠️ 사주 신청 대기 목록 및 승인 관리")
    st.info(
        "사용자가 신청한 내역을 확인하고, **[승인 및 메일 발송]** 버튼을 누르면 실제 이메일이 발송됩니다."
    )

    if not st.session_state.saju_requests:
        st.warning("현재 접수된 사주 신청 내역이 없습니다.")
    else:
        # 대기 목록 출력
        for req in st.session_state.saju_requests:
            with st.container():
                st.markdown(
                    f"""
                <div class="card">
                    <b>신청 번호:</b> #{req['id']} | <b>이름:</b> {req['name']} ({req['gender']})<br>
                    <b>생년월일시:</b> {req['birth']}<br>
                    <b>이메일:</b> {req['email']}<br>
                    <b>현재 상태:</b> <span style="color: {'orange' if req['status']=='대기중' else 'green'}; font-weight: bold;">{req['status']}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # 대기중인 항목에만 승인 버튼 노출
                if req["status"] == "대기중":
                    if st.button(
                        f"✅ [ID: {req['id']}] {req['name']}님 승인 및 메일 발송",
                        key=f"approve_{req['id']}",
                    ):
                        # 사주 결과 컨텐츠 생성
                        saju_content = f"""
                        [{req['name']}님의 맞춤 사주 분석 리포트]
                        - 생년월일: {req['birth']} ({req['gender']})
                        
                        [총운]
                        올해는 새로운 도약과 변화의 시기입니다. 꾸준히 준비해온 일에서 결실을 맺을 수 있습니다.
                        
                        [재물운]
                        문서운과 재물운이 함께 들어오는 형상입니다. 충동적인 지출만 주의한다면 안정적인 자산 관리가 가능합니다.
                        
                        [조언]
                        주변 사람들과의 소통을 넓히고 귀인의 조언을 경청하세요.
                        
                        - 관리자 승인을 통해 발송된 안전한 리포트입니다.
                        """

                        try:
                            # --- [실제 SMTP 메일 발송 로직 구간] ---
                            # smtp_server = "smtp.naver.com"
                            # smtp_port = 465
                            # sender_email = "your_email@naver.com"
                            # sender_password = "your_password"
                            #
                            # msg = MIMEText(saju_content, _charset='utf-8')
                            # msg['Subject'] = Header(f"🔮 {req['name']}님의 맞춤 사주 운세 리포트입니다.", 'utf-8')
                            # msg['From'] = sender_email
                            # msg['To'] = req['email']
                            #
                            # server = smtplib.SMTP_SSL(smtp_server, smtp_port)
                            # server.login(sender_email, sender_password)
                            # server.sendmail(sender_email, req['email'], msg.as_string())
                            # server.quit()
                            # ----------------------------------------

                            # 상태 변경 처리
                            req["status"] = "승인완료"
                            st.success(
                                f"🎉 {req['name']}님에게 메일이 성공적으로 발송되었습니다!"
                            )
                            st.rerun()  # 화면 새로고침

                        except Exception as e:
                            st.error(
                                f"메일 전송 실패 (관리자 계정 설정을 확인하세요): {e}"
                            )
                else:
                    st.markdown(
                        "🔒 *이미 승인 및 발송이 완료된 건입니다.*"
                    )
                st.markdown("---")