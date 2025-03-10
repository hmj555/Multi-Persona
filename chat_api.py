from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from ChatAgent_Tag import chat, save_chat_log

app = FastAPI()

# 요청 데이터 형식 정의
class ChatRequest(BaseModel):
    user_number: str
    session_id: str
    persona_type: str
    input_text: str

@app.post("/chat")
def chat_with_persona(request: ChatRequest):
    try:
        response = chat(
            input_text=request.input_text,
            session_id=request.session_id,
            persona_type=request.persona_type
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save_chat_log")
def save_log(user_number: str, persona_type: str):
    try:
        save_chat_log(user_number=user_number, persona_type=persona_type)
        return {"message": "Chat log saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)