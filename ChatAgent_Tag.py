from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
from datetime import datetime
import json
import os
import asyncio
import sys
from firebase_utils import db  # ✅ Firestore 연결

## 라이브러리 불러오기
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

## ✅ 세션 저장소
store = {}  # 세션별 데이터 저장소

## ✅ Firestore에서 사용자 토픽 불러오기
def get_user_topics(user_number):
    """Firestore에서 사용자별 선택된 토픽 데이터를 가져옴"""
    doc_ref = db.collection("user_topics").document(user_number)
    doc = doc_ref.get()

    if doc.exists:
        topics_data = doc.to_dict()
        
        # ✅ Firestore에서 가져온 데이터가 문자열이면 JSON 변환
        if isinstance(topics_data["tag_topics"], str):
            topics_data["tag_topics"] = json.loads(topics_data["tag_topics"])
        if isinstance(topics_data["tag_topic_descriptions"], str):
            topics_data["tag_topic_descriptions"] = json.loads(topics_data["tag_topic_descriptions"])

        return topics_data
    else:
        print(f"🚨 [ERROR] Firestore에서 {user_number}의 토픽 데이터를 찾을 수 없습니다.")
        return None

## ✅ 사용자 페르소나 및 행동 패턴 불러오기
def load_user_persona(user_number):
    """사용자 페르소나 데이터 불러오기"""
    filepath = f"User_info/{user_number}.json"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ {filepath} 파일을 찾을 수 없습니다.")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_persona(user_number):
    """페르소나 및 행동 패턴 정리"""
    user_persona = load_user_persona(user_number)
    persona_text1 = f"""{user_persona["Age"]}세 {user_persona['Gender']}, {user_persona['Job']}, {user_persona['Major']}을 전공하였고 MBTI는 {user_persona['MBTI']}이다."""
    persona_text2 = f"""나는 {user_persona["Self-tag"]}와 같은 성격을 가졌다."""
    persona = f"{persona_text1}\n{persona_text2}"
    return persona


## ✅ 사용자 데이터 (페르소나 & 토픽) + LLM 실행체까지 미리 저장
def initialize_session(user_number, session_id):
    """세션 시작 시 한 번만 페르소나, 토픽, 프롬프트, LLM 실행체를 생성하여 저장"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),
            "persona": None,
            "topic": None,
            "topic_description": None,
            "prompt": None,
            "llm": None
        }

    # ✅ Firestore에서 토픽 불러오기
    topics_data = get_user_topics(user_number)
    if not topics_data:
        raise ValueError(f"🚨 [ERROR] Firestore에서 {user_number}의 토픽 데이터를 찾을 수 없음")

    session_number = int(session_id.split("/")[-1])  # ✅ 대화 세션 번호 가져오기
    tag_topics = topics_data.get("tag_topics", [])
    tag_topic_descriptions = topics_data.get("tag_topic_descriptions", [])

    store[session_id]["topic"] = (
        tag_topics[session_number - 1] if 0 <= (session_number - 1) < len(tag_topics) else "자유 주제"
    )

    # ✅ topic_description 불러오기 (자유 주제 제외)
    if store[session_id]["topic"] != "자유 주제":
        store[session_id]["topic_description"] = (
            tag_topic_descriptions[session_number - 1]
            if 0 <= (session_number - 1) < len(tag_topic_descriptions)
            else None
        )
    else:
        store[session_id]["topic_description"] = None  # 자유 주제일 경우 설명 없음
        
    
    # ✅ 페르소나 불러오기 (여기 추가!)
    if store[session_id]["persona"] is None:
        persona_description = clean_persona(user_number)
        store[session_id]["persona"] = persona_description  # ✅ 페르소나 저장

    # ✅ 프롬프트 생성 (세션 내에서 최초 한 번만 실행)
    if store[session_id]["prompt"] is None:
        persona_description, topic, topic_description = (
            store[session_id]["persona"],
            store[session_id]["topic"],
            store[session_id]["topic_description"],
        )
        topic_text = f"{topic}: {topic_description}" if topic_description else topic
        print(f"✅ 토픽 설명: {topic_text}")
        store[session_id]["prompt"] = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    === User Persona (= Your Persona) ===
                    {persona_description}
                    === Instructions ===
                    Construct a personality that embodies the given persona's characteristics.
                    ⭐️ Lead a conversation around a << {topic_text} >>
                    Your responses MUST feel human-like and contextually grounded
    
                    Speak casually and use “I” when referring to yourself and “you” when addressing the user.
                    Avoid honorifics or formal speech.
                    Always respond in Korean.
                    You should talk to the user at least 10-turns.
                    """
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

    #  🟢 DO NOT give generic advice without sharing a relevant personal experience. Ensure that your responses reflect the persona’s perspective and personal values.

    # ✅ LLM 실행체 생성 (세션 내에서 최초 한 번만 실행)
    if store[session_id]["llm"] is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7, stream_usage=True)
        store[session_id]["llm"] = store[session_id]["prompt"] | llm  # ✅ 실행체 저장


