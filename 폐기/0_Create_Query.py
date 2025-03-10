### Create_Query.py : 사용자 경험을 기반으로 RAG 검색 쿼리 생성
### Step(4) 에 필요한 사용자 번호 "Pn"을 프론트엔드에서 받아와야 함

from dotenv import load_dotenv
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("Persona")
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

### (1) 검색 쿼리 생성을 위한 PromptTemplate 정의
query_expansion_prompt = PromptTemplate.from_template(
    """
    사용자의 역할: {role}
    사용자의 경험: {user_experience}
    
    위의 경험과 관련된 심리학 및 성격 발달 연구를 찾기 위해 3개의 검색 Query를 생성하세요.
    - 역할과 관련된 사용자의 경험으로부터 형성된 성격을 추론하기 위한 컨텍스트를 찾는 검색 쿼리로 사용됩니다.
    - Big Five 성격 특성과 관련된 연관성을 고려하세요.
    - 검색 쿼리는 연구 논문에서 나올 법한 형태로 작성하세요.
    - 검색 쿼리는 영어로 작성하세요.
    
    예시:
    user_role: 셋째 딸
    user_experience: 나는 셋째 딸로서 첫째언니와 둘째 언니가 동생과 싸울 때마다 중재했다.
    answer:
    1. How does the experience of mediating sibling conflict in childhood affect personality development?
    2. what is the research on the relationship between family structure (first, second, and third) and personality development?
    3. what is the impact of mediation experience on Extraversion and Agreeableness in the Big Five personality theory?
    """
)

### (2) OpenAI 모델 설정
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

### (3) 체인 연결
llm_chain = LLMChain(llm=llm, prompt=query_expansion_prompt)

### (4) 사용자 경험 불러오기 User_info/Pn.json  --> 프론트엔드에서 "Pn"을 받아와야 함
import json; import os
input_filepath = "User_info/P0.json"
output_filepath = "User_Query/P0.json"

os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
# 검색 쿼리를 저장할 파일이 존재하지 않으면 생성
if not os.path.exists(output_filepath):
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    print(f"검색 쿼리를 저장할 {output_filepath} 생성 완료.")
else:
    print(f"검색 쿼리를 저장할 {output_filepath} 이미 존재합니다.")

# 사용자 경험 읽어오기
with open(input_filepath, "r", encoding="utf-8") as f:
    user_data = json.load(f)

print(user_data)

### (5) 각 역할(Role)의 각 에피소드(Ep1, Ep2)별로 검색 쿼리 생성
queries = {"User": user_data["name"], "Queries": []}

for role_key, role_data in user_data["Episode"].items():
    role = role_data["Role"]  # 역할
    for ep_key in ["Ep1", "Ep2"]:  # 에피소드
        if ep_key in role_data:
            user_experience = role_data[ep_key]  # 에피소드 내용   
            
            print("========== 쿼리로 생성할 데이터 ==========")
            print("사용자 역할: ", role , "\n")
            print("에피소드 번호: ", ep_key , "\n")
            print("사용자 경험: ", user_experience , "\n")
            print("========== 검색 쿼리 생성중 ==========")
            
            # 검색 쿼리 생성
            expanded_query = llm_chain.invoke({
                "role": role,
                "user_experience": user_experience
            })
            
            print("생성된 검색 쿼리: ", "\n",  expanded_query["text"])
            print("========== 검색 쿼리 생성 완료 ==========")

            # 검색 쿼리 저장
            queries["Queries"].append({
                "Role": role,
                "Experience": user_experience,
                "Generated_Query": expanded_query["text"]
            })
            
            print("========== 데이터로 검색 쿼리 저장 완료 ========== ")

### (6) 생성된 쿼리를 `User_Query/Pn.json`에 저장
with open(output_filepath, "w", encoding="utf-8") as f:
    json.dump(queries, f, indent=4, ensure_ascii=False)

print(f"✅ {output_filepath} 파일에 검색 쿼리 저장 완료!")


