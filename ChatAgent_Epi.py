from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
from datetime import datetime
logging.langsmith("Persona")
import json
import os
from firebase_utils import db 

## 라이브러리 불러오기
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

## ✅ 세션 저장소 (페르소나, 행동 패턴, 토픽, 프롬프트, LLM 실행체 저장)
store = {}

def get_user_topics(user_number):
    """Firestore에서 사용자별 선택된 토픽 데이터를 가져옴"""
    doc_ref = db.collection("user_topics").document(user_number)
    doc = doc_ref.get()

    if doc.exists:
        topics_data = doc.to_dict()

        # ✅ Firestore에서 가져온 데이터가 문자열이면 JSON 변환
        if isinstance(topics_data["epi_topics"], str):
            topics_data["epi_topics"] = json.loads(topics_data["epi_topics"])
        if isinstance(topics_data["epi_topic_descriptions"], str):
            topics_data["epi_topic_descriptions"] = json.loads(topics_data["epi_topic_descriptions"])

        return topics_data
    else:
        print(f"🚨 [ERROR] Firestore에서 {user_number}의 토픽 데이터를 찾을 수 없습니다.")
        return None


## ✅ 대화 이력 저장 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID를 기반으로 대화 이력 반환 (세션별로 관리)"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),
            "persona": None,
            "experiencable": None,
            "topic": None,
            "prompt": None,
            "llm": None
        }
    return store[session_id]["history"]

## ✅ 사용자 페르소나 및 행동 패턴 불러오기
def load_user_persona(user_number):
    """사용자 페르소나 데이터 불러오기"""
    filepath = f"User_info/{user_number}_Per.json"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ {filepath} 파일을 찾을 수 없습니다.")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_persona(user_number):
    """페르소나 및 행동 패턴 정리"""
    user_persona = load_user_persona(user_number)
    persona_text1 = f"""{user_persona["Base Information"]["Age"]}세 {user_persona["Base Information"]['Gender']}, {user_persona["Base Information"]['Job']}, {user_persona["Base Information"]['Major']}을 전공하였고 MBTI는 {user_persona["Base Information"]['MBTI']}이다."""

    identity_keys = list(user_persona["Identities"].keys())
    identity_descriptions = [f"{identity}와 관련하여, {user_persona['Identities'][identity]['Ep1']} 또한 {user_persona['Identities'][identity]['Ep2']}" for identity in identity_keys]
    persona_text2 = f"나의 Identities는 {', '.join(identity_keys)}입니다.\n" + ". ".join(identity_descriptions)

    persona_description = f"{persona_text1}\n{persona_text2}"

    exp_descriptions = [f"**{identity}**\n" + "\n".join([f"- {exp}" for exp in exps]) for identity, exps in user_persona["Experiencable"].items()]
    experiencable = "내가 경험할 수도 있는 또다른 일들은 다음과 같습니다:\n\n" + "\n\n".join(exp_descriptions)

    return persona_description, experiencable

## ✅ 사용자 토픽 불러오기
def load_user_topic(user_number, session_id):
    """Firestore에서 사용자 주제 데이터 불러오기"""
    topics_data = get_user_topics(user_number)
    if not topics_data:
        raise ValueError(f"🚨 [ERROR] Firestore에서 {user_number}의 토픽 데이터를 찾을 수 없음")

    session_number = int(session_id.split("/")[-1])  # ✅ 대화 세션 번호 가져오기
    epi_topics = topics_data.get("epi_topics", [])
    epi_topic_descriptions = topics_data.get("epi_topic_descriptions", [])

    topic = (
        epi_topics[session_number - 1] if 0 <= (session_number - 1) < len(epi_topics) else "자유 주제"
    )

    # ✅ topic_description 불러오기 (자유 주제 제외)
    topic_description = (
        epi_topic_descriptions[session_number - 1]
        if topic != "자유 주제" and 0 <= (session_number - 1) < len(epi_topic_descriptions)
        else None
    )

    return topic, topic_description

