# Generate Scenarios
# env: AIInterviewer

import openai ; import os
import pandas as pd; import openpyxl
openai.api_key = os.environ.get('OPENAI_API_KEY')

import openai
import os
import pandas as pd ; import re
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from umato import UMATO


# 층화 샘플링을 위한 초기 시나리오
initial_scenarios = [
    ("Emotional support", "Advice on romantic relationships", "Users facing romantic troubles talk with a conversational agent. In response, the agent offers understanding and tips for maintaining a healthy relationship."),
    ("Emotional support", "Talking About Self-compassion", "When users are too hard on themselves, a conversational agent encourages them to be kinder to themselves and offers ways to practice self-esteem."),
    ("Emotional support", "Discussions on sleep issues", "Users having trouble sleeping want to talk with a conversational agent for understanding and suggestions on how to sleep better."),
    ("Emotional support", "Managing nightmares", "For users bothered by bad dreams, a conversational agent offers comfort and suggestions on managing them better"),
    ("Emotional support", "Overcoming fear of failure", "A chatbot assists users struggling with a fear of failure by sharing stories of resilience, encouraging a growth mindset, and suggesting small achievable steps."),
    ("Appraisal support", "Evaluating and building leadership skills", "Users who want to be better leaders discuss leadership styles, effective leadership practices, and ways to improve leadership with a conversational agent."),
    ("Appraisal support", "Improving problem-solving skills", "Users discuss with a conversational agent how to think more logically and make better decisions."),
    ("Appraisal support", "Assessing my Skills and personal growth", "Users want to earn feedback on their academic or job skills by chatting with conversational agents. Users especially want to figure out strengths, areas to work on, and goals for personal growth."),
    ("Appraisal support", "Boosting Project management skills", "Users chat with a conversational agent about how to manage projects better, from scheduling to working well with a team."),
    ("Appraisal support", "Reviewing financial decisions", "Users review their financial planning with a chatbot that provides insights on budgeting, investment strategies, and risk management.")
]

# GPT-4o 기반 추가 시나리오 생성 (25개씩 20회 실행 = 500개)
generated_scenarios = []

# Define the prompt for the model (with examples)
prompt = """
You are a highly skilled AI trained in user modeling and chatbot scenario generation.

## Task:
Generate 25 new situational scenarios each for Emotional support and Appraisal support.

## Examples:
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
1. Generate 50 unique scenarios for Emotional support.
2. Generate 50 unique scenarios for Appraisal support.
3. Each scenario should be unique, practical, and aligned with real-world use cases.
4. Follow the output format exactly as shown in the examples.
5. Do not repeat the examples provided—create entirely new ones.

## Output:
"""

## 수정
for _ in range(1):  # 20회 실행 = 500개 생성
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,  # 다양성 확보
        max_tokens=4000
    )

    # 파싱
    response_text = response["choices"][0]["message"]["content"]
    scenarios = [line.split(";", 2) for line in response_text.strip().split("\n")]
    generated_scenarios.extend(scenarios)
    
len(generated_scenarios)

# 초기 시나리오 + GPT-4o 생성 시나리오 통합
all_scenarios = initial_scenarios + generated_scenarios

# 층화 샘플링: 랜덤하게 10개씩 선택하여 99회 반복 (총 1,000개 구축)
final_scenarios = []
for _ in range(5): ## 수정
    sampled = random.sample(all_scenarios, 10)
    final_scenarios.extend(sampled)

# DataFrame 변환
df = pd.DataFrame(final_scenarios, columns=["Topic", "Situation", "Description"])
# 숫자 제거하여 Topic 정리
df["Topic"] = df["Topic"].apply(lambda x: re.sub(r"^\d+\.\s*", "", str(x)) if pd.notna(x) else x)
df_cleaned = df.dropna().reset_index(drop=True)
df_cleaned = df_cleaned.drop_duplicates(subset=["Situation", "Description"]).reset_index(drop=True)
print(df_cleaned)
df = df_cleaned
len(df)

# 정리된 데이터 저장
Emo = df[df["Topic"] == "Emotional support"]
App = df[df["Topic"] == "Appraisal support"]
Emo
App
# Save to Excel
i=1
i = i+1
file_path_emo = f"scenario/Emo_scene_{i}.xlsx"
file_path_app = f"scenario/App_scene_{i}.xlsx"
Emo.to_excel(file_path_emo, index=False)
App.to_excel(file_path_app, index=False)

print(f"✅ 정리된 데이터 저장 완료: {file_path_emo}, {file_path_app}")

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

if num_samples < 10:
    print("⚠️ 데이터 개수가 너무 적습니다. 최소 10개 이상의 데이터가 필요합니다.")
    
