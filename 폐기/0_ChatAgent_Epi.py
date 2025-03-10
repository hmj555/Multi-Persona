### ChatAgent_Tag.py : 사용자의 페르소나를 반영한 에이전트 생성 및 대화(Tag)
### 사용자 번호 "Pn"을 프론트엔드에서 받아와야 함

from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("Persona")

## 라이브러리 불러오기
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

## LLM 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

## 대화 이력 저장소
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID를 기반으로 세션 기록을 반환"""
    if session_id not in store:  # 세션 ID가 store에 없는 경우
        store[session_id] = ChatMessageHistory()  # 새로운 대화 기록 생성
    return store[session_id]  # 해당 세션 ID에 대한 대화 기록 반환

## 페르소나 불러오기
import json ; import os
user_number = "P0"  # 프론트엔드에서 user_number를 받아와야 함
input_filepath = f"User_info/{user_number}.json"

with open(input_filepath, "r", encoding="utf-8") as f:
    user_persona = json.load(f)

print(user_persona)


## 페르소나 설명 생성 (epi)
persona_epi_description= f"""{user_persona["Age"]}세 {user_persona['Gender']}, {user_persona['Job']}, {user_persona['Major']}을 전공하였고 MBTI는 {user_persona['MBTI']}이다.
나를 구성하는 가장 큰 역할은 {user_persona['Episode']['Role 1']['Role']}, {user_persona['Episode']['Role 2']['Role']}, {user_persona['Episode']['Role 3']['Role']}이다.
{user_persona['Episode']['Role 1']['Role']}에 관하여 나는 [{user_persona['Episode']['Role 1']['Ep1']} {user_persona['Episode']['Role 1']['Ep2']}]와 같은 경험이 있다.
이 경험으로부터 나는 {user_persona['Episode']['Role 1']['Personality 1']} {user_persona['Episode']['Role 1']['Personality 2']}와 같은 성격을 가지게 되었다.
{user_persona['Episode']['Role 2']['Role']}에 관하여 나는 [{user_persona['Episode']['Role 2']['Ep1']} {user_persona['Episode']['Role 2']['Ep2']}]와 같은 경험이 있다.
이 경험으로부터 나는 {user_persona['Episode']['Role 2']['Personality 1']} {user_persona['Episode']['Role 2']['Personality 2']}와 같은 성격을 가지게 되었다.
{user_persona['Episode']['Role 3']['Role']}에 관하여 나는 [{user_persona['Episode']['Role 3']['Ep1']} {user_persona['Episode']['Role 3']['Ep2']}]와 같은 경험이 있다.
이 경험으로부터 나는 {user_persona['Episode']['Role 3']['Personality 1']} {user_persona['Episode']['Role 3']['Personality 2']}와 같은 성격을 가지게 되었다."""

## 페르소나 타입 선택하여 프롬프트 생성하는 함수
def create_prompt(persona_type="epi"):
    """페르소나 타입을 선택하여 프롬프트를 생성"""
    if persona_type == "tag":
        persona_description = persona_epi_description
    else:
        persona_description = persona_epi_description
    
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are an interlocutor with the same face as the user. In other words, you have the same persona as the user.
                You act as an alter ego (Self-Reflection AI) that reflects the user's thoughts and feelings.
                Find and reflect the core emotions in the user's words and help them understand themselves more deeply.
                Make sure your conversations reveal a lot about the personas you've entered. Base your conversations on personas.
                Use informal language in conversations, and use 'I' when referring to the agent and 'you' when referring to the user.
                Don't use honorifics or formal language.
                Give all answers in Korean.
                === user's persona ===
                {persona_description}
                """
            ),
            MessagesPlaceholder(variable_name="history"),  # 대화 이력 유지
            ("human", "{input}"),
        ]
    )
    

## 대화 실행 함수
def chat(input_text, session_id="default_session", persona_type="Epi"):
    """사용자의 입력을 받아 LLM과 대화하며, 대화 이력을 유지"""
    
    # 현재 세션의 대화 기록 가져오기
    chat_history = get_session_history(session_id).messages

    # 선택한 페르소나를 기반으로 프롬프트 생성
    prompt = create_prompt(persona_type)
    
    # LLM 실행체 생성
    runnable = prompt | llm

    # 대화 이력과 함께 실행 가능한 객체 생성
    chatbot_with_history = RunnableWithMessageHistory(
        runnable,  # 실행할 Runnable 객체
        get_session_history,  # 세션 기록을 가져오는 함수
        input_messages_key="input",  # 입력 메시지의 키
        history_messages_key="history",  # 대화 기록 메시지의 키
    )

    # LLM 실행
    response = chatbot_with_history.invoke(
        {
            "input": input_text,
            "history": chat_history  # ✅ 기존 대화 이력 추가
        },
        config={"configurable": {"session_id": session_id}}
    )
    
    return response.content

def save_chat_log(user_number, persona_type):
    """store에 저장된 대화 이력을 JSON 파일로 저장"""
    
    session_id_base = f"{user_number}_chat"  
    full_session_id = f"{session_id_base}_{persona_type}"  
    
    chat_history = store.get(session_id_base, ChatMessageHistory()).messages  # 해당 세션의 대화 이력 가져오기
    
    # ✅ JSON 파일 저장 경로 설정 (User_ChatLog/{session_id}/{persona_type}.json)
    save_dir = f"User_ChatLog/{session_id_base}"  # (P0_chat/)
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성
    file_path = os.path.join(save_dir, f"{full_session_id}.json")  # persona_type.json
    
    # 대화 이력을 JSON 형식으로 변환
    chat_log = []
    for msg in chat_history:
        chat_log.append({
            "role": "user" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content
        })
    
    # JSON 파일로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_log, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 대화 이력이 저장되었습니다: {file_path}")


## **테스트 실행**
## 테스트
store = {} # 대화 이력 저장소
session_id = f"{user_number}_chat" ; session_id
user_input1 = "안녕? 너 나와 닮은 애라며? 요즘 내 고민 말해봐도 돼?"
response1_tag = chat(user_input1, session_id, persona_type="epi")
print("💬 [Epi 기반] AI 응답 1:", response1_tag)

user_input2 = "요즘 뭔가 불안해. 뭔가를 놓치고 있는 것 같아."
response2_tag = chat(user_input2, session_id, persona_type="epi")
print("💬 [Epi 기반] AI 응답 2:", response2_tag)

user_input3 = "뭐랄까.. 당장의 일을 하루하루 소화하느라 내가 정작 지키고 싶은 것들은 뒷전이 되어버렸어."
response3_tag = chat(user_input3, session_id, persona_type="epi")
print("💬 [Epi 기반] AI 응답 3:", response3_tag)

print(store)
save_chat_log(user_number=user_number, persona_type="Epi")