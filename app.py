import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (Sticky Graph - Height Fix)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - 순정")

st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [기존 유지] 텍스트 스타일 */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: inherit !important;
        margin-bottom: 1em !important;
    }
    
    /* [기존 유지] 제목 스타일 (20px, Bold) */
    h1, h2, h3 {
        font-size: 20px !important; 
        font-weight: 700 !important;
        color: inherit !important;
        margin-top: 1.5em !important;
        margin-bottom: 0.5em !important;
        letter-spacing: -0.5px !important;
    }
    
    /* [기존 유지] 기타 스타일 */
    .katex { font-size: 1.1em !important; color: inherit !important; }
    
    .stButton > button {
        border-radius: 8px;
        border: 1px solid var(--default-textColor) !important;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #00C4B4 !important;
        color: #00C4B4 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
    }
    section[data-testid="stSidebar"] * {
         color: #ffffff !important;
    }
    
    /* ====================================================================
       [1호기의 눈물] 스크롤 따라오기 (Sticky) - 높이 압축 기술
       ==================================================================== */
    
    /* 1. 가로 배치 컨테이너(Row)가 자식 높이를 억지로 늘리지 못하게 함 */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 2. 'sticky-target' 표식이 있는 오른쪽 컬럼을 타겟팅 */
    div[data-testid="column"]:has(#sticky-target) {
        position: fixed !important; /* 이번엔 sticky 대신 fixed로 강제할 수도 있지만, sticky로 갑니다 */
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important;
        z-index: 100 !important;
        
        /* [핵심] 높이를 강제로 '내용물 크기'만큼만 잡게 해서 움직일 공간 확보 */
        height: fit-content !important; 
        min-height: auto !important;
        
        overflow: visible !important;
        display: block !important;
    }
    
    /* 3. 혹시 모를 내부 iframe/div의 높이 간섭 제거 */
    div[data-testid="column"]:has(#sticky-target) > div {
        height: auto !important;
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
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 새로운 문제 풀기 (Reset)"):
        st.session_state.analysis_result = None
        st.session_state.graph_method = 1
        st.rerun()

# ==========================================
# 4. 메인 로직 (자동 분석 시작)
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽 사이드바에서 문제 사진을 업로드하면 **즉시 풀이가 시작**됩니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🕵️‍♂️ 1타 강사가 문제를 분석하고 있습니다... 잠시만 기다려주세요."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # [프롬프트 유지] 2:1 레이아웃, 글씨크기 9px, 그래프 단순화
            prompt = """
            너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

            **[작성 원칙]**
            1. **시작**: 서론, 인사말, 문제 요약 절대 하지 마. **무조건 '# Method 1'로 바로 시작해.** (반드시 # 하나만 써서 제목으로 만들어)
            2. **가독성**: 줄글보다는 개조식(-)을 사용하고, 문단 간격을 넉넉히 둬.
            3. **수식**: 모든 수식은 LaTeX 형식($...$)을 사용해. (예: 함수 $f(x) = x^2$)
            4. **금지**: 'Step 1', '화살표 기호(arrow)', '백틱(`) 강조'는 절대 쓰지 마. **Bold**만 사용해.
            5. **구조**:
               - **# Method 1: 정석 풀이** (논리적 서술)
               - **# Method 2: 빠른 풀이** (실전 스킬)
               - **# Method 3: 직관 풀이** (도형/그래프 해석)

            **[그래프 코드 요청 - 매우 중요]**
            풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
            - 코드는 `#CODE_START#` 와 `#CODE_END#` 로 감싸줘.
            - 함수 이름: `def draw(method):`
            - **[중요 1]** 각 Method의 '최종 결과(Final State)' 그래프 하나만 그려. (중간 과정 X)
            - `figsize=(6, 6)` 고정.
            - 한글 대신 영어 사용.
            - **[중요 2 - 표현 규칙]**:
                - **그래프(함수)**인 경우: 주요 **점의 좌표**와 **그래프 식**만 표시해.
                - **도형(기하)**인 경우: **변의 길이**, **각의 크기**, **보조선**만 표시해.
                - 그 외 불필요한 요소(복잡한 격자, 너무 많은 눈금 등)는 제거해서 깔끔하게 해.
            - **[중요 3 - 글씨 크기]**: 그래프 내부의 모든 텍스트(좌표, 식, 각도, 길이 등)는 **반드시 `fontsize=9`로 통일**해.
            
            자, 바로 # Method 1부터 시작해.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    # 분리
    text_content = full_text
    code_content = ""
    
    if "#CODE_START#" in full_text:
        parts = full_text.split("#CODE_START#")
        text_content = parts[0]
        
        if "#CODE_END#" in parts[1]:
            code_content = parts[1].split("#CODE_END#")[0]
            if len(parts[1].split("#CODE_END#")) > 1:
                text_content += parts[1].split("#CODE_END#")[1]

    # 세탁
    text_content = text_content.replace("`", "")
    text_content = text_content.replace("arrow_down", "")
    
    # 인사말 제거
    match = re.search(r'(#+\s*Method\s*1|\*{2}Method\s*1|Method\s*1:)', text_content, re.IGNORECASE)
    if match:
        text_content = text_content[match.start():]

    # ==========================================
    # 화면 레이아웃 (2:1 비율 유지)
    # ==========================================
    col_text, col_graph = st.columns([2, 1])
    
    with col_text:
        st.markdown(text_content)
        
    with col_graph:
        # [핵심] 닻(Anchor) 심기 - CSS가 이놈을 찾아서 고정합니다.
        st.markdown('<div id="sticky-target"></div>', unsafe_allow_html=True)
        
        # [Sticky 적용됨]
        st.markdown("### 📐 그래프 시각화")
        
        m1, m2, m3 = st.columns(3)
        if m1.button("Method 1"): st.session_state.graph_method = 1
        if m2.button("Method 2"): st.session_state.graph_method = 2
        if m3.button("Method 3"): st.session_state.graph_method = 3
        
        st.caption(f"현재 보여주는 그래프: Method {st.session_state.graph_method} (최종 결과)")

        if code_content:
            try:
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](st.session_state.graph_method)
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.error("그래프 생성 중 오류가 발생했습니다.")
                st.write(e)
        else:
            st.info("이 문제에 대한 시각화 코드가 생성되지 않았습니다.")