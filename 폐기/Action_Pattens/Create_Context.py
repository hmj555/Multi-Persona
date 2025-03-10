import os
import json
import requests
from langchain_community.utilities import GoogleSerperAPIWrapper
import time
import random


participant_number = "P0"

# ✅ 1. User_Query/P0.json에서 Query 가져오기
query_file = f"User_Query/{participant_number}.json"
with open(query_file, "r", encoding="utf-8") as f:
    user_queries = json.load(f)

# ✅ 2. 외부 Retriever (Google Scholar or Serper.dev)에서 검색
os.environ["SERPER_API_KEY"] = "8f1eea61a5aa20e026ffa5e57fb0604a618a1c71"
retriever = GoogleSerperAPIWrapper(
    serper_api_key=os.getenv("SERPER_API_KEY"), 
    gl="us", hl="en", k=5, type="search"
)

user_context = {"queries": []}

for query_data in user_queries["queries"]:
    role = query_data["role"]
    
    i = random.randint(0,2)
    query_text = query_data["expanded_queries"][i]  # ✅ 첫 번째 확장된 쿼리 사용

    search_results = retriever.results(query_text)
    papers = search_results.get("organic", [])  # 검색된 논문 리스트

    paper_data = []
    for paper in papers:
        title = paper.get("title", "No title")
        link = paper.get("link", "")
        snippet = paper.get("snippet", "No snippet available")  # ✅ 검색 결과 요약문 추가

        # ✅ 3. CrossRef에서 DOI 추출
        doi = None
        crossref_url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        crossref_res = requests.get(crossref_url).json()

        if "message" in crossref_res and "items" in crossref_res["message"]:
            doi = crossref_res["message"]["items"][0].get("DOI", None)
            time.sleep(1)
        print("DOI:", doi)
        

        # ✅ 4. Semantic Scholar에서 초록 가져오기
        abstract = None
        if doi:
            sem_scholar_url = f"https://api.semanticscholar.org/v1/paper/{doi}"
            sem_res = requests.get(sem_scholar_url).json()
            abstract = sem_res.get("abstract", None)
            time.sleep(1)

        # ✅ 5. Abstract 저장 + Snippet 항상 포함
        paper_data.append({
            "title": title,
            "link": link,
            "doi": doi,
            "abstract": {
                "content": abstract if abstract else "No abstract available",
                "snippet": snippet  # ✅ snippet도 함께 저장
            }
        })
        print(f"📌 Title: {title}")
        print(f"🔗 DOI: {doi}")
        print(f"📝 Abstract: {abstract if abstract else 'No abstract available'}")
        print(f"📑 Snippet: {snippet}")

    user_context["queries"].append({
        "role": role,
        "query": query_text,
        "papers": paper_data
    })
    print("✅ Context 생성 완료")

# ✅ 결과를 User_Context/P0.json에 저장
output_file = f"User_Context/{participant_number}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(user_context, f, ensure_ascii=False, indent=4)

print(f"✅ User_Context/{participant_number}.json에 저장 완료!")
