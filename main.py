from fastapi import FastAPI, Query
from app.rag.engine import RAGEngine

app=FastAPI()

rag_engine=RAGEngine()

@app.get("/query")
def query(question:str =Query(..., description="User question")):
    """
    Return an LLM generated answer, grounded using the PDF content
    """
    try:
        answer=rag_engine.generate_answer(question)
        return {
            "question":question,
            "answer":answer
        }
    except Exception as e:
        return {
            "question":question,
            "answer":None,
            "error": str(e)
        }