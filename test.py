from collections import Counter
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

# 사용자 입력 처리
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


# ✅ [분석 기능] 사용자 입력 메시지 유형 분류 함수
def classify_issue(text):
    categories = {
        "안전 문제": ["사고", "위험", "안전", "보호구", "경고"],
        "장비 문제": ["장비", "기계", "작동", "오류", "점검"],
        "작업 절차 문제": ["절차", "규정", "허가", "승인", "검토"],
        "환경 문제": ["소음", "먼지", "환경", "배출", "폐기물"],
        "기타": []  # 미분류 항목
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "기타"

# ✅ [분석 기능] 사용자의 입력만 추출하여 분류 및 통계 생성
def analyze_issues():
    user_messages = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    issue_counts = Counter(classify_issue(msg) for msg in user_messages)
    return issue_counts


# ✅ [분석 버튼] 누르면 통계를 화면에 표시
if st.button("🔍 문제 분석하기"):
    issue_stats = analyze_issues()

    st.subheader("📊 문제 분석 결과")
    for category, count in issue_stats.items():
        st.write(f"- **{category}**: {count}건")

    # 차트 표시
    st.bar_chart(issue_stats)