### langchat.py : 페르소나 생성

### setting
from dotenv import load_dotenv  # openai API KEY
load_dotenv() 
import os ; print(f"[API KEY]\n{os.environ['OPENAI_API_KEY']}") 
from langchain_teddynote import logging # langsmith connection
logging.langsmith("LangChat-t1")

# PromptTemplate 생성
from langchain.prompts import PromptTemplate
prompt_template = """
You provide a service that generates a persona by receiving user information.
Your mission is to create a personalized persona based on your information.
A user lives in many roles as an individual.
Create a persona by inferring the user's personality and behavioral style based on the episode according to the role.
Please answer in Korean.

USER INFORMATION:
Age: {age} Sex: {sex} Occupation: {occupation} Major: {major} 
MBTI: {MBTI} 
(Role)Episode: {Role1}{Episode11} \n {Role1}{Episode12} \n {Role1}{Episode13}

OUTPUT FORMAT:
Name: (You create it at random)
Age: 
Sex:
Occupation:
Major:
MBTI:
Personality/Behavior(Role1): 
"""
prompt = PromptTemplate.from_template(prompt_template) ; prompt

### model
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    temperature = 0.4, # 창의성 (0.0~2.0)
    # max_tokens = 100, # 최대 토큰수 (1~4096)
    model_name = "gpt-4-turbo" # gpt-4-turbo
)

### Chain
from langchain.chains import LLMChain
chain = LLMChain(prompt=prompt, llm=llm)

### Output
result = chain.run({"age": "27", 
             "sex": "여성",
             "occupation" : "대학원생", 
             "major" : "인공지능", 
             "MBTI" : "INFJ", 
             "Role1": "셋째 딸", 
             "Episode11" : "나는 첫째 언니와 둘째언니가 동생을 괴롭힐 때, 항상 말리곤 했다.", 
             "Episode12" : "어른들은 '셋째 딸'을 예뻐한다. 나는 '나' 자체가 아니라 '셋째 딸'이기 때문에 예뻐하는 어른들을 보며 기쁘기도 했지만, 진정한 나를 숨기게 되고 이에 답답함을 느꼈다.",
             "Episode13" : "엄마는 내가 뭐든 잘 해낼거라고 생각하고 나에게 신경을 덜 써줬다. 나는 그게 방임 같기도, 자유 같기도 했지만 그 덕분에 독립적으로 자란 거 같다." ,       
              })
print(result)






