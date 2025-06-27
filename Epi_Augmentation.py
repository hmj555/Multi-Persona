import json
import os
from collections import defaultdict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


participant_number = "P0"


# OpenAI 모델 설정
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8)

# ✅ 개선된 Action Patterns 추론 프롬프트
experience_augmentation_prompt = PromptTemplate.from_template(
"""
Generate a new experience for the user based on the instructions below.
1st. Understand Context 1 and Context 2.
2nd. Understand the user by referring to their basic information, roles, and original experience.
3rd. Based on Context 1 and Context 2, generate a plausible experience that the user might have gone through.
- You may refer to the user's basic information and roles when generating the experience.
- The generated experience must be differentiated from the original experience in terms of both situation and content.
- The generated experience should allow for inference of the user's personality, values, and internal state.
- Keep the generated experience realistic, practical and concise.
- All output must be provided in Korean.
Output Examples:
- 무기력하고 우울한 순간도 있었고, 완전히 실패한 사람처럼 느껴지기도 했습니다. 하지만 이러한 경험을 통해 저와 마찬가지로 힘든 시기를 겪고 있는 주변 사람들에 대한 공감을 키울 수 있었습니다. 이렇게 힘든 순간을 직접 경험한 것이 인간관계에 있어 소중한 자산이라는 것을 깨달았습니다. 제가 겪은 일 덕분에 이제는 주변에서 힘들어하는 사람들이 저에게 기댈 수 있고, 제가 그들에게 힘이 되어줄 수 있기를 바랍니다.
- 속상한 일이 있었던 날, 우리 가족은 외식을 하러 나갔어요. 동생이 기분이 좋지 않아 퉁명스럽게 말했고 어색한 침묵이 식당에 가득 찼습니다. 제 마음도 복잡했지만 분위기를 밝게 하려고 노력했습니다. 저는 제 감정보다 다른 사람의 감정을 먼저 알아차리는 버릇이 있어요. 사람들은 종종 제가 성숙하다고 말하지만, 가끔은 제 감정을 억누르는 데 너무 익숙해진 건 아닌가 하는 생각이 들기도 합니다.
    
    Role: {role}
    Episode 1: {episode1}
    Episode 2: {episode2}
    Context:
    {retrieved_experiences}
    
    Augmented Episodes:
"""
)

llm_chain = LLMChain(llm=llm, prompt=experience_augmentation_prompt)

def compile_retrieved_experiences(role, contexts):
    """🔹 Role과 연관된 웹 검색 경험을 하나의 텍스트로 합침"""
    summaries = []
    for context in contexts:
        url = context["url"]
        content = context["content"]
        summaries.append(f"[출처: {url}] {content[:300]}")  # 300자 제한
    return "\n".join(summaries)


def generate_augmented_experiences(role, episode1, episode2, retrieved_experiences):
    """🔹 LLM을 사용하여 에피소드 증대 수행"""
    response = llm_chain.invoke({
        "role": role,
        "episode1": episode1,
        "episode2": episode2,
        "retrieved_experiences": retrieved_experiences
    })
    episodes = response["text"].strip().split("\n")
    return [ep.strip("- ") for ep in episodes if ep.strip()]  # 리스트 정리


# 🔹 User_Context/P0.json 불러오기
context_filepath = f"User_Context/{participant_number}.json"
with open(context_filepath, "r", encoding="utf-8") as file:
    user_context = json.load(file)
    
# ✅ User_Query/P0.json 불러오기
query_filepath = f"User_Query/{participant_number}.json"
with open(query_filepath, "r", encoding="utf-8") as file:
    user_query = json.load(file)

# 🔹 User_Info/P0.json 불러오기
user_info_filepath = f"User_info/{participant_number}.json"
with open(user_info_filepath, "r", encoding="utf-8") as file:
    user_info = json.load(file)

# ✅ Role별 검색된 경험 저장
role_experiences = defaultdict(list)

for context_data in user_context["context"]:
    role = context_data["role"]
    role_experiences[role].append({
        "url": context_data["url"],
        "content": context_data["content"]
    })
    
# ✅ User_Query에서 masked_episode 가져오기
role_masked_episodes = defaultdict(list)

for query_entry in user_query["queries"]:
    role = query_entry["role"]
    masked_episode = query_entry["masked_episode"]
    role_masked_episodes[role].append(masked_episode)

# ✅ Role과 연결된 검색 경험 기반으로 Augmentation 수행
for role_key, role_data in user_info["Episode"].items():
    role = role_data["Role"]
    
    # ✅ Ep1, Ep2 가져오기 (masked_episode 사용)
    masked_episodes = role_masked_episodes.get(role, ["", ""])
    episode1 = masked_episodes[0] if len(masked_episodes) > 0 else ""
    episode2 = masked_episodes[1] if len(masked_episodes) > 1 else ""
    
    # ✅ 같은 Role의 검색된 경험 가져오기
    retrieved_experiences = compile_retrieved_experiences(role, role_experiences.get(role, []))
        
    if retrieved_experiences and episode1 and episode2:  # 검색된 경험과 에피소드가 있을 때 실행
        augmented_episodes = generate_augmented_experiences(role, episode1, episode2, retrieved_experiences)

        # ✅ User_Info/P0.json에 Experiencable 추가
        role_data["Experiencable"] = augmented_episodes  
        print(f"✅ {role}의 Experiencable Episodes 추가 완료")

