from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from firebase_utils import db
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

import firebase_admin
from firebase_admin import credentials, firestore
# ✅ Firebase 초기화 (서비스 계정 키 JSON 파일 경로 입력)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
# ✅ Firestore 클라이언트 생성
db = firestore.client()

app = FastAPI()

# ✅ CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://multi-personas-a.vercel.app", "https://multi-personas-b.vercel.app"],  # 프론트엔드 도메인 추가
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




################## 3. Topic.js에서 받아오는 정보 ##################
TOPICS_FILE = "topics.json"
with open(TOPICS_FILE, "r", encoding="utf-8") as f:
    TOPICS_DATA = json.load(f)
    
# ✅ 요청 데이터 모델 정의
class TopicSelection(BaseModel):
    tag_topics: list
    epi_topics: list

# ✅ Firestore에 토픽 저장하는 함수
def save_selected_topics(user_number: str, selected_topics: dict):
    """사용자가 선택한 토픽을 Firestore에 저장"""
    
    # ✅ topics.json에서 description_ko 찾기 함수
    def get_topic_description(title_ko):
        for topic in TOPICS_DATA:
            if topic["title_ko"] == title_ko:
                return topic["description_ko"]
        return "설명 없음"  # 기본값

    # ✅ 토픽 설명 추가
    selected_topics["tag_topic_descriptions"] = [get_topic_description(topic) for topic in selected_topics["tag_topics"]]
    selected_topics["epi_topic_descriptions"] = [get_topic_description(topic) for topic in selected_topics["epi_topics"]]

    # ✅ Firestore에 저장
    db.collection("user_topics").document(user_number).set(selected_topics)

# ✅ FastAPI 엔드포인트: Firestore에 토픽 저장
@app.post("/save_selected_topics/{participant_id}")
async def save_selected_topics_api(participant_id: str, selected_topics: TopicSelection):
    try:
        print(f"📡 [SERVER] 선택된 토픽 저장 요청 받음: {participant_id}")
        print(json.dumps(selected_topics.dict(), indent=4, ensure_ascii=False))

        # ✅ Firestore에 저장
        save_selected_topics(participant_id, selected_topics.dict())

        print(f"✅ [SUCCESS] {participant_id}의 선택된 토픽이 Firestore에 저장되었습니다.")
        return {"message": f"{participant_id}의 선택된 토픽이 Firestore에 저장되었습니다."}

    except Exception as e:
        print(f"🚨 [ERROR] Firestore 저장 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

########### 4. Chat.js에서 불러오는 정보 ###########

from fastapi import HTTPException

@app.get("/get_user_topics/{participant_id}")  
def get_user_topics(participant_id: str):
    """Firestore에서 참가자의 토픽 데이터 가져오기"""
    try:
        # ✅ Firestore에서 해당 참가자의 문서 조회
        doc_ref = db.collection("user_topics").document(participant_id)
        doc = doc_ref.get()

        # ✅ 문서가 존재하면 JSON 반환
        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="해당 참가자의 토픽 데이터가 없습니다.")

    except Exception as e:
        print(f"🚨 [ERROR] Firestore에서 토픽 데이터 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류 발생")

    
########### 5. Chat.js에서 메시지 ###########

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

@app.post("/chat_tag")
async def chat_with_tag(request: ChatRequest):
    try:
        print(f"📌 [DEBUG] 서버에서 받은 topic: {request.topic}")  # ✅ FastAPI에서 topic을 정상적으로 받는지 확인
        
        ai_response = chat_tag(
            user_number=request.user_number,
            input_text=request.input_text,
            session_id=request.session_id,
            # topic=request.topic
        )
        return {"response": ai_response}
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/get_chat_log/{user_number}/{session_id}")
async def get_chat_log(user_number: str, session_id: str):
    """Firebase Firestore에서 채팅 로그 가져오기"""
    doc_ref = db.collection("chat_logs").document(f"{user_number}_{session_id}").set(chat_log)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    else:
        return {"error": "해당 대화 기록이 존재하지 않습니다."}

class ChatLogRequest(BaseModel):
    user_number: str
    session_id: str
    persona_type: str 
    messages: list
    
