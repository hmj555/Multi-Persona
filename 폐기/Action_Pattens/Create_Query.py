from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
import os
import re

participant_number = "P0"

# ✅ OpenAI 모델 설정
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# ✅ 개선된 Masking & Query Expansion 프롬프트
masked_query_prompt = PromptTemplate.from_template(
    """
    Rephrase the user's experience in a form that can be used in a research paper without personal information, and generate additional search queries.
    
    - Don't include personal information (place names, proper nouns, etc.).
    - Clearly describe the behavioral patterns associated with the experience.
    - Try to make connections to the Big Five personality theories, Emotion Regulation, Social Interaction, etc.
    - Perform query expansion to create three search queries that will be fed into Google Scalar for inferring Action Patterns.
    
    Role: {role}
    Experience: {episode}

    Output format:
    Masked Experience: [Provide the rephrased experience in a single sentence.]
    Expanded Queries:
    1. [Query 1]
    2. [Query 2]
    3. [Query 3]
    """
)

llm_chain = LLMChain(llm=llm, prompt=masked_query_prompt)

def parse_llm_response(response_text):
    """LLM의 응답을 `masked_experience`와 `expanded_queries`로 분리"""
    masked_experience = ""
    expanded_queries = []

    lines = response_text.strip().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Masked Experience:"):
            masked_experience = line.replace("Masked Experience:", "").strip()
        elif line.startswith(("1.", "2.", "3.")):
            query = re.sub(r"^\d+\.\s*", "", line).strip()
            expanded_queries.append(query)

    if not masked_experience or not expanded_queries:
        raise ValueError("❌ LLM 응답에서 `masked_experience` 또는 `expanded_queries`를 찾을 수 없음.")

    return masked_experience, expanded_queries

def generate_expanded_queries(role, episode):
    """GPT를 사용하여 Masked Experience & Query Expansion 수행"""
    response = llm_chain.invoke({"role": role, "episode": episode})
    return parse_llm_response(response["text"])

# 🔹 User Info 불러오기
input_filepath = f"User_info/{participant_number}.json"
with open(input_filepath, "r", encoding="utf-8") as file:
    user_info = json.load(file)

# 🔹 User Query 저장 경로
output_filepath = f"User_Query/{participant_number}.json"

# 🔹 Role & Episode 기반 Rephrased Query 생성 실행
query_data = {"queries": []}

for role_key, role_data in user_info["Episode"].items():
    role_name = role_data["Role"]
    
    for ep_key in ["Ep1", "Ep2"]:
        if ep_key in role_data:
            episode = role_data[ep_key]
            try:
                # 🔹 Masked Experience & Expanded Queries 생성
                masked_query, expanded_queries = generate_expanded_queries(role_name, episode)

                # 🔹 검색용 Query 저장
                query_data["queries"].append({
                    "role": role_name,
                    "original_episode": episode,
                    "masked_query": masked_query,  # ✅ 첫 번째 문장만 저장
                    "expanded_queries": expanded_queries  # ✅ Query 리스트 저장
                })
            except Exception as e:
                print(f"❌ 오류 발생 (role: {role_name}): {e}")

# 🔹 JSON 파일로 저장
os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
with open(output_filepath, "w", encoding="utf-8") as file:
    json.dump(query_data, file, indent=4, ensure_ascii=False)

print("✅ Episode Rephrase & Query Expansion 완료 & 저장:", output_filepath)

