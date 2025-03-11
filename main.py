from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from datetime import datetime
import os
import json
from typing import Dict

from ChatAgent_Tag import chat as chat_tag
from ChatAgent_Tag import chat as chat_tag_stream
from ChatAgent_Epi import chat as chat_epi
from ChatAgent_Epi import chat as chat_epi_stream

app = FastAPI()

# ✅ CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 가능
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

################## 1. Intro.js에서 받아오는 정보 ##################

# 데이터 경로 설정
USER_INFO_DIR = "User_info"
USER_QUERY_DIR = "User_Query"

# 입력 데이터 모델 정의
class ParticipantInput(BaseModel):
    participant_id: str  # 예: P50

@app.post("/submit")
async def submit_participant(input_data: ParticipantInput):
    participant_id = input_data.participant_id.strip()

    if not participant_id.startswith("P"):
        raise HTTPException(status_code=400, detail="잘못된 참가자 번호 형식입니다. 예: P50")

    input_filepath = f"{USER_INFO_DIR}/{participant_id}.json"
    output_filepath = f"{USER_QUERY_DIR}/{participant_id}.json"

    if not os.path.exists(input_filepath):
        raise HTTPException(status_code=404, detail=f"{input_filepath} 파일이 존재하지 않습니다.")

    # ✅ 터미널에 로그 출력
    print(f"[INFO] 파일 경로 설정됨: {input_filepath} → {output_filepath}")
    print(f"[INFO] 파일 경로 설정됨: User_Info, {participant_id} : {input_filepath}")
    print(f"[INFO] 파일 경로 설정됨: User_Query, {participant_id} : {output_filepath}")

    return {
        "message": "파일 경로가 설정되었습니다.",
        "input_filepath": input_filepath,
        "output_filepath": output_filepath
    }


################## 2. Info.js에서 받아오는 정보 ##################
USER_INFO_DIR = "User_info"
os.makedirs(USER_INFO_DIR, exist_ok=True)

# Pydantic 데이터 모델 정의
class UserInfo(BaseModel):
    Age: str
    Gender: str
    Job: str
    Major: str
    MBTI: str
    Self_tag: str
    Episode: dict  # Role과 에피소드 포함

@app.post("/save_user_info/{participant_id}")
async def save_user_info(participant_id: str, user_data: dict):
    try:
        print(f"📡 [SERVER] 데이터 저장 요청 받음: {participant_id}")
        print(f"🔍 [DEBUG] user_data: {json.dumps(user_data, ensure_ascii=False, indent=4)}")

        # 저장할 경로 설정
        save_path = f"User_info/{participant_id}.json"

        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # JSON 파일로 저장
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)

        print(f"✅ [SUCCESS] {participant_id}.json 저장 완료")
        return {"message": f"User data saved successfully: {participant_id}"}

    except Exception as e:
        print(f"🚨 [ERROR] 파일 저장 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")


################## 3. Topic.js에서 받아오는 정보 ##################
TOPICS_FILE = "topics.json"
with open(TOPICS_FILE, "r", encoding="utf-8") as f:
    TOPICS_DATA = json.load(f)

@app.post("/save_selected_topics/{participant_id}")
async def save_selected_topics(participant_id: str, selected_topics: dict):
    try:
        print(f"📡 [SERVER] 선택된 토픽 저장 요청 받음: {participant_id}")
        print(json.dumps(selected_topics, indent=4, ensure_ascii=False))

        # 저장 경로 설정
        save_path = f"User_Topics/{participant_id}.json"

        # 디렉토리 생성 (없을 경우)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # ✅ 추가: topics.json에서 description_ko 찾기
        def get_topic_description(title_ko):
            for topic in TOPICS_DATA:
                if topic["title_ko"] == title_ko:
                    return topic["description_ko"]
            return "설명 없음"  # 기본값

        # ✅ 토픽 설명 추가
        selected_topics["tag_topic_descriptions"] = [get_topic_description(topic) for topic in selected_topics["tag_topics"]]
        selected_topics["epi_topic_descriptions"] = [get_topic_description(topic) for topic in selected_topics["epi_topics"]]

        # ✅ JSON 파일로 저장
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(selected_topics, f, ensure_ascii=False, indent=4)

        print(f"✅ [SUCCESS] {participant_id}의 선택된 토픽이 저장되었습니다.")
        return {"message": f"{participant_id}의 선택된 토픽이 저장되었습니다."}

    except Exception as e:
        print(f"🚨 [ERROR] 파일 저장 중 오류 발생: {e}")
        return {"error": str(e)}
    
