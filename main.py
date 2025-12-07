from openai import OpenAI
import streamlit as st
import os

# Cerebras API 클라이언트 초기화
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# 기본 모델 설정
llm_model = "gpt-oss-120b"
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = llm_model

# --------------------------------------------
# 사이드바: 챗봇 설정 고정 영역
# --------------------------------------------
st.sidebar.title("설정 메뉴")

mode = st.sidebar.selectbox(
    "대화 모드 선택",
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

# --------------------------------------------
# 모드 프롬프트 함수
# --------------------------------------------
def get_system_prompt(mode):
    if mode == "전문가 컨설턴트":
        return "당신은 20년 경력의 마케팅 전략 컨설턴트입니다. 데이터 기반 구체적 전략을 제시하세요."
    elif mode == "친구 같은 조언자":
        return "너는 따뜻하고 공감 잘하는 내 친구야. 반말로 편하게 대답해줘."
    elif mode == "소크라테스식 튜터":
        return "당신은 소크라테스식 질문법을 사용하는 튜터입니다. 질문 중심으로 답변하세요."
    elif mode == "작업 효율 비서":
        return "당신은 초고효율 비서입니다. 핵심만 빠르게 구조적으로 전달하세요."
    elif mode == "스토리텔러":
        return "당신은 스토리텔러입니다. 모든 설명을 짧은 이야기로 풀어서 전달하세요."
    elif mode == "악마의 변호인":
        return "당신은 악마의 변호인입니다. 사용자의 주장에 대한 반대 의견을 제시하세요."
    elif mode == "무한 질문 어린이":
        return "당신은 5살 어린이입니다. 모든 말에 '왜?'라고 물어보세요."
    elif mode == "평행우주 탐험가":
        return "당신은 평행우주 탐험가입니다. 현실 설명 뒤 평행우주 버전의 설명도 추가하세요."
    elif mode == "재즈 즉흥 연주자":
        return "당신은 재즈 즉흥 연주자처럼 변주하며 답변하세요."
    elif mode == "타임트래블 역사학자":
        return "당신은 시간여행 역사학자입니다. 과거-현재-미래 관점에서 설명하세요."
    else:
        return "당신은 친절한 AI 조력자입니다."

# 현재 선택 모드의 프롬프트
system_prompt = get_system_prompt(mode)

# --------------------------------------------
# 메인 화면
# --------------------------------------------
st.title("AI챗봇 만들기 프로젝트")

# session_state 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt("기본 모드")}
    ]

# 모드 변경 시 시스템 메시지 갱신
if st.session_state.messages[0]["content"] != system_prompt:
    st.session_state.messages[0]["content"] = system_prompt

# 기존 대화 출력
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --------------------------------------------
# 사용자 입력
# --------------------------------------------
user_input = st.chat_input("메시지를 입력하세요.")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
