from openai import OpenAI
import streamlit as st

st.title("현장에 문제점을 알려주세요")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

system_message = '''
너의 공사현장 안전 전문가의 어시스턴트야.
항상 존뎃로 공손고 친근하게 대답해줘.
영어로 질문을 받아도 무조건 한글로 답변해줘.
한글이 아닌 답변일 때는 다시 생각해서 꼭 한글로 만들어줘.
user 메세지에서 정확하지 않는 육하원칙에 입각하여 물어보고.
정확한 답변이 아니면 답하지 말 '일단 상부 보고 부터한다' 해. 
그리고 항상 답변은 문제를 취합해서 신속하게 전달 하도록 하겠습니다.라고해줘.
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
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ], # type: ignore
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response}) # type: ignore
