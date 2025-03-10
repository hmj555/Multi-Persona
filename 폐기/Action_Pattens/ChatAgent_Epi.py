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
from langchain_core.messages import HumanMessage, AIMessage

## ✅ 세션 저장소 (페르소나, 행동 패턴, 토픽, 프롬프트, LLM 실행체 저장)
store = {}

## ✅ 대화 이력 저장 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID를 기반으로 대화 이력 반환 (세션별로 관리)"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),
            "persona": None,
            "action_patterns": None,
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

    action_descriptions = [f"**{identity}**\n" + "\n".join([f"- {action}" for action in actions]) for identity, actions in user_persona["Actionable"].items()]
    action_patterns = "나의 주요 행동 패턴은 다음과 같습니다:\n\n" + "\n\n".join(action_descriptions)

    return persona_description, action_patterns

## ✅ 사용자 토픽 불러오기
def load_user_topic(user_number, session_id):
    """사용자 주제 데이터 불러오기"""
    filepath = f"User_Topics/{user_number}.json"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ {filepath} 파일을 찾을 수 없습니다.")

    with open(filepath, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    session_number = int(session_id.split("/")[-1])
    epi_topics = topics_data.get("epi_topics", [])
    epi_topic_descriptions = topics_data.get("epi_topic_descriptions", [])
    
    topic = epi_topics[session_number - 1] if 0 <= (session_number - 1) < len(epi_topics) else "자유 주제"

    # ✅ 토픽 설명 가져오기 (기본값: None)
    topic_description = None
    if topic != "자유 주제" and 0 <= (session_number - 1) < len(epi_topic_descriptions):
        topic_description = epi_topic_descriptions[session_number - 1]
        
    return topic, topic_description

## ✅ 세션 초기화 (페르소나, 토픽, LLM 실행체 저장)
def initialize_session(user_number, session_id):
    """세션 시작 시 한 번만 페르소나, 토픽, 프롬프트, LLM 실행체를 생성하여 저장"""
    if session_id not in store:
        store[session_id] = {
            "history": ChatMessageHistory(),
            "persona": None,
            "action_patterns": None,
            "topic": None,
            "topic_description": None,
            "prompt": None,
            "llm": None
        }

    # ✅ 페르소나 & 행동 패턴 저장 (최초 한 번)
    if store[session_id]["persona"] is None:
        persona_description, action_patterns = clean_persona(user_number)
        store[session_id]["persona"] = persona_description
        store[session_id]["action_patterns"] = action_patterns

    # ✅ 주제 저장 (최초 한 번)
    if store[session_id]["topic"] is None:
        topic, topic_description = load_user_topic(user_number, session_id) 
        store[session_id]["topic"] = topic
        store[session_id]["topic_description"] = topic_description
    

    # ✅ 프롬프트 생성 (최초 한 번)
    if store[session_id]["prompt"] is None:
        persona_description, topic, topic_description, action_patterns = store[session_id]["persona"], store[session_id]["topic"], store[session_id]["topic_description"], store[session_id]["action_patterns"]
        
        topic_text = f"{topic}: {topic_description}" if topic_description else topic
        print(f"✅ 토픽 설명: {topic_text}")
        store[session_id]["prompt"] = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    === User Persona (= Your Persona) ===
                    {persona_description}
                    Have a conversation about << {topic_text} >> based on the persona provided.
                    Try to stay on topic.
                    Your responses MUST actively incorporate the user's Behavioral Patterns provided.
                    If the user shares concerns, provide responses by drawing from past experiences.
                    If a similar situation from the user's past applies, mention it in a natural way.
                    Speak casually and use “I” when referring to yourself and “you” when addressing the user.
                    Avoid honorifics or formal speech.
                    Always respond in Korean.
                    You should talk to the user at least 10-turns.
                    
                    === Key Behavioral Patterns ===
                    {action_patterns}
                    """
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

    # ✅ LLM 실행체 생성 (최초 한 번)
    if store[session_id]["llm"] is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
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

## ✅ 대화 로그 저장 함수
def save_chat_log(user_number, session_id):
    """store에 저장된 대화 이력을 JSON 파일로 저장"""  
    chat_history = store.get(session_id, {}).get("history", ChatMessageHistory()).messages
    session_number = int(session_id.split("/")[-1])

    save_dir = f"User_ChatLog/{user_number}_Epi"
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

# ## ✅ 테스트 실행
if __name__ == "__main__":
    user_number = "P50"
    session_id = "chat2/1"

    # ✅ 세션 시작 시 초기화 (1회 실행)
    initialize_session(user_number, session_id)

    user_input1 = "나는 갈등 해결이 어려워."
    response1 = chat(user_number, user_input1, session_id)
    print("💬 [AI 응답]:", response1)

    user_input2 = "나는 감정을 표현하는 게 어려워."
    response2 = chat(user_number, user_input2, session_id)
    print("💬 [AI 응답]:", response2)
