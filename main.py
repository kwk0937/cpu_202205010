from openai import OpenAI
import streamlit as st
import os

# -------------------------------
# Streamlit 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Cerebras API 클라이언트
# -------------------------------
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# -------------------------------
# 기본 모델 설정
# -------------------------------
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "gpt-oss-120b"

# ===============================
# 사이드바 (설정 메뉴)
# ===============================
st.sidebar.title("설정 메뉴")

# 1) 모델 선택
model_list = [
    "gpt-oss-120b",
    "llama3.1-8b",
    "llama-3.3-70b",
    "qwen-3-32b",
    "qwen-3-235b-a22b-instruct-2507",
    "qwen-3-235b-a22b-thinking-2507"
]

selected_model = st.sidebar.selectbox("모델 선택", model_list)

# 세션에 저장
st.session_state.llm_model = selected_model

# 2) 답변 길이 조절
max_tokens = st.sidebar.slider(
    "최대 답변 길이 (max tokens)",
    min_value=50,
    max_value=2000,
    value=600
)

# 3) temperature 조절
temperature = st.sidebar.slider(
    "창의성 온도 (temperature)",
    min_value=0.0,
    max_value=1.5,
    value=0.7,
    step=0.1
)

# 4) Think 모드 ON/OFF
think_mode = st.sidebar.checkbox("Think / Reasoning 모드 활성화", value=False)

# 5) 어시스턴트 말투 선택
tone = st.sidebar.selectbox(
    "어시스턴트 말투 선택",
    [
        "기본",
        "丁寧하고 공손한 말투",
        "친근하고 편안한 말투",
        "격려하는 멘토 말투",
        "차갑고 분석적인 말투",
        "유머러스한 말투"
    ]
)

# 말투 미리보기
if tone == "丁寧하고 공손한 말투":
    tone_preview = "말투 예) 말씀 감사합니다. 도움이 될 만한 내용을 안내드리겠습니다."
elif tone == "친근하고 편안한 말투":
    tone_preview = "말투 예) 오, 그거 재밌네. 한 번 같이 해결해보자."
elif tone == "격려하는 멘토 말투":
    tone_preview = "말투 예) 좋아, 지금 잘하고 있어. 다음 단계로 가보자."
elif tone == "차갑고 분석적인 말투":
    tone_preview = "말투 예) 결론만 말하겠습니다. 해당 문제의 핵심은 다음과 같습니다."
elif tone == "유머러스한 말투":
    tone_preview = "말투 예) 오호? 그건 마치 내 커피가 식기 전에 해결해야 하는 문제 같네."
else:
    tone_preview = "말투 예) 기본 설정이 적용됩니다."

st.sidebar.caption(f"미리보기: {tone_preview}")

# ===============================
# 모드 프롬프트 함수
# ===============================
def get_system_prompt(mode, tone, think_mode):
    tone_text = ""

    if tone == "丁寧하고 공손한 말투":
        tone_text = "丁寧하고 공손한 말투로 대답하세요."
    elif tone == "친근하고 편안한 말투":
        tone_text = "친근하고 편안한 말투로 자연스럽게 대답하세요."
    elif tone == "격려하는 멘토 말투":
        tone_text = "격려하고 힘이 되어주는 멘토 말투로 설명하세요."
    elif tone == "차갑고 분석적인 말투":
        tone_text = "최대한 감정을 배제하고 분석적이고 간결하게 대답하세요."
    elif tone == "유머러스한 말투":
        tone_text = "가벼운 유머를 섞어서 재밌게 설명하세요."

    think_text = ""
    if think_mode:
        think_text = "답변 전에 숨겨진 사고 과정을 내부적으로 수행하되 외부로 표시하지 마세요."

    # 기존 대화 모드 설정
    mode_prompt = {
        "기본 모드": "당신은 친절한 AI 조력자입니다.",
        "전문가 컨설턴트": "당신은 20년 경력의 마케팅 전략 컨설턴트입니다. 데이터 기반 전략을 제시하세요.",
        "친구 같은 조언자": "너는 따뜻하고 친근한 친구야. 편한 반말로 이야기해줘.",
        "소크라테스식 튜터": "당신은 질문 중심으로 사고를 유도하는 소크라테스식 튜터입니다.",
        "작업 효율 비서": "당신은 초고효율 비서입니다. 핵심만 빠르게 정리하세요.",
        "스토리텔러": "당신은 재능 있는 스토리텔러입니다. 모든 답변을 짧은 이야기처럼 표현하세요.",
        "악마의 변호인": "당신은 악마의 변호인입니다. 사용자의 주장에 반대되는 논리를 제시하세요.",
        "무한 질문 어린이": "당신은 5살 어린이입니다. 모든 말 끝에 '왜?'라고 물어보세요.",
        "평행우주 탐험가": "당신은 평행우주 전문가입니다. 현실 버전 + 평행우주 버전 2가지로 설명하세요.",
        "재즈 즉흥 연주자": "당신은 재즈 뮤지션처럼 즉흥적이고 변주된 설명을 합니다.",
        "타임트래블 역사학자": "당신은 시간여행 역사학자입니다. 과거-현재-미래 순으로 설명하세요."
    }

    return f"{mode_prompt[mode]} {tone_text} {think_text}"

# -------------------------------
# system prompt 적용
# -------------------------------
system_prompt = get_system_prompt(mode, tone, think_mode)

# ===============================
# 메인 화면
# ===============================
st.title("AI챗봇 만들기 프로젝트")

# 메시지 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 모드 변경 시 prompt 갱신
st.session_state.messages[0]["content"] = system_prompt

# 기존 대화 다시 출력
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ===============================
# 사용자 입력 처리
# ===============================
user_input = st.chat_input("메시지를 입력하세요.")
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state.llm_model,
            messages=st.session_state.messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
