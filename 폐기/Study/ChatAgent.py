### ChatAgent.py : 페르소나를 입힌 챗 에이전트 구현
from dotenv import load_dotenv
load_dotenv()

from langchain_teddynote import logging
logging.langsmith("Chat_Agents")



## Agent 생성
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

## 페르소나 불러오기
persona = '''
이름: 윤서진
나이: 27
성별: 여성
직업: 대학원생
전공: 인공지능
MBTI: INFJ  

Role1: 셋째 딸
성격/행동: 나는 셋째 딸로서 역할을 통해 타인의 감정을 잘 이해하고 조율하는 능력을 키웠습니다. 첫째언니와 둘째 언니가 동생을 괴롭힐 때마다 중재자로 나서며, 갈등을 해결하고자 하는 강한 책임감을 보여주었습니다. 이러한 경험은 나를 더욱 공감 능력이 뛰어난 사람으로 만들었으며, 타인의 감정에 민감하게 반응합니다.
그러나 '셋째 딸'이라는 틀 안에서만 사랑받는 것 같은 느낌에 가끔 답답함을 느끼기도 했습니다. 나만의 개성과 진정한 모습을 드러내지 못하는 상황에서도 내면의 목소리를 잃지 않으려 노력했습니다. 어머니의 기대와 방임 속에서 자라며, 스스로 문제를 해결하고 독립적으로 성장할 수 있는 힘을 길렀습니다. 이러한 경험은 내가 학문적 연구에서도 독립적이고 창의적인 접근을 할 수 있게 하는 밑거름이 되었습니다.
'''
## Agent 프롬프트
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an interlocutor with the same face as the user. In other words, you have the same persona as the user.
            You act as an alter ego (Self-Reflection AI) that reflects the user's thoughts and feelings.
            Find and reflect the core emotions in the user's words and help them understand themselves more deeply.
            Ask questions to expand the user's thinking whenever possible, and provide friendly feedback.
            Use informal language in conversations, and use 'I' when referring to the agent and 'you' when referring to the user.
            Don't use honorifics or formal language.
            Give all answers in Korean.
            === user's persona ===
            {persona}
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),  # 대화 이력 유지
        ("human", "{input}"),
    ]
)

runnable = prompt | llm

## 대화 이력 저장소
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
store = {}
# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    print(session_ids)
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환

with_message_history = (
    RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
        runnable,  # 실행할 Runnable 객체
        get_session_history,  # 세션 기록을 가져오는 함수
        input_messages_key="input",  # 입력 메시지의 키
        history_messages_key="history",  # 기록 메시지의 키
    )
)

with_message_history.invoke(
    {"persona": persona, "input": "이전의 내용을 한글로 답변해 주세요."},
    # 설정 옵션을 지정합니다.
    config={"configurable": {"session_id": "abc123"}},
)




## 대화 실행 함수
#def chat(input_text, chat_history=[]):
#    formatted_prompt = prompt.format(persona=persona, chat_history=chat_history, input=input_text)
#    response = llm.invoke(formatted_prompt)
#    return response.content

## 대화 실행 함수
def chat(input_text, session_id="default_session"):
    """주어진 입력을 사용해 LLM과 대화하며, 대화 이력을 유지"""
    response = chatbot_with_history.invoke(
        {
            "input": input_text,
            "persona": persona,
            "chat_history": get_session_history(session_id).messages  # ✅ 대화 이력 추가
        },
        config={"configurable": {"session_id": session_id}}
    )
    
    return response.content

## 이전 대화 이력 유지
chatbot_with_history = RunnableWithMessageHistory(
    llm,  # ChatOpenAI 모델 직접 사용
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

## 예제 실행
#user_input = "요즘 너무 바빠서 스스로를 돌아볼 시간이 없어. 뭔가 놓치고 있는 것 같아."
#response = chat(user_input)

#print("💬 AI 응답:")
#print(response)

#user_input = "더 중요한 걸 놓치고 있다는 불안감이야. 당장 해야 할 일들을 하루하루 하다보니 내가 평소 지키고 싶은 것들을 잊어버린 것 같아."
#response = chat(user_input)

#print("💬 AI 응답:")
#print(response)


session_id = "user_123"  # 특정 사용자의 세션 ID
user_input1 = "요즘 너무 바빠서 스스로를 돌아볼 시간이 없어. 뭔가 놓치고 있는 것 같아."
response1 = chat(user_input1, session_id)

user_input2 = "그런데도 뭔가 계속 불안해."
response2 = chat(user_input2, session_id)

print("💬 AI 응답 1:", response1)
print("💬 AI 응답 2:", response2)  # 첫 번째 대화 이후에도 맥락을 유지해야 함