########### 4. Chat.js에서 불러오는 정보 ###########
@app.get("/get_user_topics/{participant_id}")  # ✅ 올바른 엔드포인트
def get_user_topics(participant_id: str):
    file_path = f"User_Topics/{participant_id}.json"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            topics_data = json.load(f)
        return topics_data  # ✅ JSON 데이터를 반환
    except FileNotFoundError:
        return {"error": "해당 참가자의 토픽 데이터가 없습니다."}
    
########### 5. Chat.js에서 메시지 ###########

# class ChatRequest(BaseModel):
#     user_number: str
#     session_id: str
#     input_text: str
#     topic: str

# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     """사용자의 입력을 받아 AI 응답을 반환하는 엔드포인트"""
#     try:
#         # ✅ ChatAgent_Tag.py에서 chat() 함수 호출 (AI 응답 생성)
#         ai_response = chat(
#             user_number=request.user_number,
#             input_text=request.input_text,
#             session_id=request.session_id,
#             # persona_type=request.persona_type
#         )
#         return {"response": ai_response}

#     except Exception as e:
#         return {"error": str(e)}

# ✅ ChatAgent_Tag.py 실행 엔드포인트
# ✅ AI 응답을 스트리밍 방식으로 보내는 엔드포인트

class ChatRequest(BaseModel):
    user_number: str
    session_id: str
    input_text: str
    persona_type: str
    
# ✅ FastAPI에서 직접 OpenAI API의 응답을 스트리밍 처리
@app.post("/chat_tag_stream")
async def chat_with_tag_stream(request: ChatRequest):
        return StreamingResponse(
        chat_tag_stream(
            user_number=request.user_number,
            input_text=request.input_text,
            session_id=request.session_id
        ),
        media_type="text/event-stream"
    )
        
@app.post("/chat_epi_stream")
async def chat_with_epi_stream(request: ChatRequest):
    return StreamingResponse(
        chat_epi_stream(
            user_number=request.user_number,
            input_text=request.input_text,
            session_id=request.session_id
        ),
        media_type="text/event-stream"  # ✅ 이벤트 스트리밍 형식 사용
    )

# @app.post("/chat_tag")
# async def chat_with_tag(request: ChatRequest):
#     try:
#         print(f"📌 [DEBUG] 서버에서 받은 topic: {request.topic}")  # ✅ FastAPI에서 topic을 정상적으로 받는지 확인
        
#         ai_response = chat_tag(
#             user_number=request.user_number,
#             input_text=request.input_text,
#             session_id=request.session_id,
#             # topic=request.topic
#         )
#         return {"response": ai_response}
#     except Exception as e:
#         return {"error": str(e)}

# ✅ ChatAgent_Epi.py 실행 엔드포인트
@app.post("/chat_epi")
async def chat_with_epi(request: ChatRequest):
    try:
        print(f"📌 [DEBUG] 서버에서 받은 topic: {request.topic}")  # ✅ FastAPI에서 topic을 정상적으로 받는지 확인
        
        ai_response = chat_epi(
            user_number=request.user_number,
            input_text=request.input_text,
            session_id=request.session_id,
            # topic=request.topic
        )
        return {"response": ai_response}
    except Exception as e:
        return {"error": str(e)}