# ✅ JSON 파일로 저장
with open(user_info_filepath, "w", encoding="utf-8") as file:
    json.dump(user_info, file, indent=4, ensure_ascii=False)

print("🎯 Episode Augmentation 완료 & 저장:", user_info_filepath)


##### ===== Persona 생성 ===== #####
def create_persona(user_info_path, user_query_path, save_path):
    """🔹 User_Info.json과 User_Query.json을 기반으로 페르소나 생성 및 저장"""

    # ✅ User_Info 불러오기
    with open(user_info_path, "r", encoding="utf-8") as file:
        user_info = json.load(file)

    # ✅ User_Query 불러오기
    with open(user_query_path, "r", encoding="utf-8") as file:
        user_query = json.load(file)

    # ✅ 기본 정보 저장
    persona = {
        "Base Information": {
            "Age": user_info["Age"],
            "Gender": user_info["Gender"],
            "Job": user_info["Job"],
            "Major": user_info["Major"],
            "MBTI": user_info["MBTI"]
        },
        "Identities": {},
        "Experiencable": {}
    }

    # ✅ Role별 `masked_episode` 저장
    role_masked_episodes = defaultdict(list)
    for query_entry in user_query["queries"]:
        role = query_entry["role"]
        masked_episode = query_entry["masked_episode"]
        role_masked_episodes[role].append(masked_episode)

    # ✅ Role & Episode 저장 (`masked_episode` 활용)
    for role_key, role_data in user_info["Episode"].items():
        role = role_data["Role"]
        
        # ✅ Ep1, Ep2 가져오기 (masked_episode 사용)
        masked_episodes = role_masked_episodes.get(role, ["", ""])
        episode1 = masked_episodes[0] if len(masked_episodes) > 0 else ""
        episode2 = masked_episodes[1] if len(masked_episodes) > 1 else ""
        
        # ✅ Experiencable(증대된 에피소드) 가져오기
        experiencable_episodes = role_data.get("Experiencable", [])

        # ✅ 데이터 저장
        persona["Identities"][role] = {
            "Ep1": episode1,
            "Ep2": episode2
        }
        persona["Experiencable"][role] = experiencable_episodes

    # ✅ JSON으로 저장
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(persona, file, indent=4, ensure_ascii=False)

    print("✅ 페르소나 생성 완료 & 저장:", save_path)
    return persona

user_info_path = f"User_info/{participant_number}.json"
user_query_path = f"User_Query/{participant_number}.json"
persona_save_path = f"User_info/{participant_number}_Per.json"
persona = create_persona(user_info_path, user_query_path,  persona_save_path)



### ==== 테스트 코드 ==== ###
def test_manual_augmentation():
    role = "시골 출생자"
    episode1 = "나는 작은 시골 마을에서 자라며, 그곳이 사랑스럽지만 동시에 답답하게 느껴졌다."
    episode2 = "처음으로 친구들과 외국의 대도시로 여행을 떠나면서, 부모님의 간섭 없이 내 용돈과 선택으로 이루어진 자유로운 여행을 통해 도시 여행의 매력을 깊이 느끼고 사랑하게 되었다."
    
    retrieved_experiences = """
    현대에 널리 받아들여지는 성격모형인 Big5에서 외향성은 따뜻함, 사교성, 자신감, 활기, 자극 추구, 긍정적 정서의 여섯 가지 하위 측면(facets)들로 구성되어 있다. 외향적인 사람들은 '친근함', '사교성', '활동적' 등 단어들로 성격 특성들을 정리할 수 있다.
    """

    print(f"🎯 Role: {role}")
    print(f"🎯 Episode 1: {episode1}")
    print(f"🎯 Episode 2: {episode2}")
    print(f"🎯 Context: \n{retrieved_experiences}")

    augmented_episodes = generate_augmented_experiences(role, episode1, episode2, retrieved_experiences)

    # ✅ 결과 저장
    test_output_path = f"Test_Augmentation/{participant_number}_test.json"
    os.makedirs(os.path.dirname(test_output_path), exist_ok=True)

    test_data = {
        "role": role,
        "episode1": episode1,
        "episode2": episode2,
        "retrieved_experiences": retrieved_experiences,
        "augmented_episodes": augmented_episodes
    }

    with open(test_output_path, "w", encoding="utf-8") as file:
        json.dump(test_data, file, indent=4, ensure_ascii=False)

    print(f"\n✅ 증대된 에피소드 생성 완료 & 저장: {test_output_path}")
    print("\n=== Augmented Episodes ===")
    for i, ep in enumerate(augmented_episodes, 3):
        print(f"Ep{i}: {ep}")

##### 🔹 테스트 실행
if __name__ == "__main__":
    test_manual_augmentation()