import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (심플 순정 모드)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - 순정")

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    .stApp { background-color: #ffffff !important; }
    
    /* 본문 텍스트 가독성 (제미나이 웹과 유사하게) */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: #1a1a1a !important;
        margin-bottom: 1em !important;
    }
    
    /* 수식 스타일 */
    .katex { font-size: 1.1em !important; }
    
    /* 헤더 스타일 */
    h1, h2, h3 { color: #000000 !important; font-weight: 700 !important; }
    
    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #ddd;
        background: white;
        color: black;
    }
    .stButton > button:hover {
        border-color: #00C4B4;
        color: #00C4B4;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 초기화 및 설정
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'graph_method' not in st.session_state:
    st.session_state.graph_method = 1  # 기본값 Method 1

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바 (입력)
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("Pure Gemini Mode")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    if st.button("🔄 새로운 문제 풀기 (Reset)"):
        st.session_state.analysis_result = None
        st.session_state.graph_method = 1
        st.rerun()

# ==========================================
# 4. 메인 로직 (복잡한 파싱 제거)
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽에서 문제 사진을 업로드하면 바로 풀이가 시작됩니다.")
    st.stop()

# 이미지 로드
image = Image.open(uploaded_file)

# 분석 요청 (결과가 없으면 실행)
if st.session_state.analysis_result is None:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(image, caption="업로드된 문제", use_container_width=True)
    with c2:
        if st.button("🚀 1타 강사 풀이 시작", type="primary"):
            with st.spinner("분석 중입니다..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # [프롬프트] 파싱을 위한 특수 토큰 제거 -> 자연스러운 마크다운 출력 요청
                    prompt = """
                    너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

                    **[작성 원칙]**
                    1. **가독성**: 줄글보다는 개조식(-)을 사용하고, 문단 간격을 넉넉히 둬.
                    2. **수식**: 모든 수식은 LaTeX 형식($...$)을 사용해. (예: 함수 $f(x) = x^2$)
                    3. **금지**: 'Step 1', '화살표 기호(arrow)', '백틱(`) 강조'는 절대 쓰지 마. **Bold**만 사용해.
                    4. **구조**:
                       - **Method 1: 정석 풀이** (논리적 서술)
                       - **Method 2: 빠른 풀이** (실전 스킬)
                       - **Method 3: 직관 풀이** (도형/그래프 해석)

                    **[그래프 코드 요청]**
                    풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
                    - 코드는 `#CODE_START#` 와 `#CODE_END#` 라는 단어로 감싸줘. (이건 내가 분리해서 실행할 거야)
                    - 함수 이름: `def draw(method):` (method 번호를 받아서 해당 그래프를 그림)
                    - `figsize=(6, 6)` 고정.
                    - 한글 대신 영어 사용.
                    
                    자, 이제 풀이를 시작해.
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.session_state.analysis_result = response.text
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# ==========================================
# 5. 결과 화면 (순정 모드 출력)
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    # 1. 텍스트와 코드 분리 (단순 스플릿)
    # 제미나이가 코드를 #CODE_START# ... #CODE_END# 로 감싸서 줍니다.
    text_content = full_text
    code_content = ""
    
    if "#CODE_START#" in full_text:
        parts = full_text.split("#CODE_START#")
        text_content = parts[0] # 설명 부분
        
        if "#CODE_END#" in parts[1]:
            code_content = parts[1].split("#CODE_END#")[0] # 코드 부분
            # 뒤에 남은 텍스트가 있다면 붙이기
            text_content += parts[1].split("#CODE_END#")[1]

    # [중요] 텍스트 세탁 (최소한의 안전장치)
    # 백틱(`)만 제거하면 형광 문제는 99% 해결됩니다.
    text_content = text_content.replace("`", "")
    text_content = text_content.replace("arrow_down", "") # 혹시 모를 텍스트 제거

    # ==========================================
    # 화면 레이아웃: [왼쪽: 설명 텍스트] / [오른쪽: 그래프]
    # ==========================================
    col_text, col_graph = st.columns([1.2, 1])
    
    with col_text:
        st.markdown("### 📝 1타 강사 풀이")
        st.markdown("---")
        # [핵심] 제미나이의 답변을 그대로 렌더링 (가장 자연스러움)
        st.markdown(text_content)
        
    with col_graph:
        st.markdown("### 📐 그래프 시각화")
        
        # 그래프 선택 버튼
        m1, m2, m3 = st.columns(3)
        if m1.button("Method 1"): st.session_state.graph_method = 1
        if m2.button("Method 2"): st.session_state.graph_method = 2
        if m3.button("Method 3"): st.session_state.graph_method = 3
        
        st.caption(f"현재 보여주는 그래프: Method {st.session_state.graph_method}")

        # 코드 실행 및 그래프 그리기
        if code_content:
            try:
                # 코드 정리 (마크다운 기호 제거)
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                
                # 실행 환경
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](st.session_state.graph_method)
                    st.pyplot(fig)
                else:
                    st.warning("그래프 함수