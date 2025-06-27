# Generate Scenarios for Appraisal Support
# env: AIInterviewer

import openai
import os
import pandas as pd ; import re
import numpy as np
import random ; import openpyxl
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from umato import UMATO

openai.api_key = os.environ.get('OPENAI_API_KEY')

#################### 1. 시나리오 생성 ####################

# 층화 샘플링을 위한 초기 시나리오(10)
initial_scenarios = [
    ("Appraisal support", "Evaluating and building leadership skills", "Users who want to be better leaders discuss leadership styles, effective leadership practices, and ways to improve leadership with a conversational agent."),
    ("Appraisal support", "Improving problem-solving skills", "Users discuss with a conversational agent how to think more logically and make better decisions."),
    ("Appraisal support", "Assessing my Skills and personal growth", "Users want to earn feedback on their academic or job skills by chatting with conversational agents. Users especially want to figure out strengths, areas to work on, and goals for personal growth."),
    ("Appraisal support", "Boosting Project management skills", "Users chat with a conversational agent about how to manage projects better, from scheduling to working well with a team."),
    ("Appraisal support", "Reviewing financial decisions", "Users review their financial planning with a chatbot that provides insights on budgeting, investment strategies, and risk management."),
    ("Appraisal support", "Evaluating storytelling abilities", "A chatbot guides users in assessing their storytelling skills, offering feedback on narrative and impact."),
    ("Appraisal support", "Enhancing interpersonal skills", "Users seek feedback on their interpersonal interactions from a chatbot, which provides insights on empathy and rapport."),
    ("Appraisal support", "Improving cultural competence", "Users discuss their cultural awareness with a chatbot, receiving feedback on inclusivity and openness."),
    ("Appraisal support", "Evaluating volunteer impact", "A chatbot guides users in assessing their volunteer contributions, offering feedback on community engagement."),
    ("Appraisal support", "Improving agility in decision-making", "Users discuss their agility in decision-making with a chatbot, receiving feedback on flexibility and responsiveness.")
    ]

# GPT-4o 기반 추가 시나리오 생성 (50개씩 10회 실행 = 500개)
generated_scenarios = []

# Define the prompt for the model (with examples)
prompt = """
You are a highly skilled AI trained in user modeling and chatbot scenario generation.

## Task:
Generate 50 new situational scenarios each for Appraisal support.

## Examples:
Informational support;Understanding company culture;Users want to get the feel of a company’s culture. A conversational agent helps by talking about the basics of corporate culture, what’s unique to that company, and how to research more about it
Informational support;Handling Stress;Users look for ways to manage daily stress. A conversational agent shares techniques to relieve stress, advice on mental well-being, and other useful resources.
Informational support;Users keen on trying new dishes while chatting with a conversational agent about cooking methods, ingredients, and handy cooking tips
Informational support;Users plan trips by chatting with conversational about preparing for travel, cool places to visit, food spots to try, and useful local tips.
Emotional support;Advice on romantic relationships;Users facing romantic troubles talk with a conversational agent. In response, the agent offers understanding and tips for maintaining a healthy relationship.
Emotional support;Talking About Self-compassion;When users are too hard on themselves, a conversational agent encourages them to be kinder to themselves and offers ways to practice self-esteem.
Emotional support;Discussions on sleep issues;Users having trouble sleeping want to talk with a conversational agent for understanding and suggestions on how to sleep better.
Emotional support;Managing nightmares;For users bothered by bad dreams, a conversational agent offers comfort and suggestions on managing them better.
Emotional support;Overcoming fear of failure;A chatbot assists users struggling with a fear of failure by sharing stories of resilience, encouraging a growth mindset, and suggesting small achievable steps.
Appraisal support;Evaluating and building leadership skills;Users who want to be better leaders discuss leadership styles, effective leadership practices, and ways to improve leadership with a conversational agent.
Appraisal support;Improving problem-solving skills;Users discuss with a conversational agent how to think more logically and make better decisions.
Appraisal support;Assessing my Skills and personal growth;Users want to earn feedback on their academic or job skills by chatting with conversational agents. Users especially want to figure out strengths, areas to work on, and goals for personal growth.
Appraisal support;Boosting Project management skills;Users chat with a conversational agent about how to manage projects better, from scheduling to working well with a team.
Appraisal support;Reviewing financial decisions;Users review their financial planning with a chatbot that provides insights on budgeting, investment strategies, and risk management.

## Output Format:
topic;situation;description

## Instructions:
1. Generate 50 unique scenarios for Appraisal support.
2. Each scenario should be unique, practical, and aligned with real-world use cases.
3. Follow the output format exactly as shown in the examples.
4. Do not repeat the examples provided—create entirely new ones.

## Output:
"""

