# langchain.py
# env: LangChat ; python 3.11 ; gpt-4-turbo ; 
# pip install -r https://raw.githubusercontent.com/teddylee777/langchain-kr/main/requirements.txt
# pip install -qU langchain-teddynote

# openai API KEY
from dotenv import load_dotenv 
load_dotenv() 
import os ; print(f"[API KEY]\n{os.environ['OPENAI_API_KEY']}") 

# langsmith connection
from langchain_teddynote import logging
logging.langsmith("LangChat-t1")

# openai model
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    temperature = 0.4, # 창의성 (0.0~2.0)
    # max_tokens = 100, # 최대 토큰수 (1~4096)
    model_name = "gpt-4o" # gpt-4-turbo
)

question = "대한민국의 수도는 어디인가요?"
response = llm.invoke(question)
# print(f"[답변]: {llm.invoke(question)}")
response.content ; response.response_metadata

# LogProb 활성화
llm_w_logprob = ChatOpenAI(
    temperature = 0.4, # 창의성 (0.0~2.0)
    model_name = "gpt-4o", # gpt-4-turbo
    max_tokens = 100, # 최대 토큰수 (1~4096)
).bind(logprobs = True)
question = "대한민국의 수도는 어디인가요?"
response = llm_w_logprob.invoke(question)
response.response_metadata

# 스트리밍 출력: 질의에 대한 답변을 실시간으로 받을 때 유용
answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!") ; answer
for token in answer:
    print(token.content, end = "", flush=True)
    
from langchain_teddynote.messages import stream_response # 모듈화
answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!")
stream_response(answer)

# System, User 프롬프트 수정
system_prompt = "당신은 사용자의 정보를 입력받아 페르소나를 생성하는 서비스를 제공합니다. \n 당신의 임무는 사용자의 정보를 바탕으로 페르소나를 생성하는 것입니다."
user_prompt = "나의 정보는 아래와 같습니다. \n 이름: 테디 \n 나이: 27 \n 성별: 여성 \n 직업: 대학원생 \n 전공: 인공지능 대학원 \n MBTI: INFJ \n (Role)에피소드: (셋째 딸)나는 첫째 언니와 둘째언니가 동생을 괴롭힐 때, 항상 말리곤 했다. \n (셋째 딸)어른들은 '셋째 딸'을 예뻐한다. 나는 '나' 자체가 아니라 '셋째 딸'이기 때문에 예뻐하는 어른들을 보며 기쁘기도 했지만, 진정한 나를 숨기게 되고 이에 답답함을 느꼈다. \n (셋째 딸)엄마는 내가 뭐든 잘 해낼거라고 생각하고 나에게 신경을 덜 써줬다. 나는 그게 방임 같기도, 자유 같기도 했지만 그 덕분에 독립적으로 자란 거 같다."

llm = ChatOpenAI(
    temperature = 0.4, # 창의성 (0.0~2.0)
    # max_tokens = 100, # 최대 토큰수 (1~4096)
    model_name = "gpt-4o", # gpt-4-turbo
    system_prompt = system_prompt,
    user_prompt = user_prompt
)
answer = llm.stream("나의 정보를 바탕으로 페르소나를 생성해주세요!")
stream_response(answer)

##### 05. LangChain Expression Language (LCEL)
from dotenv import load_dotenv
load_dotenv()

from langchain_teddynote.messages import stream_response
from langchain_core.prompts import PromptTemplate

template = "{country}의 수도는 어디인가요?"
prompt_template = PromptTemplate.from_template(template) # 프롬프트 탬플릿 객체 생성
prompt_template
prompt = prompt_template.format(country = "대한민국") # 프롬프트 생성
prompt

# 사용자 입력 -> 프롬프트 탬플릿 -> 프롬프트 -> 모델
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    temperature = 0.4, 
    # max_tokens = 100, 
    model_name = "gpt-4o" 
)
prompt = PromptTemplate.from_template("{topic}에 대해 쉽게 설명해주세요.")
model = ChatOpenAI()
chain = prompt | model # 체인 생성(연결)

input = {"topic": "인공지능 모델의 학습 원리"}
chain.invoke(input) # input을 체인에 전달하여 output 출력
answer = chain.stream(input) ; stream_response(answer)

# Output Parser
from langchain_core.output_parsers import StrOutputParser
output_parser = StrOutputParser()
chain = prompt | model | output_parser

## 템플릿 변경
template = """
당신은 영어를 가르치는 10년차 영어 선생님입니다. 상황에 [FORMAT]에 영어 회화를 작성해 주세요.

상황:
{question}

FORMAT:
- 영어 회화:
- 한글 해석:
"""
prompt = PromptTemplate.from_template(template) # 프롬프트 탬플릿으로 프롬프트 생성
model = ChatOpenAI(model_name = "gpt-4o") # 모델 초기화
output_parser = StrOutputParser() # 문자열 출력 파서 초기화
chain = prompt | model | output_parser # 체인 생성

answer = chain.stream({"question" : "저는 식당에 가서 음식을 주문하고 싶어요."})
stream_response(answer)

