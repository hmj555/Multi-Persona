import json
import os
from collections import defaultdict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


participant_number = "P0"


# OpenAI 모델 설정
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# ✅ 개선된 Action Patterns 추론 프롬프트
action_pattern_prompt = PromptTemplate.from_template(
    """
    Based on the user's role, personal experiences (Episode 1 and Episode 2), and summarized context from research papers, generate 2-3 simple and clear action patterns. 
    
    - Ensure the action patterns align with both personal experiences.
    - Keep the descriptions simple and practical.
    - Focus on observable behaviors rather than theoretical concepts.

    Role: {role}
    Episode 1: {episode1}
    Episode 2: {episode2}
    Summarized Context: {summary}

    Action Patterns Examples:
    “I imagine different scenarios and outcomes when faced with a problem or decision. This can lead to more creative and flexible thinking, as evidenced by my experience of imagining alternative outcomes during discussions or debates.”
    ”I have conversations with friends and coworkers about 'what if' scenarios or imaginative ideas. I share my thoughts and build on each other's ideas to create a collaborative and open-minded environment.”
    “I utilize my outgoing personality by actively seeking out social opportunities. I try to join clubs, attend community events, or participate in group activities that align with my interests to increase my sense of belonging and enrich my life experiences.”
    "My tendency to avoid conflict and always want to be the “good kid” can sometimes make it difficult for me to express my opinions and set boundaries in social situations. I find it difficult to say no sometimes."

    Action Patterns:
    """
)

llm_chain = LLMChain(llm=llm, prompt=action_pattern_prompt)

def summarize_context(papers):
    """검색된 논문들의 snippet과 abstract 내용을 요약"""
    summaries = []
    for paper in papers:
        snippet = paper["abstract"]["snippet"]
        content = paper["abstract"]["content"] if paper["abstract"]["content"] != "No abstract available" else ""
        summary_text = f"{snippet} {content[:500]}"  # 500자 이내로 요약
        summaries.append(summary_text)

    return " ".join(summaries)  # 전체 요약을 하나의 문자열로 합침

def infer_action_patterns(role, episode1, episode2, summary):
    """LLM을 사용해 Episode와 Context를 반영한 Action Patterns 추론"""
    response = llm_chain.invoke({"role": role, "episode1": episode1, "episode2": episode2, "summary": summary})
    action_patterns = response["text"].strip().split("\n")  # 리스트로 변환
    return [pattern.strip("- ") for pattern in action_patterns if pattern.strip()]  # 리스트에서 불필요한 "-" 제거

# 🔹 User_Context/P0.json 불러오기
context_filepath = f"User_Context/{participant_number}.json"
with open(context_filepath, "r", encoding="utf-8") as file:
    user_context = json.load(file)

# 🔹 User_Info/P0.json 불러오기
user_info_filepath = f"User_info/{participant_number}.json"
with open(user_info_filepath, "r", encoding="utf-8") as file:
    user_info = json.load(file)

# 🔹 같은 Role을 가진 Abstract를 합쳐서 저장
role_contexts = defaultdict(list)

for context_data in user_context["queries"]:
    role = context_data["role"]
    summary = summarize_context(context_data["papers"])
    role_contexts[role].append(summary)  # 같은 role의 논문 요약을 모음

# 🔹 Role과 연결된 Abstract 요약 및 Action Patterns 추론
for role_key, role_data in user_info["Episode"].items():
    role = role_data["Role"]
    
    # 🔹 Ep1, Ep2 가져오기
    episode1 = role_data.get("Ep1", "")
    episode2 = role_data.get("Ep2", "")
    
    # 🔹 같은 Role의 모든 논문 요약을 하나로 합침
    combined_summary = " ".join(role_contexts.get(role, []))  # 같은 Role의 논문 요약들을 연결
    
    if combined_summary:  # 검색된 결과가 있을 때만 실행
        action_patterns = infer_action_patterns(role, episode1, episode2, combined_summary)  # LLM 추론

        # 🔹 User_Info/P0.json에 Action 추가
        role_data["Action"] = action_patterns  
        print(f"✅ {role}의 Action Patterns 추가 완료")

# 🔹 JSON 파일로 저장
with open(user_info_filepath, "w", encoding="utf-8") as file:
    json.dump(user_info, file, indent=4, ensure_ascii=False)

print("🎯 Episode 기반 Action Patterns 추가 완료 & 저장:", user_info_filepath)


##### ===== Persona 생성 ===== #####
def create_persona(user_info_path, save_path):
    """User_Info.json에서 페르소나를 생성하고 저장"""
    with open(user_info_path, "r", encoding="utf-8") as file:
        user_info = json.load(file)

    persona = {
        "Base Information": {
            "Age": user_info["Age"],
            "Gender": user_info["Gender"],
            "Job": user_info["Job"],
            "Major": user_info["Major"],
            "MBTI": user_info["MBTI"]
        },
        "Identities": {},
        "Actionable": {}
    }

    # Role & Episode & Action Patterns 저장
    for role_key, role_data in user_info["Episode"].items():
        role = role_data["Role"]
        episode1 = role_data.get("Ep1", "")
        episode2 = role_data.get("Ep2", "")
        action_patterns = role_data.get("Action", [])

        persona["Identities"][role] = {
            "Ep1": episode1,
            "Ep2": episode2
        }
        persona["Actionable"][role] = action_patterns

    # 🔹 JSON으로 저장
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(persona, file, indent=4, ensure_ascii=False)

    print("✅ 페르소나 생성 완료 & 저장:", save_path)
    return persona

user_info_path = f"User_info/{participant_number}.json"
persona_save_path = f"User_info/{participant_number}_Per.json"
persona = create_persona(user_info_path, persona_save_path)