for _ in range(10):  # 10회 실행 = 500개 생성 ($0.64 -> $0.79)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,  # 다양성 확보
        max_tokens=4000
    )

    # 파싱
    response_text = response["choices"][0]["message"]["content"]
    scenarios = [line.split(";", 2) for line in response_text.strip().split("\n")]
    print(f"🔹 GPT 응답 개수: {len(scenarios)}")  # 실행마다 몇 개 생성되는지 확인
    generated_scenarios.extend(scenarios)
    
len(generated_scenarios)

# 초기 시나리오 + GPT-4o 생성 시나리오 통합
all_scenarios = initial_scenarios + generated_scenarios
len(all_scenarios)

# DataFrame 변환
df = pd.DataFrame(all_scenarios, columns=["Topic", "Situation", "Description"])
# 숫자 제거하여 Topic 정리
df["Topic"] = df["Topic"].apply(lambda x: re.sub(r"^\d+\.\s*", "", str(x)) if pd.notna(x) else x)
df["Topic"].value_counts()
df = df.loc[df["Topic"] =="Appraisal support"]
df_cleaned = df.dropna().reset_index(drop=True)
df_cleaned = df_cleaned.drop_duplicates(subset=["Situation", "Description"]).reset_index(drop=True)
print(df_cleaned)
df = df_cleaned
len(df) # 471개

# Save to Excel
file_path_app = "scenario/App_scenarios_ori.xlsx"
df.to_excel(file_path_app, index=False)
print(f"✅ 정리된 데이터 저장 완료: {file_path_app}")

#################### 2. 시나리오 분석 ####################

# OpenAI text-embedding-ada-002 활용한 벡터 임베딩 생성
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

df["Embedding"] = df["Description"].apply(get_embedding)

# 임베딩 데이터 추출
embedding_matrix = np.vstack(df["Embedding"].values)

num_samples = embedding_matrix.shape[0]
print(f"Embedding matrix shape: {embedding_matrix.shape}")
    
hub_num = min(num_samples // 2, 30)  
n_neighbors = min(num_samples // 3, 10) 

# 차원 축소 (UMATO)
umato = UMATO(n_components=2, hub_num=hub_num, n_neighbors=n_neighbors, random_state=42)
reduced_data = umato.fit_transform(embedding_matrix)
print(f"Reduced data shape: {reduced_data.shape}")

# 차원 축소 결과 시각화
from matplotlib import rc 
rc('font', family='AppleGothic') 
plt.figure(figsize=(8,6))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1])
plt.title("UMATO 차원 축소 결과 (Appraisal Support)")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.show()

# 최적 k 값 찾기
inertia_values = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(reduced_data)
    inertia_values.append(kmeans.inertia_)

from matplotlib import rc 
rc('font', family='AppleGothic') 
plt.figure(figsize=(8,6))
plt.plot(range(2, 11), inertia_values, marker='o')
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method for Optimal k")
plt.show()

# k-Means 클러스터링 실행
optimal_k = 5  # Elbow Method 결과 기반으로 선택
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df["Cluster"] = kmeans.fit_predict(reduced_data)
df["Cluster"].value_counts()

# 결과 데이터 저장
output_path = "scenario/App_scenarios_clu.xlsx"
df.to_excel(output_path, index=False)
print(f"✅ 시나리오 분석 완료! 파일 저장: {output_path}")



#################### 3. 군집 분석 & 샘플링 ####################
data = pd.read_excel("scenario/App_scenarios_clu.xlsx")
data.head()
data["Cluster"].value_counts()
C0 = data.loc[data["Cluster"] == 0] ; C0
C1 = data.loc[data["Cluster"] == 1] ; C1
C2 = data.loc[data["Cluster"] == 2] ; C2
C3 = data.loc[data["Cluster"] == 3] ; C3
C4 = data.loc[data["Cluster"] == 4] ; C4

C0_sample = C0.sample(5) ; C0_sample
C1_sample = C1.sample(5) ; C1_sample
C2_sample = C2.sample(5) ; C2_sample
C3_sample = C3.sample(5) ; C3_sample
C4_sample = C4.sample(5) ; C4_sample