import firebase_admin
from firebase_admin import credentials, firestore
import os


# 환경 변수에서 JSON 파일 경로 가져오기
config_path = os.getenv("FIREBASE_CONFIG")

if config_path and os.path.exists(config_path):
    if not firebase_admin._apps:  # Firebase가 초기화되지 않은 경우에만 실행
        cred = credentials.Certificate(config_path)  
        firebase_admin.initialize_app(cred)
        print("🔥 Firebase 연결 성공!")
    else:
        print("⚠️ Firebase는 이미 초기화되었습니다.")
else:
    print("❌ FIREBASE_CONFIG 환경 변수가 설정되지 않았거나, JSON 파일이 존재하지 않습니다.")

db = firestore.client()
