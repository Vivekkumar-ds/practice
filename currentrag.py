from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import HuggingFaceHub
import os
from langchain_huggingface import HuggingFaceEmbeddings


os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_VlezWuKnzoXhKpthefjbBBpmXvolpJZFjdzxcvbnm"


app = FastAPI()


DOCUMENT_PATH = r"D:\apiapp\current.txt"


if not os.path.exists(DOCUMENT_PATH):
    raise FileNotFoundError(f"{DOCUMENT_PATH} not found.")


loader = TextLoader(DOCUMENT_PATH, encoding='utf-8')
documents = loader.load()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


vectorstore = FAISS.from_documents(chunks, embeddings)


llm = HuggingFaceHub(repo_id="tiiuae/falcon-7b-instruct", model_kwargs={"temperature": 0.3, "max_new_tokens": 150})


qa_chain = load_qa_chain(llm)


class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(query: QueryRequest):
    
    try:
        
        docs = vectorstore.similarity_search(query.question, k=5)  
        
        print("Retrieved Chunks: ", docs)
        
        answer = qa_chain.run(input_documents=docs, question=query.question)
        
        return QueryResponse(question=query.question, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
