import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 기본 설정 & 보안 시스템
# ==========================================
st.set_page_config(layout="centered", page_title="최승규 2호기 - Auto Pro")

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
            if password == "71140859": # 비밀번호
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
    
    .stApp { background-color: #131314 !important; color: #ffffff !important; }
    h1, h2, h3, h4, p, li { color: #ffffff !important; }
    /* 수식 흰색 통일 */
    .katex { font-size: 1.15em !important; color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    
    div.stButton > button { background-color: #333333; color: white; border: 1px solid #555555; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 설정 및 [핵심] Pro 모델 자동 탐지
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# 사용 가능한 모델 찾기 함수
def find_best_pro_model():
    try:
        # 사용 가능한 모델 리스트 조회
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: 1.5 Pro 계열 (최신)
        for m in models:
            if 'gemini-1.5-pro' in m:
                return m
        # 2순위: 1.0 Pro 계열 (안정)
        for m in models:
            if 'gemini-pro' in m and 'vision' not in m: # 비전 전용 제외
                return m
        # 3순위: 그냥 Pro 들어간 거 아무거나
        for m in models:
            if 'pro' in m:
                return m
                
        return 'gemini-1.5-flash' # 정 없으면 플래시라도 (비상용)
    except:
        return 'gemini-pro' # API 에러 시 기본값

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # [핵심] 형님 계정에서 되는 '진짜 Pro' 모델 자동 검색
    target_model = find_best_pro_model()
    
    # 설정: 창의성 0.0
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")
    target_model = "Unknown"

# ==========================================
# 3. 사이드바
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    # 현재 자동으로 잡은 모델 이름 표시
    st.caption(f"Connected: {target_model}") 
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
    st.info(f"👈 문제 사진을 올려주세요. **{target_model}** 모델이 자동으로 연결되었습니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner(f"🧠 **{target_model} 가동 중... (1타 강사 빙의)**"):
        try:
            model = genai.GenerativeModel(target_model, generation_config=generation_config)
            
            prompt = """
            너는 대한민국 수능 수학 1타 강사야. 
            주어진 문제를 **사진 속 예시처럼** 아주 구체적이고 전문적인 용어를 사용해서 풀어줘.
            
            **[작성 원칙 - 리얼 제미나이 스타일 완벽 재현]**

            1. **제목 포맷 (핵심 개념 명시 - 가장 중요)**:
               - 단순 '풀이'라고 쓰지 마. [핵심 개념]을 제목에 박아넣어.
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
            st.write("자동 연결된 모델이 문제를 일으켰습니다. API 키 권한을 확인해주세요.")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    st.markdown(st.session_state.analysis_result)