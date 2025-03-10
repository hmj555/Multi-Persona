# ch02: Prompts
from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("LangChat-t1")

### 방법1. from_template() 메서드로 프롬프트 탬플릿 객체 생성
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
from langchain_core.prompts import PromptTemplate  # 치환될 변수를 {}로 묶기
template = "{country}의 수도는 어디인가요?"
prompt = PromptTemplate.from_template(template)
chain = prompt | llm
chain.invoke("대한민국").content

### 방법2. PromptTemplate 객체 생성과 동시에 prompt 생성
template = "{country}의 수도는 어디인가요?"
prompt = PromptTemplate(
    template = template, 
    imput_variable = ["country"]
)
prompt
prompt.format(country = "대한민국")

template = "{country1}과 {country2}의 수도는 각각 어디인가요?"
prompt = PromptTemplate(
    template=template,
    input_variables=["country1"],
    partial_variables={
        "country2": "미국"  # dictionary 형태로 partial_variables를 전달
    },
)
prompt.format(country1= "대한민국")
prompt_partial = prompt.partial(country2 = "캐나다")
prompt_partial
prompt_partial.format(country1="대한민국")
chain = prompt_partial | llm
chain.invoke("대한민국").content
chain.invoke({"country1": "대한민국" , "country2": "캐나다"}).content

### partial_variables: 부분 변수 채움
# 항상 공통된 방식으로 가져오고 싶은 변수가 있는 경우
from datetime import datetime
datetime.now().strftime("%B %d")

def get_today():
    return datetime.now().strftime("%B %d")

prompt = PromptTemplate(
    template = "오늘의 날짜는 {today}입니다. 오늘이 생일인 유명인 {n}명을 나열해 주세요. 생년월일을 표기해주세요.",
    input_variables = ["n"], # 변수를 따옴표로 묶어서 리스트로 전달
    partial_variables = { # 딕셔너리 형태로 partial_variables를 전달
        "today": get_today
    }
)
prompt.format(n=3)

chain= prompt|llm
print(chain.invoke(3).content)
print(chain.invoke({"today": "Jan 02", "n": 3}).content) # today 변수 값이 고정됨

### 파일로부터 template 읽어오기
from langchain_core.prompts import load_prompt
prompt = load_prompt("prompts/country_capital.json")

### ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
chat_prompt = ChatPromptTemplate.from_template(
    "{country}의 수도는 어디인가요?"
)
chat_prompt.format(country="대한민국")

from langchain_core.prompts import ChatPromptTemplate
chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절한 AI 어시스턴트입니다. 당신의 이름은 {name} 입니다."),
        ("human", "반가워요!"),
        ("ai", "안녕하세요! 무엇을 도와드릴까요?"),
        ("human", "{user_input}"),
    ]
)

messages = chat_template.format_messages(
    name = "테디", user_input = "당신의 이름은 무엇입니까?"
)
messages
llm.invoke(messages).content

chain = chat_template | llm
chain.invoke({"name": "테디", "user_input": "당신의 이름은 무엇입니까?"}).content

### MessagePlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
             "당신은 요약 전문 AI 어시스턴트입니다. 당신의 임무는 주요 키워드로 대화를 요약하는 것입니다.",
        ),
        MessagesPlaceholder(variable_name="conversation"), # 대화 목록 추가 가능
        (
        ("human" , "지금까지의 대화를 {word_count} 단어로 요약합니다.")
        )
    ]
)
chat_prompt

formatted_chat_prompt = chat_prompt.format(
    word_count = 5, 
    conversation = [
        ("human", "안녕하세요! 저는 오늘 새로 입사한 테디 입니다. 만나서 반갑습니다."),
        ("ai", "반가워요! 앞으로 잘 부탁 드립니다."),
    ],
)
print(formatted_chat_prompt)

chain = chat_prompt | llm | StrOutputParser()
chain.invoke(
        {
        "word_count": 5,
        "conversation": [
            (
                "human",
                "안녕하세요! 저는 오늘 새로 입사한 테디 입니다. 만나서 반갑습니다.",
            ),
            ("ai", "반가워요! 앞으로 잘 부탁 드립니다."),
        ],
    }
)

#### FewShotPromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

### Example Selector









