import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 보안 시스템 (Gatekeeper)
# ==========================================
st.set_page_config(layout="centered", page_title="최승규 2호기 - The Original")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 화면
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔒 접근 승인</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Access Code", type="password", label_visibility="collapsed")
        if st.button("Login", use_container_width=True):
            if password == "71140859":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("코드가 일치하지 않습니다.")
    st.stop()

# ==========================================
# 1. 디자인 & 스타일 (제미나이 웹 스타일)
# ==========================================
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* 전체 배경 및 텍스트 설정 (다크 모드 대응 및 가독성 최적화) */
    .stApp {
        background-color: #0e1117; /* 짙은 배경 (눈 편안함) */
        color: #e0e0e0; /* 밝은 회색 텍스트 */
    }
    
    /* 제목 스타일 */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin-top: 1.5em !important;
        margin-bottom: 0.8em !important;
    }
    
    /* 본문 텍스트 */
    .stMarkdown p, .stMarkdown li {
        font-size: 17px !important;
        line-height: 1.8 !important;
        color: #e0e0e0 !important;
    }
    
    /* 수식 스타일 (LaTeX) - 선명하게 */
    .katex {
        font-size: 1.2em !important;
        color: #a5d6ff !important; /* 수식은 살짝 푸른빛 돌게 강조 */
    }
    
    /* 강조 박스 등 제거하고 순수 텍스트 위주로 감 */
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 초기화 및 설정
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # [설정] 창의성 0.0 (기계적인 정확함 추구)
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("Pure Math Logic")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 초기화"):
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info("👈 문제를 업로드하면 **최적의 풀이**를 시작합니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🧠 1타 강사 빙의 중... (잠시만 기다려주세요)"):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            
            # [프롬프트] 형님이 캡처해주신 그 스타일 그대로 나오게 하는 주문
            prompt = """
            너는 대한민국 최고의 수능 수학 강사야.
            주어진 문제를 학생이 완벽하게 이해할 수 있도록 **논리적이고 체계적**으로 풀어줘.
            
            **[작성 스타일 가이드 - 캡처된 화면처럼]**
            1. **구조**: 
               - **Method 1: 정석 풀이** (교과서적 개념 활용)
               - **Method 2: 빠른 풀이** (실전 공식 및 스킬 활용)
               - **Method 3: 직관 풀이** (그래프 개형 및 기하적 해석)
            
            2. **서술 방식**:
               - **Step 1, Step 2, Step 3**와 같이 단계별로 명확히 나누어 서술해.
               - 줄글로 길게 쓰지 말고, **핵심 수식** 위주로 전개해.
               - "~입니다." 보다는 간결하고 명확한 문체 사용.
            
            3. **수식 (LaTeX)**:
               - 모든 수식은 LaTeX 포맷($...$)을 사용해.
               - **중요한 수식은 반드시 별도 줄(Display Math Mode, `$$...$$`)에 작성해서 중앙 정렬되게 해.** (가독성 핵심)
               - 분수는 `\\dfrac` 사용.

            4. **내용**:
               - 그래프 가이드 같은 건 따로 만들지 마.
               - 오직 **문제 풀이의 논리**에만 집중해. 형님이 보내준 캡처 화면처럼 **수식과 논리**로 압도해.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"오류: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면 (One Column)
# ==========================================
if st.session_state.analysis_result:
    # 레이아웃 나누지 않음. 통으로 보여줌.
    st.markdown(st.session_state.analysis_result)