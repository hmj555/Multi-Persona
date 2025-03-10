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
    Based on the user's role, original episodes (Ep1 & Ep2), and retrieved real-world experiences(Others' experiences), generate two realistic episodes.
    
    - Use the provided context to enrich and enhance the episodes (you can weave context). 
    - Maintain the user's original personality and tendencies.
    - Generate episodes that could shape the user's character and worldview.
    - The generated episodes should be somewhat distinct from the original episodes.
    - Keep the episodes practical and concise.
    - Ensure all outputs are in Korean.

    Role: {role}
    Episode 1: {episode1}
    Episode 2: {episode2}
    Context:
    {retrieved_experiences}
    
    Example Output (if Role: 첫째딸):
    한국의 전형적인 첫째 딸로서 고등학생이 된 나는 여전히 집안일에서 자유롭지 않았다. 어느 날, 피곤한 하루를 마치고 돌아온 나는 어머니가 \"오늘 저녁은 네가 준비해야겠구나\"라고 말씀하시는 것을 듣고 잠시 멍해졌다. 하지만 곧이어 '착한 딸'이 되어야 한다는 무언의 압박감에 저녁 준비를 했다. 그런 나의 모습을 보며 어머니는 \"네가 있어서 정말 든든하다\"라고 칭찬하셨지만, 나는 그 말이 어쩐지 공허하게 느껴졌다."
    대학에 진학한 후, 나는 다양한 사람들과의 관계 속에서 나의 양면성을 더욱 절실히 느끼게 되었다. 수업 중 조별 과제를 할 때, 의견 충돌이 생기면 나는 항상 중재자가 되었다. '모두가 잘 지내야 한다'는 마음으로 항상 타인의 의견을 먼저 수용하려 했지만, 시간이 지날수록 나만의 색이 사라지는 것 같았다.

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