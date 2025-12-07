from openai import OpenAI
import streamlit as st
import os

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")

# Cerebras API 클라이언트 초기화
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# 모델 설정
llm_model = "gpt-oss-120b"
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = llm_model

# ---------------------------------------------------------
# 메인 UI
# ---------------------------------------------------------
st.title("AI챗봇 만들기 프로젝트")

# 화면 상단 selectbox (반드시 보인다)
mode = st.selectbox(
    "대화 모드를 선택하세요:",
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
    ],
    key="mode_selector"
)

# ---------------------------------------------------------
# 모드별 시스템 프롬프트
# ---------------------------------------------------------
def get_system_prompt(mode):
    if mode == "전문가 컨설턴트":
        return "당신은 20년 경력의 마케팅 전략 컨설턴트입니다. 데이터 기반 전략을 제시하세요."
    elif mode == "친구 같은 조언자":
        return "너는 따뜻한 내 친구야. 편하게 반말로 조언해줘."
    elif mode == "소크라테스식 튜터":
        return "당신은 소크라테스식 질문법을 사용하는 튜터입니다. 질문 중심으로 답하세요."
    elif mode == "작업 효율 비서":
        return "당신은 초고효율 비서입니다. 핵심만 빠르게 정리하세요."
    elif mode == "스토리텔러":
        return "당신은 스토리텔러입니다. 모든 설명을 짧은 이야기로 풀어주세요."
    elif mode == "악마의 변호인":
        return "당신은 악마의 변호인입니다. 사용자의 주장에 대한 반대 의견을 제시하세요."
    elif mode == "무한 질문 어린이":
        return "당신은 5살 어린이입니다. 모든 말에 '왜?'라고 물어보세요."
    elif mode == "평행우주 탐험가":
        return "당신은 평행우주 탐험가입니다. 현실 설명과 평행우주 버전을 함께 제시하세요."
    elif mode == "재즈 즉흥 연주자":
        return "당신은 재즈 즉흥 연주자입니다. 변주하듯 자유롭게 답하세요."
    elif mode == "타임트래블 역사학자":
        return "당신은 시간여행 역사학자입니다. 과거-현재-미래 순으로 설명하세요."
    else:
        return "당신은 친절한 AI 조력자입니다."

system_prompt = get_system_prompt(mode)

# ---------------------------------------------------------
# 메시지 초기화
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt("기본 모드")}
    ]

# 모드 변경 시 시스템 메시지 갱신
if st.session_state.messages[0]["content"] != system_prompt:
    st.session_state.messages[0]["content"] = system_prompt

# ---------------------------------------------------------
# 이전 메시지 출력
# ---------------------------------------------------------
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---------------------------------------------------------
# 사용자 입력 처리
# ---------------------------------------------------------
user_input = st.chat_input("메시지를 입력하세요.")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["llm_model"],
            messages=st.session_state.messages,
            temperature=0.7,
            max_completion_tokens=1000,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