## ✅ 대화 실행 함수
def chat(user_number, input_text, session_id):
    """미리 생성된 LLM 실행체를 사용하여 대화 수행"""
    print("✅ 현재 대화 세션:", session_id)

    # ✅ 세션이 초기화되지 않았다면 실행
    if session_id not in store or store[session_id]["llm"] is None:
        initialize_session(user_number, session_id)

    # ✅ 최신 토픽 불러오기
    topic = store[session_id]["topic"]
    topic_description = store[session_id]["topic_description"]
    topic_text = f"{topic}: {topic_description}" if topic_description else topic
    print(f"📌 [DEBUG] 최신 토픽 업데이트됨: {topic_text}")

    # ✅ 현재 세션의 대화 기록 가져오기
    chat_history = get_session_history(session_id).messages

    chatbot_with_history = RunnableWithMessageHistory(
        store[session_id]["llm"],
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # ✅ LLM 실행
    response = chatbot_with_history.invoke(
        {
            "input": input_text,
            "history": chat_history,
        },
        config={"configurable": {"session_id": session_id}},
    )

    # ✅ 대화가 끝난 후 자동으로 로그 저장
    save_chat_log(user_number, session_id)

    return response.content


## ✅ Firestore에 대화 로그 저장
def save_chat_log(user_number, session_id):
    """대화 이력을 Firestore에 저장"""
    chat_history = store.get(session_id, {}).get("history", ChatMessageHistory()).messages
    session_number = int(session_id.split("/")[-1])

    chat_log = []
    for msg in chat_history:
        chat_log.append({
            "session_id": session_id,
            "persona": "tag",
            "topic": store[session_id]["topic"],
            "role": "user" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content,
            "timestamp": getattr(msg, "timestamp", datetime.now().isoformat()),
        })

    # ✅ Firestore에 저장
    db.collection("chat_logs").document(user_number).collection("tag").document(str(session_number)).set({"messages": chat_log})

    print(f"✅ Firestore에 대화 로그가 저장되었습니다: {user_number} - 세션 {session_number}")


## ✅ 비동기 스트리밍 대화
async def chat_stream(user_number, input_text, session_id):
    """OpenAI API 스트리밍을 사용하여 실시간으로 응답을 전송"""
    print("✅ 현재 대화 세션:", session_id)

    # ✅ 세션이 초기화되지 않았다면 실행
    if session_id not in store or store[session_id]["llm"] is None:
        initialize_session(user_number, session_id)

    chat_history = get_session_history(session_id).messages

    async def generate():
        async for chunk in chatbot_with_history.astream({"input": input_text, "history": chat_history}):
            if chunk:
                yield chunk.content
                await asyncio.sleep(0.01)

    return generate()

## ✅ 대화 이력 저장 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID를 기반으로 대화 이력 반환 (세션별로 관리)"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),  # 대화 이력 저장
            "persona": None,  # 페르소나 저장
            "topic": None,  # 토픽 저장
            "prompt": None,  # 프롬프트 저장
            "llm": None  # ✅ LLM 실행체 저장
        }
    return store[session_id]["history"]  # 해당 세션의 대화 기록 반환



## ✅ 테스트 실행 (세션 유지 확인)
# if __name__ == "__main__":
#     user_number = "P50"
#     session_id = "chat1/1"

#     # ✅ 세션 시작 시 초기화 (1회 실행)
#     initialize_session(user_number, session_id)

#     user_input1 = "안녕 네 소개를 해줄래?"
#     response1 = chat(user_number, user_input1, session_id)
#     print("💬 [AI 응답]:", response1)

#     user_input2 = "요즘 재정적 스트레스가 심한데 어떻게 해야 할까?"
#     response2 = chat_stream(user_number, user_input1, session_id)
#     print("💬 [AI 응답]:", response2)

