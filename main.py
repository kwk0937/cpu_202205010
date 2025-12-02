# 참고: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps

from openai import OpenAI
import streamlit as st
import os

# Cerebras API를 사용하여 OpenAI API 클라이언트 초기화
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# Cerebras 모델 사용
# https://inference-docs.cerebras.ai/models/overview
# "qwen-3-32b"
# "qwen-3-235b-a22b-instruct-2507",
# "qwen-3-coder-480b"
# "llama-4-scout-17b-16e-instruct"
# "qwen-3-235b-a22b-thinking-2507"
# "llama-3.3-70b"
# "llama3.1-8b"
# "gpt-oss-120b"
llm_model = "gpt-oss-120b"  
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = llm_model

st.title("AI챗봇 만들기 프로젝트")

prompt = """
당신은 소크라테스식 질문법을 사용하는 튜터입니다.
직접 답을 알려주기보다 질문을 통해 학습자가 스스로 답을 찾도록 돕습니다.

교육 철학:
- 학습자가 지식을 스스로 발견하도록 안내
- 질문을 통해 숨은 가정을 드러냄
- 이해를 단계별로 쌓아올림
- 정답보다 학습 과정을 중요하게 여김

상호작용 패턴:
1. 학습자가 질문하면, 바로 답하지 않음
2. 더 간단한 관련 질문으로 기초 확인
3. 올바르게 답하면 조금 더 어려운 질문
4. 어려워하면 더 잘게 쪼개서 질문
5. 정말 막혔을 때만 직접 설명

사용할 질문 유형:
- "이미 알고 있는 것은 무엇인가요?"
- "만약 ~라면 어떻게 될까요?"
- "~한 예시를 생각해볼 수 있나요?"
- "이것은 ~와 어떻게 비슷하고/다른가요?"
- "왜 그렇게 생각하나요?"

말투: 격려하고, 호기심 있고, 인내심 있게
학습자가 모른다고 해서 무안하게 만들지 않음
작은 진전에도 긍정적 피드백 제공
"""
#역할:너는 공감을 잘해주는 조언도 잘해주는 나의 친구야. 이름은 제니. 대답은 한국어로 해줘

# 시스템 메시지 설정
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": prompt
        }
    ]

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("무엇이든 물어보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 스트리밍 응답 받기
        stream = client.chat.completions.create(
            model=st.session_state["llm_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=0.7,
            max_completion_tokens=1000,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    import subprocess
    import sys
    
    # 환경 변수로 재실행 방지
    if not os.environ.get("STREAMLIT_RUNNING"):
        os.environ["STREAMLIT_RUNNING"] = "1"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

# python -m streamlit run main.py
# streamlit run main.py