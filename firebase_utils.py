import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64

# ✅ Firebase 인증 JSON 파일 로드
# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# # ✅ Firestore 인스턴스 생성
# db = firestore.client()

firebase_config_base64 = os.getenv("FIREBASE_CONFIG")

if firebase_config_base64:
    firebase_config_json = json.loads(base64.b64decode(firebase_config_base64).decode("utf-8"))
    cred = credentials.Certificate(firebase_config_json)
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("🚨 [ERROR] 환경 변수 'FIREBASE_CONFIG'가 설정되지 않았습니다.")

db = firestore.client()