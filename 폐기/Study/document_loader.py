### RAG 1단계
from dotenv import load_dotenv
load_dotenv()

### Document: data
FILE_PATH = "./data/SPRI_AI_Brief_2023년12월호_F.pdf"
def show_metadata(docs):
    if docs:
        print("[metadata]")
        print(list(docs[0].metadata.keys()))
        print("\n[examples]")
        max_key_length = max(len(k) for k in docs[0].metadata.keys())
        for k, v in docs[0].metadata.items():
            print(f"{k:<{max_key_length}} : {v}")
            
### PyPDF (PDF를 문서 배열로 로드 -> 페이지 번호+페이지 콘텐츠)
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(FILE_PATH) # 파일 경로 설정
docs = loader.load() # PDF 페이지 로드
print(docs[10].page_content[:300])
show_metadata(docs)

# PyPDF(OCR): 문서나 그림 내 텍스트 이미지 포함된 경우
loader = PyPDFLoader("https://arxiv.org/pdf/2103.15348.pdf", extract_images=True) # 이미지 추출 옵션 활성화
docs = loader.load() # PDF 페이지 로드
print(docs[4].page_content[:300])