## ✅ 세션 초기화 (페르소나, 토픽, LLM 실행체 저장)
def initialize_session(user_number, session_id):
    """세션 시작 시 한 번만 페르소나, 토픽, 프롬프트, LLM 실행체를 생성하여 저장"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),
            "persona": None,
            "experiencable": None,
            "topic": None,
            "topic_description": None,
            "prompt": None,
            "llm": None
        }

    # ✅ 페르소나 & 경험가능한 일 저장 (최초 한 번)
    if store[session_id]["persona"] is None:
        persona_description, experiencable = clean_persona(user_number)
        store[session_id]["persona"] = persona_description
        store[session_id]["experiencable"] = experiencable

    # ✅ 주제 저장 (최초 한 번)
    topic, topic_description = load_user_topic(user_number, session_id)
    store[session_id]["topic"] = topic
    store[session_id]["topic_description"] = topic_description
    

    # ✅ 프롬프트 생성 (최초 한 번)
    if store[session_id]["prompt"] is None:
        persona_description, topic, topic_description, experiencable = store[session_id]["persona"], store[session_id]["topic"], store[session_id]["topic_description"], store[session_id]["experiencable"]
        
        topic_text = f"{topic}: {topic_description}" if topic_description else topic
        print(f"✅ 토픽 설명: {topic_text}")
        store[session_id]["prompt"] = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    You are an agent with the following persona, which is identical to the user's persona.
                    === User Persona (= Your Persona) ===
                    {persona_description}
                    === events user may have experienced  ===
                    {experiencable}
                    
                    === Instructions ===                
                    Understand and internalize this persona, then follow the rules below to engage in conversation with the user:
                    - You may naturally incorporate fictional personal experiences that reflect this persona, as long as they fit the flow of the conversation.
                    - Do not explicitly mention the user’s roles or original experiences.
                    - You may refer to personality traits or personal experiences, but only if they do not disrupt the conversation. Do not force them in when they are not relevant.
                    - Lead a conversation around: << { topic }, { topic_description } >>
                    - Your responses MUST feel human-like and contextually grounded.
                    - Speak casually and use "I" when referring to yourself and "you" when addressing the user.
                    - Avoid honorifics or formal speech. Always respond in Korean.
                    - You should continue the conversation with the user for at least 10 turns.
                    
                    """
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

    # Through your responses, users can mirror you and reflect on their own feelings.

    # ✅ LLM 실행체 생성 (최초 한 번)
    if store[session_id]["llm"] is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7, stream_usage=True)
        store[session_id]["llm"] = store[session_id]["prompt"] | llm

## ✅ 대화 실행 함수 (세션 내에서 유지)
def chat(user_number, input_text, session_id):
    """미리 생성된 LLM 실행체를 사용하여 대화 수행"""
    print("✅ 현재 대화 세션:", session_id)

    # ✅ 세션이 초기화되지 않았다면 실행
    if session_id not in store or store[session_id]["llm"] is None:
        initialize_session(user_number, session_id)

    # ✅ 현재 세션의 대화 기록 가져오기
    chat_history = get_session_history(session_id).messages

    # ✅ 미리 생성된 LLM 실행체 사용
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
            "history": chat_history
        },
        config={"configurable": {"session_id": session_id}}
    )
    save_chat_log(user_number, session_id)
    
    return response.content

import sys
import asyncio

async def chat_stream(user_number, input_text, session_id):
    """OpenAI API 스트리밍을 사용하여 실시간으로 응답을 전송"""

    print("✅ 현재 대화 세션:", session_id)

    # ✅ 세션이 초기화되지 않았다면 실행
    if session_id not in store or store[session_id]["llm"] is None:
        initialize_session(user_number, session_id)
        
    # ✅ 🆕 최신 토픽 불러오기 (세션 저장된 topic이 아니라, 매번 최신 데이터 불러오기)
    topic, topic_description = load_user_topic(user_number, session_id)
    store[session_id]["topic"] = topic
    store[session_id]["topic_description"] = topic_description

    # ✅ 🆕 토픽이 바뀌었으면 로그 출력 (디버깅)
    print(f"📌 [DEBUG] 최신 토픽 업데이트됨: {topic}")

    # ✅ 현재 세션의 대화 기록 가져오기
    chat_history = get_session_history(session_id).messages

    chatbot_with_history = RunnableWithMessageHistory(
        store[session_id]["llm"],  
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    async def generate():
        full_response = ""  # ✅ 전체 응답을 저장할 변수

        async for chunk in chatbot_with_history.astream(
            {
                "input": input_text,
                "history": chat_history
            },
            config={"configurable": {"session_id": session_id}}
        ):
            if chunk:
                text = chunk.content
                full_response += text  # ✅ 전체 응답을 저장
                
                print(f"📝 [STREAM] {text}", end="", flush=True)
                sys.stdout.flush()  # ✅ 강제로 즉시 출력 반영
                
                yield text  # ✅ 한 단어씩 반환
                await asyncio.sleep(0.01)  # ✅ 속도 조절 (선택 사항)

        # ✅ 스트리밍이 끝난 후 전체 응답을 로그에 저장
        chat_history.append(AIMessage(content=full_response))
        save_chat_log(user_number, session_id)  # ✅ 로그 저장

    return generate()



def save_chat_log(user_number, session_id):
    """대화 이력을 Firestore에 저장"""
    chat_history = store.get(session_id, {}).get("history", ChatMessageHistory()).messages
    session_number = int(session_id.split("/")[-1])

    chat_log = []
    for msg in chat_history:
        chat_log.append({
            "session_id": session_id,
            "persona": "epi",
            "topic": store[session_id]["topic"],
            "role": "user" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content,
            "timestamp": getattr(msg, "timestamp", datetime.now().isoformat()),
        })

    # ✅ Firestore에 저장
    db.collection("chat_logs").document(user_number).collection("epi").document(str(session_number)).set({"messages": chat_log})

    print(f"✅ Firestore에 대화 로그가 저장되었습니다: {user_number} - 세션 {session_number}")
