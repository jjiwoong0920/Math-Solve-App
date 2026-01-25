import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# ==========================================
# 0. 보안 시스템 (Gatekeeper)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - Final")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 화면
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: black;'>🔒 1호기 보안 시스템</h2>", unsafe_allow_html=True)
        password = st.text_input("승인 코드", type="password")
        
        if st.button("접속"):
            if password == "71140859":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("코드가 일치하지 않습니다.")
    st.stop()

# ==========================================
# 1. 디자인 & 스타일 (고대비 + 무조건 스티키)
# ==========================================
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [핵심 1] 고대비 강제 적용 (시스템 다크모드 무시) */
    .stApp {
        background-color: #ffffff !important; /* 무조건 흰 배경 */
    }
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    
    /* 모든 텍스트 무조건 검은색 */
    p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: #000000 !important;
        line-height: 1.8 !important;
    }
    
    /* 수식(LaTeX)도 검은색 */
    .katex {
        color: #000000 !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
    }
    
    /* 사이드바는 형님 원하시던 민트색 유지 */
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span { color: #ffffff !important; }
    
    /* ====================================================================
       [핵심 2] 스크롤 고정 (오른쪽 기둥 전체 고정)
       ==================================================================== */
    
    /* 가로 정렬 기준을 상단으로 (필수) */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 오른쪽(2번째) 기둥을 타겟팅하여 고정 */
    div[data-testid="column"]:nth-of-type(2) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important;
        
        /* 가이드 박스 디자인을 기둥 자체에 적용 */
        background-color: #f8f9fa !important; /* 아주 연한 회색 */
        border: 2px solid #000000 !important; /* 진한 테두리 */
        border-radius: 10px !important;
        padding: 20px !important;
        
        height: fit-content !important;
        z-index: 999 !important;
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 초기화 및 설정
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # [설정] 창의성 0.0 (변덕 죽이기)
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("Ver. Contrast & Sticky")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 초기화"):
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info("👈 문제 사진을 업로드하세요.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🔄 분석 및 검증 중..."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            
            prompt = """
            너는 대한민국 1타 수학 강사야. 
            
            **[지시사항 1: 텍스트 스타일]**
            - 말투: "~임.", "~함." 처럼 명사형으로 간결하게 끝내. (잡담 금지)
            - **줄바꿈(가장 중요)**: 모든 문장은 번호(`1.`, `2.`)를 붙이고, 마침표가 끝나면 **무조건 줄을 바꿔.**
            - 정석 풀이도 줄글로 쓰지 말고 단계별로 끊어서 써.
            - 수식: LaTeX($...$) 사용. **분수는 `\\dfrac` 사용.**

            **[지시사항 2: 출력 형식]**
            결과를 `|||SPLIT|||`로 구분하여 출력해.

            **[Part 1: 문제 해설]**
            - **# Method 1: 정석 풀이** (번호 붙여서 단계별 줄바꿈)
            - **# Method 2: 빠른 풀이** (번호 붙여서 단계별 줄바꿈)
            - **# Method 3: 직관 풀이** (번호 붙여서 단계별 줄바꿈)

            `|||SPLIT|||`

            **[Part 2: 그래프 작도 가이드]**
            - **목적**: 학생이 연습장에 직접 그릴 수 있게 지시.
            - **내용**: 좌표 평면 설정, 함수 개형 그리기, 교점 찍기, 보조선 긋기.
            - **주의**: 여기서도 수식은 **반드시 LaTeX($...$)**를 써야 해. 절대 그냥 쓰지 마.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"오류: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    if "|||SPLIT|||" in full_text:
        parts = full_text.split("|||SPLIT|||")
        solution_text = parts[0].strip()
        guide_text = parts[1].strip()
    else:
        solution_text = full_text
        guide_text = "가이드 생성 실패"

    # [레이아웃 2:1]
    col_text, col_guide = st.columns([2, 1])
    
    # [왼쪽] 해설 (검은 글씨 확인 완료)
    with col_text:
        st.markdown(solution_text)
        
    # [오른쪽] Sticky 가이드 (배경 및 테두리는 CSS로 처리됨)
    with col_guide:
        # 제목
        st.markdown("### 📝 작도 가이드")
        st.markdown("---")
        
        # [핵심 수정] HTML 태그 없이 순수 마크다운으로 출력해야 LaTeX가 먹힙니다.
        # CSS가 이 컬럼 전체를 잡고 있으므로 박스 안에 예쁘게 들어갑니다.
        st.markdown(guide_text)