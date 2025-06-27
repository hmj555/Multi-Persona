from langchain_community.tools import TavilySearchResults
import json
import os
from dotenv import load_dotenv

user_number = "P0"

load_dotenv()  # ✅ .env 파일 로드
api_key = os.getenv("TAVILY_API_KEY")

# ✅ Tavily API 설정 (블로그 및 커뮤니티 검색 우선)
tavily_tool = TavilySearchResults(
    tavily_api_key=api_key,
    max_results=1,  # ✅ 최대 검색 결과 개수 조정
    include_answer=True,  # ✅ 질문 답변 포함
    include_raw_content=True,  # ✅ 웹 문서 본문 포함
    include_images=False,
)

def search_web(query):
    """🔍 Tavily API를 사용하여 웹 검색 실행"""
    return tavily_tool.invoke({"query": query})  # ✅ 리스트 반환

# ✅ User_Query 불러오기
input_filepath = f"User_Query/{user_number}.json"

with open(input_filepath, "r", encoding="utf-8") as file:
    query_data = json.load(file)

# ✅ 검색 결과 저장 경로
output_filepath = f"User_Context/{user_number}.json"
os.makedirs(os.path.dirname(output_filepath), exist_ok=True)


##### ===== 실행 코드 ===== #####

context_data = {"context": []}
retrieved_urls = set()  # ✅ 중복 방지를 위한 URL 저장

for query_entry in query_data["queries"]:
    role = query_entry["role"]
    masked_experience = query_entry["masked_episode"]  # ✅ Masked Experience 추가
    
    for query in query_entry["expanded_queries"]:
        print(f"🔍 Searching: {query}")
        results = search_web(query)  # ✅ Tavily API 검색 실행

        # ✅ 검색 결과를 순회하며 저장
        for result in results:
            url = result.get("url", "No URL")  # ✅ URL 가져오기
            content = result.get("content", "").strip()  
            snippet = result.get("snippet", "").strip() 

            # ✅ 중복된 URL 방지
            if url in retrieved_urls:
                continue  
            retrieved_urls.add(url)
            
            final_content = content if content else snippet

            # ✅ 결과 저장
            context_data["context"].append({
                "role": role,
                "masked_episode": masked_experience,  
                "query": query,
                "url": url,
                "content": final_content if final_content else "No content available" 
            })

# ✅ JSON 파일로 저장
with open(output_filepath, "w", encoding="utf-8") as file:
    json.dump(context_data, file, indent=4, ensure_ascii=False)

print("✅ 관련 경험 검색 완료 & 저장:", output_filepath)

