from datetime import datetime
import os
from openai import OpenAI
import streamlit as st

st.title("현장에 문제점을 알려주세요")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

system_message = '''
너의 공사현장 안전 전문가의 어시스턴트임.
항상 존댓말로 공손하고 친근하게 대답해.
영어로 질문을 받아도 무조건 한글로 답변해줘.
한글이 아닌 답변일 때는 다시 생각해서 꼭 한글로 만들어줘.
user 메세지에서 정확하지 않으면 언제 어디서 어떤 문제가 발생 한것인지 다시 물어봐야함.
정확한 답변이 아니면 답하지 말고 '일단 상부 보고부터 한다' 해.
그리고 항상 답변은 문제를 취합해서 신속하게 전달하도록 하겠습니다.라고 해줘.
'''

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": system_message}]

for idx, message in enumerate(st.session_state.messages):
    if idx > 0:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],  # type: ignore
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})  # type: ignore

    # 채팅 내용을 파일로 저장하는 함수 실행
    def save_chat_to_file():
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_date}_chatlog.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for msg in st.session_state.messages:
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n\n")
        return filename

    filename = save_chat_to_file()

    # 파일 다운로드 버튼 제공
    with open(filename, "rb") as f:
        st.download_button(
            label="채팅 내용 다운로드",
            data=f,
            file_name=filename,
            mime="text/plain"
        )