### Personality_Inference.py: 검색기를 통한 컨텍스트 생성 + 컨텍스트 기반 성격 추론 실행
### 사용자 번호 "Pn"을 프론트엔드에서 받아와야 함

from dotenv import load_dotenv ; import os
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("Persona")
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))

############ (2)-1. 컨텍스트 생성을 위한 Retriever  ############
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# 저장된 FAISS DB 로드
vectorstore = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(model="text-embedding-ada-002"),
    allow_dangerous_deserialization=True 
)

############ (3)-1. 성격 추론기  ############
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template(
    """You are an assistant for personality inferences. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Answer in Korean.
    Answer Example: Openness, imagination, creativity, and receptiveness to new experiences

    #Question: 
    {question} 
    #Context: 
    {context} 

    #Answer:
    """
)

llm = ChatOpenAI(model_name = "gpt-4o", temperature = 0.5)

chain = (
    {"context": RunnablePassthrough(), "question": RunnablePassthrough()} 
    | prompt
    | llm
    | StrOutputParser()
)

############ (2)-2. 컨텍스트 생성을 위한 검색 실행  ############
import json
user_number = "P0"  # 프론트엔드에서 user_number를 받아와야 함
input_filepath = f"User_Query/{user_number}.json"

with open(input_filepath, "r", encoding="utf-8") as f:
    user_query_data = json.load(f)
    
print(user_query_data)

# 각 검색 쿼리에 대해 검색 수행 및 컨텍스트 저장
for query_data in user_query_data["Queries"]:
    query = query_data["Generated_Query"]
    
    print("🔍 검색 쿼리: \n", query)
    
    retrieved_docs = vectorstore.similarity_search_with_score(query, k=3)

    # 검색된 결과 저장
    retrieved_texts = []
    retrieved_scores = []
    for doc, score in retrieved_docs:
        retrieved_texts.append(doc.page_content)
        retrieved_scores.append(float(score))
        print(f"📄 검색 결과 (유사도 점수: {score}): {doc.page_content}")
    
    # 검색된 컨텍스트를 Query 데이터에 추가
    query_data["Context"] = retrieved_texts
    query_data["Scores"] = retrieved_scores
    print(f"컨텍스트 데이터 추가 완료")

# 업데이트된 데이터 저장
with open(input_filepath, "w", encoding="utf-8") as f:
    json.dump(user_query_data, f, ensure_ascii=False, indent=4)

print(f"✅ {input_filepath} 파일 업데이트 완료: 검색 컨텍스트 추가됨.")
    

############ (3)-2. 성격 추론 실행  ############
user_info_path = f"User_info/{user_number}.json"
user_query_path = f"User_Query/{user_number}.json"

# 사용자 정보 및 쿼리 로드
with open(user_info_path, "r", encoding="utf-8") as f:
    user_data = json.load(f)
with open(user_query_path, "r", encoding="utf-8") as f:
    user_context = json.load(f)
    
# 역할(Role) 및 성격(Personality) 추론
for n in range(1, 4):  # Role 1 ~ Role 3
    for N in range(1, 3):  # Personality 1 ~ Personality 2
        i= 0 
        role = user_data["Episode"][f"Role {n}"]["Role"]
        user_experience = user_data["Episode"][f"Role {n}"][f"Ep{N}"]
        context = user_context["Queries"][i]["Context"] 

        print(f"성격 추론 시작: Role {n}, Personality {N}")
        question = f"[나는 {role}로서 {user_experience}]\n 이 경험으로부터 어떤 성격 특성이 형성되는지 알려주세요."
        print(question)
        
        response = chain.invoke({"context": context, "question": question}) 
        print(response)

        # 결과를 JSON 데이터에 추가
        user_data["Episode"][f"Role {n}"][f"Personality {N}"] = response
        print(f"성격 추론 결과 추가 완료")
        i += 1


# 업데이트된 JSON 저장
with open(user_info_path, "w", encoding="utf-8") as f:
    json.dump(user_data, f, ensure_ascii=False, indent=4)

print(f"성격 추론 결과가 성공적으로 {user_info_path}에 추가되었습니다.")






role = user_data["Episode"]["Role 3"]["Role"] ; role
user_experience = user_data["Episode"]["Role 3"]["Ep1"] ; user_experience
context = user_context["Queries"][4]["Context"] ; context

question = f"나는 {role}로서 {user_experience}와 같은 경험으로부터 어떤 성격 특성이 형성되는지 알려주세요." ;question
response = chain.invoke({"context": context , "question": question})


print(response)

############ 






