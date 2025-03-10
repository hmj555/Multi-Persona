from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
from datetime import datetime
logging.langsmith("Persona")
import json
import os

## 라이브러리 불러오기
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


## ✅ 세션 저장소
store = {}  # 세션별 데이터 저장소


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

    # ✅ 페르소나 & 토픽 불러오기 (세션 내에서 최초 한 번만 실행)
    if store[session_id]["persona"] is None:
        persona_filepath = f"User_info/{user_number}.json"
        if not os.path.exists(persona_filepath):
            raise FileNotFoundError(f"❌ {persona_filepath} 파일을 찾을 수 없습니다.")
        with open(persona_filepath, "r", encoding="utf-8") as f:
            user_persona = json.load(f)

        persona_description = (
            f"{user_persona['Age']}세 {user_persona['Gender']}, {user_persona['Job']}, "
            f"{user_persona['Major']}을 전공하였고 MBTI는 {user_persona['MBTI']}이다.\n"
            f"내가 생각하는 나는 {user_persona['Self_tag']}와 같은 성격을 가졌다."
        )
        store[session_id]["persona"] = persona_description

    if store[session_id]["topic"] is None:
        topic_filepath = f"User_Topics/{user_number}.json"
        if not os.path.exists(topic_filepath):
            raise FileNotFoundError(f"❌ {topic_filepath} 파일을 찾을 수 없습니다.")
        with open(topic_filepath, "r", encoding="utf-8") as f:
            topics_data = json.load(f)

        session_number = int(session_id.split("/")[-1])
        tag_topics = topics_data.get("tag_topics", [])
        tag_topic_descriptions = topics_data.get("tag_topic_descriptions", [])
        
        store[session_id]["topic"] = tag_topics[session_number - 1] if 0 <= (session_number - 1) < len(tag_topics) else "자유 주제"

        # ✅ topic_description 불러오기 (자유 주제 제외)
        if store[session_id]["topic"] != "자유 주제":
            store[session_id]["topic_description"] = tag_topic_descriptions[session_number - 1] if 0 <= (session_number - 1) < len(tag_topic_descriptions) else None
        else:
            store[session_id]["topic_description"] = None  # 자유 주제일 경우 설명 없음

    # ✅ 프롬프트 생성 (세션 내에서 최초 한 번만 실행)
    if store[session_id]["prompt"] is None:
        persona_description, topic, topic_description = store[session_id]["persona"], store[session_id]["topic"], store[session_id]["topic_description"]
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
                    Have a conversation about << {topic_text} >> based on the persona provided.
                    Try to stay on topic.
                    Speak casually and use “I” when referring to yourself and “you” when addressing the user.
                    Avoid honorifics or formal speech.
                    Always respond in Korean.
                    """
                ),
                MessagesPlaceholder(variable_name="history"),  # ✅ history 변수를 반드시 전달
                ("human", "{input}"),
            ]
        )

    # ✅ LLM 실행체 생성 (세션 내에서 최초 한 번만 실행)
    if store[session_id]["llm"] is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        store[session_id]["llm"] = store[session_id]["prompt"] | llm  # ✅ 실행체 저장


## ✅ 대화 실행 함수 (미리 생성한 LLM 실행체 사용)
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
        store[session_id]["llm"],  # ✅ 기존 LLM 실행체 사용
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # ✅ LLM 실행
    response = chatbot_with_history.invoke(
        {
            "input": input_text,
            "history": chat_history  # ✅ 기존 대화 이력 추가
        },
        config={"configurable": {"session_id": session_id}}
    )

    # ✅ 대화가 끝난 후 자동으로 로그 저장
    save_chat_log(user_number, session_id)

    return response.content


## ✅ 대화 로그 저장 함수
def save_chat_log(user_number, session_id):
    """store에 저장된 대화 이력을 JSON 파일로 저장"""  
    chat_history = store.get(session_id, {}).get("history", ChatMessageHistory()).messages
    session_number = int(session_id.split("/")[-1])

    save_dir = f"User_ChatLog/{user_number}_Tag"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{session_number}.json")

    chat_log = []
    for msg in chat_history:
        chat_log.append({
            "session_id": session_id,
            "persona": "tag",
            "topic": store[session_id]["topic"],
            "role": "user" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content,
            "timestamp": getattr(msg, "timestamp", datetime.now().isoformat())
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_log, f, ensure_ascii=False, indent=4)

    print(f"✅ 대화 이력이 저장되었습니다: {file_path}")


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
#     response2 = chat(user_number, user_input2, session_id)
#     print("💬 [AI 응답]:", response2)
