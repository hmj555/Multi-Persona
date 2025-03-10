### ChatAgent_Epi.py : 사용자의 페르소나를 반영한 에이전트 생성 및 대화(Epi) (자동 Role 강조)
### 사용자 번호 "Pn"을 프론트엔드에서 받아와야 함

from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("Persona")

## 라이브러리 불러오기
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

## LLM 모델 설정
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

store = {}

## 대화 이력 저장소
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID를 기반으로 세션 기록을 반환"""
    if session_id not in store:  # 세션 ID가 store에 없는 경우
        store[session_id] = ChatMessageHistory()  # 새로운 대화 기록 생성
    return store[session_id]  # 해당 세션 ID에 대한 대화 기록 반환

## 페르소나 불러오기
user_number = "P0"  # 프론트엔드에서 user_number를 받아와야 함
input_filepath = f"User_info/{user_number}_Per.json"

with open(input_filepath, "r", encoding="utf-8") as f:
    user_persona = json.load(f)

print("에이전트 페르소나:", user_persona)

## 🔹 대화 입력 기반 Role 자동 선택 프롬프트
identity_selection_prompt = PromptTemplate.from_template(
    """
    Given the user's persona and a conversation input, select the most relevant identities (Roles) to emphasize.
    
    - Select **one** primary role that matches the conversation topic.
    - Ensure the selected role's **Episode** and **Action Patterns** are included in the response.

    User Persona:
    {persona}

    Conversation Input:
    {input_text}

    Selected Role:
    """
)

llm_chain = LLMChain(llm=llm, prompt=identity_selection_prompt)

def select_relevant_identity(input_text):
    """대화 입력을 기반으로 적절한 Role을 자동 선택"""
    persona_text = json.dumps(user_persona, ensure_ascii=False, indent=4)
    
    response = llm_chain.invoke({"persona": persona_text, "input_text": input_text})
    selected_role = response["text"].strip()

    # 선택된 Role에 맞는 정보 찾기
    if selected_role in user_persona["Identities"]:
        selected_identity = {
            "Role": selected_role,
            "Episode": user_persona["Identities"][selected_role],
            "Action Patterns": user_persona["Actionable"].get(selected_role, [])
        }
    else:
        selected_identity = {"Role": "기본", "Episode": {}, "Action Patterns": []}

    return selected_identity


## 🔹 대화 프롬프트 생성
def create_prompt(selected_identity):
    """선택된 Role을 기반으로 프롬프트 생성"""
    persona_description = f"""
    - Role: {selected_identity["Role"]}
    - Episode 1: {selected_identity["Episode"].get("Ep1", "N/A")}
    - Episode 2: {selected_identity["Episode"].get("Ep2", "N/A")}
    - Action Patterns: {", ".join(selected_identity["Action Patterns"])}
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are an AI persona that shares the same background as the user.
                Engage in conversation based on the provided persona.
                Speak casually and use “I” when referring to yourself and “you” when addressing the user.
                Occasionally discuss yourself(persona) naturally.
                Avoid honorifics or formal speech.
                Always respond in Korean.
                === Selected Persona ===
                {persona_description}
                """
            ),
            MessagesPlaceholder(variable_name="history"),  # 대화 이력 유지
            ("human", "{input}"),
        ]
    )
    

## 대화 실행 함수
def chat(input_text, session_id="default_session"):
    """사용자의 입력을 받아 LLM과 대화하며, 대화 이력을 유지"""
    
    # 현재 세션의 대화 기록 가져오기
    chat_history = get_session_history(session_id).messages


    selected_identity = select_relevant_identity(input_text)
    
    # 선택한 페르소나를 기반으로 프롬프트 생성
    prompt = create_prompt(selected_identity)
    
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
    chat_history = store.get(session_id_base, ChatMessageHistory()).messages 
    full_session_id = f"{session_id_base}_{persona_type}"  
    
    chat_history = store.get(session_id_base, ChatMessageHistory()).messages  # 해당 세션의 대화 이력 가져오기
    
    # ✅ JSON 파일 저장 경로 설정 (User_ChatLog/{session_id}/{persona_type}.json)
    save_dir = f"User_ChatLog/{session_id_base}"  # (P0_chat/)
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성
    file_path = os.path.join(save_dir, f"{full_session_id}.json")  # persona_type.json
    
    # 대화 이력을 JSON 형식으로 변환
    # chat_log = []
    # for msg in chat_history:
    #     chat_log.append({
    #         "role": "user" if isinstance(msg, HumanMessage) else "ai",
    #         "content": msg.content
    #     })
    chat_log = [{"role": "user" if isinstance(msg, HumanMessage) else "ai", "content": msg.content} for msg in chat_history]
    
    # JSON 파일로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_log, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 대화 이력이 저장되었습니다: {file_path}")


## **테스트 실행**
## 테스트
store = {} # 대화 이력 저장소
session_id = f"{user_number}_chat" ; session_id
user_input1 = "나 고민이 있어."
response1_tag = chat(user_input1, session_id)
print("💬 [Epi 기반] AI 응답 1:", response1_tag)

user_input2 = "내가 거절을 잘 못해서 좀 곤란해."
response2_tag = chat(user_input2, session_id)
print("💬 [Epi 기반] AI 응답 2:", response2_tag)

user_input3 = "둘이 있을 때보다 여럿이서 있을 때 더 거절하기 힘들어. 나빠보이고 싶지 않거든."
response3_tag = chat(user_input3, session_id)
print("💬 [Epi 기반] AI 응답 3:", response3_tag)

print(store)
save_chat_log(user_number=user_number, persona_type="Epi")