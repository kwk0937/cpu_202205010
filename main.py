from openai import OpenAI
import streamlit as st
import os

# -----------------------------------------------------------
# Streamlit 기본 설정
# -----------------------------------------------------------
st.set_page_config(
    page_title="AI 챗봇 프로젝트",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------
# Cerebras API 클라이언트 초기화
# -----------------------------------------------------------
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# -----------------------------------------------------------
# 사이드바 - 설정 메뉴
# -----------------------------------------------------------
st.sidebar.title("설정 메뉴")

# 1) 대화 모드 선택
mode = st.sidebar.selectbox(
    "대화 모드",
    [
        "기본 모드",
        "전문가 컨설턴트",
        "친구 같은 조언자",
        "소크라테스식 튜터",
        "작업 효율 비서",
        "스토리텔러",
        "악마의 변호인",
        "무한 질문 어린이",
        "평행우주 탐험가",
        "재즈 즉흥 연주자",
        "타임트래블 역사학자"
    ]
)

# 2) 모델 선택
model = st.sidebar.selectbox(
    "LLM 모델 선택",
    [
        "gpt-oss-120b",
        "llama-3.1-8b",
        "llama-3.3-70b",
        "qwen-3-32b",
        "qwen-3-235b-a22b-instruct-2507"
    ]
)

# 3) Temperature 조절
temperature = st.sidebar.slider("창의성 (Temperature)", 0.0, 1.5, 0.7, 0.1)

# 4) 답변 길이 제한
max_tokens = st.sidebar.slider("최대 답변 길이", 200, 4000, 1200, 100)

# 5) Think 모드 토글
think_mode = st.sidebar.checkbox("Think 모드 활성화", value=False)

# 6) 말투 미리보기
st.sidebar.subheader("현재 말투 미리보기")

# -----------------------------------------------------------
# 시스템 프롬프트 생성
# -----------------------------------------------------------
def get_system_prompt(mode, think_mode):
    
    base = ""

    if mode == "전문가 컨설턴트":
        base = """
당신은 20년 경력의 마케팅 전략 컨설턴트입니다.
데이터 기반의 전략, 실행 가능한 조언, 산업 사례를 바탕으로 답변하세요.
"""
    elif mode == "친구 같은 조언자":
        base = """
너는 따뜻하고 공감 잘하는 친구야. 편하게 반말로 조언해줘.
"""
    elif mode == "소크라테스식 튜터":
        base = """
당신은 소크라테스식 질문법을 사용하는 튜터입니다.
직접 답을 말하지 말고 질문으로 유도하세요.
"""
    elif mode == "작업 효율 비서":
        base = """
당신은 초고효율 업무 비서입니다. 핵심만 짧고 정확하게 전달하세요.
"""
    elif mode == "스토리텔러":
        base = """
당신은 스토리텔러입니다. 설명은 짧은 이야기나 비유로 전달하세요.
"""
    elif mode == "악마의 변호인":
        base = """
당신은 악마의 변호인 역할을 합니다. 사용자의 주장에 반대 근거를 제시하고 논리적 허점을 짚어주세요.
"""
    elif mode == "무한 질문 어린이":
        base = """
당신은 5살 어린이입니다. 모든 답변 후 '왜?' 라고 물어보세요.
"""
    elif mode == "평행우주 탐험가":
        base = """
당신은 평행우주 탐험가입니다.
항상 현실 설명 + 평행우주 설명 두 가지로 답하세요.
"""
    elif mode == "재즈 즉흥 연주자":
        base = """
당신은 재즈 즉흥 연주자입니다. 변주된 리듬감 있는 대답을 사용자에게 제공합니다.
"""
    elif mode == "타임트래블 역사학자":
        base = """
당신은 시간여행 역사학자입니다.
과거/현재/미래 관점에서 동시에 답변하세요.
"""
    else:
        base = "당신은 친절한 AI 조력자입니다."

    # Think 모드 추가
    think = ""

    if think_mode:
        think = """
추론 과정을 내부에서 충분히 생각한 뒤, 최종 답변만 사용자에게 전달하세요.
사용자에게는 생각 과정(Chain of Thought)을 절대 보여주지 마세요.
"""

    return base + think


system_prompt = get_system_prompt(mode, think_mode)

st.sidebar.write("현재 적용된 말투:")
st.sidebar.info(system_prompt[:200] + " ...")


# -----------------------------------------------------------
# 메인 영역
# -----------------------------------------------------------
st.title("AI 챗봇 만들기 프로젝트")

# 메시지 저장 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# system prompt 갱신
st.session_state.messages[0]["content"] = system_prompt

# 이전 메시지 출력
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# -----------------------------------------------------------
# 사용자 입력
# -----------------------------------------------------------
user_input = st.chat_input("메시지를 입력하세요.")

if user_input:

    # 저장
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 사용자 메시지 즉시 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            messages=st.session_state.messages,
            stream=True
        )
        ai_output = st.write_stream(stream)

    # 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": ai_output})
