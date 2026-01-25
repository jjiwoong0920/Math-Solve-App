import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 기본 설정 & 보안 시스템
# ==========================================
st.set_page_config(layout="centered", page_title="최승규 2호기 - Gemini 1.5 Pro")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# [보안] 로그인 화면
if not st.session_state.authenticated:
    st.markdown("<br><br><h2 style='text-align: center; color: white;'>🔒 접근 승인 요청</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Access Code", type="password", label_visibility="collapsed", placeholder="비밀번호 입력")
        if st.button("Login", use_container_width=True):
            if password == "71140859":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("🚫 접근 거부")
    st.stop()

# ==========================================
# 1. 디자인 & 스타일 (리얼 블랙 & 화이트)
# ==========================================
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    .stApp {
        background-color: #131314 !important;
        color: #ffffff !important;
    }
    h1, h2, h3, h4, p, li {
        color: #ffffff !important;
    }
    /* 수식 흰색 통일 */
    .katex {
        font-size: 1.15em !important;
        color: #ffffff !important; 
    }
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    
    div.stButton > button {
        background-color: #333333;
        color: white;
        border: 1px solid #555555;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 및 모델 설정 (Gemini 1.5 Pro 강제)
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # [설정] 창의성 0.0 (기계적인 정확도)
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    genai.configure(api_key=api_key)
    
    # =================================================================
    # [핵심] 1.5 Pro로 고정 (현재 가장 똑똑하고 안정적인 정식 Pro 모델)
    # 2.0/3.0은 API 권한 문제로 에러 날 수 있음 -> 1.5 Pro가 정답입니다.
    # =================================================================
    model_name = 'gemini-1.5-pro' 
    
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption(f"Engine: {model_name}") # 모델 이름 표시
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 초기화 (Reset)"):
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info(f"👈 문제 사진을 올려주세요. **{model_name} (고지능 모델)**이 대기 중입니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner(f"🧠 **{model_name} 분석 중... (시간이 조금 걸려도 정확합니다)**"):
        try:
            model = genai.GenerativeModel(model_name, generation_config=generation_config)
            
            prompt = """
            너는 대한민국 수능 수학 1타 강사야. 
            주어진 문제를 **사진 속 예시처럼** 아주 구체적이고 전문적인 용어를 사용해서 풀어줘.
            
            **[작성 원칙 - 리얼 제미나이 스타일 완벽 재현]**

            1. **제목 포맷 (핵심 개념 명시 - 가장 중요)**:
               - 단순 '풀이'라고 쓰지 마. 아래 예시처럼 [핵심 개념]을 제목에 박아넣어.
               - 예시:
                 **Method 1: 차함수와 인수정리 활용 (정석 & 추천)**
                 **Method 2: 극대·극소의 차 공식 활용 (빠른 풀이)**
                 **Method 3: 그래프 평행이동을 통한 단순화 (센스 풀이)**

            2. **수식 표현 (가독성)**:
               - 문장 중간 수식: $...$
               - **[필수] 핵심 계산 식이나 결과는 반드시 `$$ ... $$` (Display Math)를 사용하여 중앙에 크게 배치해.**
               - 분수: `\\dfrac` 사용.
               - 모든 수식 색상은 흰색으로 통일될 것이니 신경 쓰지 마.

            3. **서술 방식**:
               - **Step 1: 조건 해석**, **Step 2: 식 세우기**, **Step 3: 결론 도출** 구조를 지켜.
               - 문장은 명사형(~함, ~임) 또는 간결한 문장으로 끝내. 

            4. **내용**:
               - 오직 문제 풀이 텍스트만 출력해.
               - 논리적 비약 없이 꽉 찬 해설을 보여줘.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ **오류 발생**: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    st.markdown(st.session_state.analysis_result)