# stream: 실시간 출력 ; end="" : 줄바꿈 방지 ; flush=True : 버퍼 비우기
for token in chain.stream({"topic": "멀티모달"}):
    print(token, end="", flush = True)

# batch: 단위 실행, 여러개의 딕셔너리를 포함하는 리스트를 인자로 받아 일괄 처리 (하나의 체인에서 일괄 처리)
chain.batch([{"topic": "ChatGPT"} , {"topic": "Instagram"}])
chain.batch([
    {"topic": "ChatGPT"},
    {"topic": "Instagram"},
    {"topic": "Google"},
    {"topic": "AI"},
    {"topic": "ML"}
],
    config = {"max_concurrency": 3} # 동시 처리할 수 있는 최대 작업 수
    )

# async stram: 비동기 스트림, 메시지를 순차적으로 받은 후, 즉시 출력 -> 챗봇 느낌이 아님
async for token in chain.astream({"topic": "YouTube"}):
    print(token, end="", flush=True)

import asyncio
async def main():
    my_process = await chain.ainvoke({"topic": "NVDA"}) # await: 비동기 작업이 완료될 때까지 기다림
    print(my_process)
asyncio.run(main())

# Parallel: 병렬성 (여러 개의 체인)
from langchain_core.runnables import RunnableParallel
# 수도 체인
chain1 = (PromptTemplate.from_tamplate("{country}의 수도는 어디야?")
        | model
        | StrOutputParser()
)
chain2 = (
    PromptTemplate.from_template("{country}의 면적은 얼마야?")
    | model
    | StrOutputParser()
)
combined = RunnableParallel(capital = chain1, area = chain2) # 병렬 체인 생성
chain1.invoke({"country": "대한민국"}) 
chain2.invoke({"country": "미국"})
combined.invoke({"country": "대한민국"})

### 배치에서의 병렬 처리 (여러 개의 배치, 여러개의 입력)
chain1.batch([{"country": "대한민국"}, {"country": "미국"}]) # 수도 체인에 대한 배치
chain2.batch([{"country": "대한민국"}, {"country": "미국"}]) # 면적 체인에 대한 배치
combined.batch([{"country": "대한민국"}, {"country": "미국"}]) # 병렬 처리(면적, 배치)

### 데이터를 전달하는 방법
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
prompt = PromptTemplate.from_template("{num}의 10배는?")
llm = ChatOpenAI(temperature = 0)
chain = prompt | llm
chain.invoke({"num": 5}) ; chain.invoke(5)

from langchain_core.runnables import RunnablePassthrough
RunnablePassthrough().invoke({"num": 10}) # 입력이 그대로 출력됨

runnable_chain = {"num": RunnablePassthrough()} | prompt | ChatOpenAI()
runnable_chain.invoke(10) # 10의 10배는 100입니다.
RunnablePassthrough().invoke({"num":1}) # {'num': 1}

(RunnablePassthrough.assign(new_num = lambda x: x["num"]*3)).invoke({"num": 1}) # 1 인수에 3이 추가되어 출력됨

####RunnableParallel
from langchain_core.runnables import RunnableParallel
runnable = RunnableParallel(
    passed = RunnablePassthrough(),
    extra = RunnablePassthrough.assign(mult=lambda x: x["num"]*3)
    modified = lambda x: x["num"] + 1
)
runnable.invoke({"num": 1}) # {'passed': {'num': 1}, 'extra': {'num': 1, 'mult': 3}, 'modified': 2}

chain1 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country}의 수도는 어디야?")
    | ChatOpenAI()
)
chain2 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country}의 면적은 얼마야?")
    | ChatOpenAI()
)

combined_chain = RunnableParallel(capital = chain1, area = chain2)
combined_chain.invoke({"country": "대한민국"})

### RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from datetime import datetime

def get_today(a):
    return datetime.today().strftime("%b-%d")
get_today(None)

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
prompt = PromptTemplate.from_template(
    "{today} 가 생일인 유명인 {n} 명을 나열하세요. 생년월일을 표기해 주세요."
)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
chain = (
    {"today": RunnableLambda(get_today), "n": RunnablePassthrough()} # 람다 함수를 사용하여 오늘 날짜를 가져옴
    | prompt
    | llm
    | StrOutputParser()
)
print(chain.invoke(3))

### itemgetter
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

def length_function(text):
    return len(text)

def _multiple_length_function(text1, text2):
    return len(text1) * len(text2)

def multiple_length_function(_dict):
    return _multiple_length_function(_dict["text1"], _dict["text2"])

prompt = ChatPromptTemplate.from_template("{a} + {b} 는 무엇인가요?")
model = ChatOpenAI()
chain1 = prompt | model
chain = (
    {
        "a": itemgetter("word1") | RunnableLambda(length_function),
        "b": {"text1": itemgetter("word1"), "text2": itemgetter("word2")}
        | RunnableLambda(multiple_length_function),
    }
    | prompt
    | model
)
chain.invoke({"word1": "hello", "word2": "world"})








