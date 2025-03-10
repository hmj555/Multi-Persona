### Create_DB.py: RAG에서 검색 대상이 될 문서 DB 생성

from dotenv import load_dotenv ; import os
load_dotenv()
from langchain_teddynote import logging
logging.langsmith("Persona")
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))

############ (1) DB 구축 ############
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 모든 PDF 파일 로드
pdf_folder = "data" 
pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

# 모든 PDF 문서 로드
all_documents = []
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()
    all_documents.extend(documents) 

# Text Chunking
text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
docs = text_splitter.split_documents(all_documents)

# OpenAI 임베딩
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# FAISS 벡터 DB 저장
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index")  # 저장 완료

print(f"총 {len(docs)}개의 청크가 FAISS 벡터 DB에 저장되었습니다.")