@app.post("/save_chat_log")
async def save_chat_log(request: ChatLogRequest):
    """Tag와 Epi 대화 로그를 JSON 파일로 저장"""
    
    # ✅ persona_type에 따라 저장 경로 분리
    if request.persona_type not in ["Tag", "Epi"]:
        return {"error": "잘못된 persona_type 입니다. 'Tag' 또는 'Epi' 중 하나여야 합니다."}
    
    save_dir = f"User_ChatLog/{request.user_number}_{request.persona_type}/{request.session_id}"
    os.makedirs(save_dir, exist_ok=True)  # 폴더 생성

    file_path = os.path.join(save_dir, f"{request.session_id}.json")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(request.messages, f, ensure_ascii=False, indent=4)
    
    return {"message": f"✅ {request.persona_type} 대화 로그가 저장되었습니다."}


class SurveyRequest(BaseModel):
    user_number: str
    session_id: str
    responses: dict


@app.post("/submit_survey")
async def submit_survey(request: SurveyRequest):
    try:
        print(f"📩 [SERVER] 설문 제출 요청 받음: {request.user_number}, 세션 {request.session_id}")

        # ✅ Firestore 경로 설정 (logs/user_number/surveys/session_id)
        survey_ref = db.collection("Eval_logs(chat)").document(request.user_number).collection("ChatEval").document(request.session_id)

        # ✅ Firestore에 데이터 저장
        survey_ref.set({
            "user_number": request.user_number,
            "session_id": request.session_id,
            "responses": request.responses,
            "timestamp": datetime.now().isoformat(),  # ✅ 제출 시간 저장
        })

        print(f"✅ [SUCCESS] 설문 데이터가 Firestore에 저장되었습니다: {request.user_number} - 세션 {request.session_id}")
        return {"message": "설문이 성공적으로 저장되었습니다."}

    except Exception as e:
        print(f"🚨 [ERROR] 설문 저장 중 오류 발생: {e}")
        return {"error": str(e)}


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



# ✅ Firestore에 설문 데이터를 저장하는 엔드포인트
@app.post("/submit_epi_eval")
async def submit_epi_eval(request: EpiEvalRequest):
    try:
        # ✅ Firestore 경로 설정
        survey_ref = db.collection("user_surveys").document(request.user_number).collection("evaluations").document(request.session_id)
        
        # ✅ Firestore에 저장할 데이터 구조
        survey_data = {
            "user_number": request.user_number,
            "session_id": request.session_id,
            "responses": request.responses,
            "timestamp": datetime.now().isoformat(),
        }

        # ✅ Firestore에 데이터 저장
        survey_ref.set(survey_data)

        print(f"✅ Firestore에 설문 데이터 저장 완료: {request.user_number} - {request.session_id}")
        return {"message": "설문 데이터가 Firestore에 저장되었습니다."}

    except Exception as e:
        print(f"🚨 [ERROR] Firestore 저장 중 오류 발생: {e}")
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

# ✅ Firestore에 버튼 클릭 로그 저장하는 엔드포인트
@app.post("/log_event")
async def log_event(event: LogEvent):
    try:
        # ✅ Firestore 경로 설정
        log_ref = db.collection("button_logs").document(event.participantId).collection("events").document()

        # ✅ Firestore에 저장할 데이터 구조
        log_data = {
            "participantId": event.participantId,
            "page": event.page,
            "button": event.button,
            "timestamp": event.timestamp,
        }

        # ✅ Firestore에 데이터 저장
        log_ref.set(log_data)

        print(f"✅ Firestore에 버튼 클릭 로그 저장 완료: {event.participantId} - {event.page} - {event.button}")
        return {"message": "버튼 클릭 로그가 Firestore에 저장되었습니다."}

    except Exception as e:
        print(f"🚨 [ERROR] Firestore 저장 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SurveyLog(BaseModel):
    participantId: str
    page: str
    timestamp: str
    responses: dict

#     return {"message": "설문 응답 저장 완료"}
from fastapi import APIRouter
@app.post("/log_survey")
async def log_survey(survey: SurveyLog):
    """설문 응답 로그를 Firestore에 저장"""

    try:
        # Firestore에 저장할 데이터
        survey_data = {
            "participantId": survey.participantId,
            "page": survey.page,
            "responses": survey.responses,
            "timestamp": survey.timestamp
        }

        # ✅ Firestore의 `survey_logs` 컬렉션에 저장
        db.collection("Eval_logs").document(survey.participantId).collection("PerEval").document(survey.page).set(survey_data)

        print(f"✅ Firestore에 설문 데이터 저장 완료: ")
        return {"message": "설문 응답 저장 완료"}
    
    except Exception as e:
        print(f"🚨 Firestore 저장 중 오류 발생: {e}")
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Multi-Persona Backend is running!"}


@app.get("/")
def root():
    return {"message": "Welcome to Multi-Personas Backend!"}