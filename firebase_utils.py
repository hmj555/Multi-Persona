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

# # ✅ Firebase 인증 JSON 파일 로드
# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# # ✅ Firestore 인스턴스 생성
# db = firestore.client()

# firebase_config_base64 = os.getenv("FIREBASE_CONFIG")
# os.getenv("SUPABASE_KEY")

# if not firebase_config_base64:
#     raise ValueError("🚨 [ERROR] 환경 변수 'FIREBASE_CONFIG'가 설정되지 않았습니다.")

# # ✅ Base64 디코딩하여 JSON 객체로 변환
# firebase_config_base64 = os.getenv("FIREBASE_CONFIG")

# if not firebase_config_base64:
#     raise ValueError("🚨 [ERROR] 환경 변수 'FIREBASE_CONFIG'가 설정되지 않았습니다.")

# # ✅ Base64 디코딩하여 JSON 객체로 변환
# firebase_config_json = json.loads(base64.b64decode(firebase_config_base64).decode("utf-8"))

# # ✅ JSON 객체를 credentials.Certificate()에 직접 전달
# cred = credentials.Certificate(firebase_config_json)
# firebase_admin.initialize_app(cred)

# # ✅ Firestore 클라이언트 생성
# db = firestore.client()

# print("🔥 Firebase 연결 성공!")