hub_num = min(num_samples // 2, 30)  # 데이터 개수의 절반 또는 30 중 작은 값
n_neighbors = min(num_samples // 3, 10) 

# 🔹 차원 축소 (UMATO vs UMAP vs t-SNE 비교)

# ✅ UMATO 실행
umato = UMATO(n_components=2, hub_num=hub_num, n_neighbors=n_neighbors, random_state=42)
reduced_data = umato.fit_transform(embedding_matrix)
print(f"Reduced data shape: {reduced_data.shape}")

umato = UMATO(n_components=2, random_state=42)
reduced_data = umato.fit_transform(embedding_matrix)

umato = UMATO(n_components=2, hub_num=min(embedding_matrix.shape[0] // 2, 30), random_state=42)
reduced_data = umato.fit_transform(embedding_matrix)


# 🔹 차원 축소 결과 시각화
from matplotlib import rc 
rc('font', family='AppleGothic') 
plt.figure(figsize=(8,6))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1])
plt.title("UMATO 차원 축소 결과")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.show()

# 🔹 최적 k 값 찾기
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

# 🔹 k-Means 클러스터링 실행 (기본값 k=4)
optimal_k = 4  # Elbow Method 결과 기반으로 선택
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df["Cluster"] = kmeans.fit_predict(reduced_data)

# 🔹 결과 데이터 저장
output_path = "scenario_analysis.xlsx"
df.to_excel(output_path, index=False)
print(f"✅ 시나리오 분석 완료! 파일 저장: {output_path}")








# Define the prompt for the model
prompt ="""
You are a highly skilled AI trained in user modeling and chatbot scenario generation. 

Task:
Generate 10 new situational scenarios each for Emotional support and Appraisal support in the format below.

Examples:
Informational support;Understanding company culture;Users want to get the feel of a company’s culture. A conversational agent helps by talking about the basics of corporate culture, what’s unique to that company, and how to research more about it.
Informational support;Exploring recipes;Users keen on trying new dishes while chatting with a conversational agent about cooking methods, ingredients, and handy cooking tips.
Emotional support;Advice on romantic relationships;Users facing romantic troubles talk with a conversational agent. In response, the agent offers understanding and tips for maintaining a healthy relationship.
Emotional support;Talking About Self-compassion;When users are too hard on themselves, a conversational agent encourages them to be kinder to themselves and offers ways to practice self-esteem.
Appraisal support;Evaluating and building leadership skills;Users who want to be better leaders discuss leadership styles, effective leadership practices, and ways to improve leadership with a conversational agent.
Appraisal support;Improving problem-solving skills;Users discuss with a conversational agent how to think more logically and make better decisions.

Output Format:
topic;situation;description

Instructions:
1. Generate 50 unique situational scenarios for **Emotional support**.
2. Generate 50 unique situational scenarios for **Appraisal support**.
3. Ensure each scenario is distinct, practical, and aligned with real-world use cases.
4. Follow the exact output format as shown in the examples.
5. Do not repeat the examples provided—create entirely new ones.

Output:
"""

os.makedirs("scenario", exist_ok=True)

for i in range(1, 11):
    print(f"Generating batch {i}...")

    # Call the model
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an expert in chatbot scenario generation."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000  # Increased max tokens to generate more data
    )

    # Extract response text
    response_text = response["choices"][0]["message"]["content"]

    # Output Parsing
    data = [line.split(";", 2) for line in response_text.strip().split("\n")]
    df = pd.DataFrame(data, columns=["Topic", "Situation", "Description"])

    # Separate Emotional & Appraisal support scenarios
    Emo = df[df["Topic"] == "Emotional support"]
    App = df[df["Topic"] == "Appraisal support"]

    # Save to Excel
    file_path_emo = f"scenario/Emo_scene_{i}.xlsx"
    file_path_app = f"scenario/App_scene_{i}.xlsx"
    Emo.to_excel(file_path_emo, index=False)
    App.to_excel(file_path_app, index=False)

    print(f"Batch {i} saved: {file_path_emo}, {file_path_app}")

print("Scenario generation completed.")









final_scenarios = []
for _ in range(99):
    sampled = random.sample(all_scenarios, 10)
    final_scenarios.extend(sampled)

# 🔹 DataFrame 변환
df = pd.DataFrame(final_scenarios, columns=["Topic", "Situation", "Description"])

# 🔹 OpenAI text-embedding-ada-002 활용한 벡터 임베딩 생성
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

df["Embedding"] = df["Description"].apply(get_embedding)

# 🔹 임베딩 데이터 추출
embedding_matrix = np.vstack(df["Embedding"].values)

# 🔹 차원 축소 (UMATO vs UMAP vs t-SNE 비교)
umato = UMATO(n_components=2, random_state=42)
reduced_data = umato.fit_transform(embedding_matrix)

# 🔹 차원 축소 결과 시각화
plt.figure(figsize=(8,6))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1])
plt.title("UMATO 차원 축소 결과")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.show()

# 🔹 최적 k 값 찾기 (Elbow Method)
inertia_values = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(reduced_data)
    inertia_values.append(kmeans.inertia_)

plt.figure(figsize=(8,6))
plt.plot(range(2, 11), inertia_values, marker='o')
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method for Optimal k")
plt.show()

# 🔹 k-Means 클러스터링 실행 (기본값 k=4)
optimal_k = 4  # Elbow Method 결과 기반으로 선택
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df["Cluster"] = kmeans.fit_predict(reduced_data)

# 🔹 결과 데이터 저장
output_path = "scenario_analysis.xlsx"
df.to_excel(output_path, index=False)
print(f"✅ 시나리오 분석 완료! 파일 저장: {output_path}")