# ✅ User_Topics 폴더에서 특정 참가자의 토픽 가져오기
def get_user_topics(user_number):
    topics_path = f"User_Topics/{user_number}.json"
    if not os.path.exists(topics_path):
        raise HTTPException(status_code=404, detail="User topics not found")
    
    with open(topics_path, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    return topics_data.get("persona1", [])  # "persona1" 키의 리스트 반환

# ✅ src/data/topics.json에서 topic에 맞는 description 가져오기
def get_topic_description(topic):
    topics_path = "topics.json"
    if not os.path.exists(topics_path):
        raise HTTPException(status_code=404, detail="Topics data not found")
    
    with open(topics_path, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    for t in topics_data:
        if t["title_ko"] == topic:
            return t.get("description_en", "No description available")
    
    return "No description available"

# ✅ 프론트엔드에서 요청 시 topic과 topic_description 반환
@app.get("/get_chat_topic/{user_number}/{chat_id}")
async def get_chat_topic(user_number: str, chat_id: int):
    topics = get_user_topics(user_number)

    if chat_id < 1 or chat_id > len(topics):
        topic = "자유 주제"
    else:
        topic = topics[chat_id - 1]  # chatId는 1-based index이므로 -1 처리

    topic_description = get_topic_description(topic)

    return {"topic": topic, "topic_description": topic_description}

class ChatLogRequest(BaseModel):
    user_number: str
    session_id: str
    messages: list

@app.post("/save_chat_log")
async def save_chat_log(request: ChatLogRequest):
    """대화 로그를 JSON 파일로 저장"""
    save_dir = f"User_ChatLog/{request.user_number}_Tag/{request.session_id}"
    os.makedirs(save_dir, exist_ok=True)  # 폴더 생성

    file_path = os.path.join(save_dir, f"{request.session_id}.json")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(request.messages, f, ensure_ascii=False, indent=4)
    
    return {"message": "😀대화 로그가 저장되었습니다."}

class SurveyRequest(BaseModel):
    user_number: str
    session_id: str
    responses: dict

@app.post("/submit_survey")
async def submit_survey(request: SurveyRequest):
    print(f"설문 제출: {request}")
    return {"message": "설문이 성공적으로 저장되었습니다."}


####### ===== 에피소드 평가 ====== #######
# ✅ 참가자의 에피소드 데이터를 가져오는 API
@app.get("/get_experiencable/{participant_id}")
async def get_experiencable(participant_id: str):
    file_path = f"User_info/{participant_id}_Per.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {"Experiencable": data.get("Experiencable", {})}

class EpiEvalRequest(BaseModel):
    user_number: str
    responses: Dict[str, int]

# ✅ 설문 데이터를 받는 엔드포인트
@app.post("/submit_epi_eval")
async def submit_epi_eval(request: EpiEvalRequest):
    try:
        save_path = f"User_EpiEval/{request.user_number}.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # ✅ 폴더 자동 생성

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(request.dict(), f, ensure_ascii=False, indent=4)

        return {"message": "설문 데이터 저장 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
# ✅ 기존 경험을 가져오는 엔드포인트 
@app.get("/get_identity/{user_id}")
def get_identity(user_id: str):
    file_path = f"User_info/{user_id}_Per.json"
    
    # ✅ 파일이 존재하지 않으면 404 에러 반환
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일 없음")
    
    # ✅ 파일이 존재하면 JSON 로드
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {"Identities": data.get("Identities", {})}


##### ==== 로그 저장 ===== #####
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class LogEvent(BaseModel):
    participantId: str
    page: str
    button: str
    timestamp: str

@app.post("/log_event")
async def log_event(event: LogEvent):
    """버튼 클릭 로그 저장"""
    log_path = os.path.join(LOG_DIR, f"{event.participantId}_events.json")
    
    # 기존 로그 불러오기
    logs = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    
    logs.append(event.dict())

    # 로그 저장
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

    return {"message": "로그 저장 완료"}

class SurveyLog(BaseModel):
    participantId: str
    page: str
    chatId: int
    topic: str
    timestamp: str
    responses: dict

@app.post("/log_survey")
async def log_survey(survey: SurveyLog):
    """설문 응답 로그 저장"""
    log_path = os.path.join(LOG_DIR, f"{survey.participantId}_survey.json")
    
    # 기존 로그 불러오기
    logs = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    
    logs.append(survey.dict())

    # 로그 저장
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

    return {"message": "설문 응답 저장 완료"}
