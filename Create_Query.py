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
    Rephrase the user's experience in a form that can be used for general web search (blogs, forums, articles) without personal information, and generate additional search queries.
    
    - Remove and Rephrase personal details (place names, organizations, personal identifiers, etc.) form Episode.
    - Expand the query to retrieve diverse but relevant experiences.
    - Generate two search queries optimized for relevant real-world experience web search.
    - All outputs are in Korean.

    Role: {role}
    Episode: {episode}
    
    Masked Episode Example (if Epi: 나는 무안이라는 작은 시골 마을에서 나고 자랐다. 무안은 친구도, 지인들도 한 다리를 건너면 다 알 만큼 작은 도시다. 외향적이고 새로운 것을 좋아하는 나에게는 사랑하는 고향인 동시에 답답한 공간이었다.)
    나는 작은 시골 마을에서 나고 자랐다. 그곳은 친구도, 지인들도 한 다리를 건너면 다 알 만큼 작은 도시다. 외향적이고 새로운 것을 좋아하는 나에게는 사랑하는 고향인 동시에 답답한 공간이었다.
    
    Generated Query Examples (if role: 공상가, Epi: 한국에서 첫째 딸, 그것도 2살차이 남동생이 있는 첫째 딸은 어디에도 말할 수 없는 고충을 하나씩은 다 가지고 있는 것 같다. 집에 부모님이 안계 시는 날에는 청소, 설거지, 요리 모두 내 몫이었다. ):
    1. 한국에서 남동생이 있는 첫째 딸로서의 경험을 공유하는 사람들의 이야기를 찾아보세요.
    2. 한국에서 첫째 딸이 가지는 성격적 특징은 무엇인가요?

    Output format:
    Masked Episode: [Provide the rephrased episode in a single sentence.]
    Expanded Queries (Only Two):
    1. [Query 1] 
    2. [Query 2] 
    """
)

# (Search in blogs and forums)
# (Search for personal experiences on SNS)

llm_chain = LLMChain(llm=llm, prompt=masked_query_prompt)

def parse_llm_response(response_text):
    """LLM의 응답을 `masked_episode`와 `expanded_queries`로 분리"""
    masked_episode = ""
    expanded_queries = []

    lines = response_text.strip().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Masked Episode:"):
            masked_episode = line.replace("Masked Episode:", "").strip()
        elif line.startswith(("1.", "2.", "3.")):
            query = re.sub(r"^\d+\.\s*", "", line).strip()
            expanded_queries.append(query)

    if not masked_episode or not expanded_queries:
        raise ValueError("❌ LLM 응답에서 `masked_episode` 또는 `expanded_queries`를 찾을 수 없음.")

    return masked_episode, expanded_queries

def generate_expanded_queries(role, episode):
    """GPT를 사용하여 Masked Episode & Query Expansion 수행"""
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
                masked_episode, expanded_queries = generate_expanded_queries(role_name, episode)

                # 🔹 검색용 Query 저장
                query_data["queries"].append({
                    "role": role_name,
                    "original_episode": episode,
                    "masked_episode": masked_episode,  # ✅ 첫 번째 문장만 저장
                    "expanded_queries": expanded_queries  # ✅ Query 리스트 저장
                })
            except Exception as e:
                print(f"❌ 오류 발생 (role: {role_name}): {e}")

# 🔹 JSON 파일로 저장
os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
with open(output_filepath, "w", encoding="utf-8") as file:
    json.dump(query_data, file, indent=4, ensure_ascii=False)

print("✅ Episode Rephrase & Query Expansion 완료 & 저장:", output_filepath)

