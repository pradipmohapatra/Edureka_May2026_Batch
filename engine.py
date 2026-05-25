from app.core.config import PDF_PATH, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME, TOP_K
from app.rag.loader import PDFLoader
from app.rag.chunker import LangchainTextChunker
from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore

from langchain.agents import create_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

class RAGEngine:
    """
    Singleton-style RAG Engine.
    Initialized once and serves all queries
    """

    def __init__(self):
        self.vector_store=None
        self._initialize()

    def _initialize(self):
        load_dotenv()

        text=PDFLoader(PDF_PATH).load()

        chunks=LangchainTextChunker(CHUNK_SIZE, CHUNK_OVERLAP).chunk(text)

        embeddings=EmbeddingModel(EMBEDDING_MODEL_NAME)

        self.vector_store=VectorStore(embeddings)
        self.vector_store.build(chunks)

        self.llm=ChatGroq(model_name="llama-3.3-70b-versatile")

    def generate_answer(self, question:str):
        """
        Geneate an answer using the vectore store with a grounded prompt.
        Retrieve top -k chunls and pass them to llm with a strict prompt
        """
        contexts=self.vector_store.search(query=question, k=TOP_K)
        combined_text="\n\n".join(contexts)

        prompt_template=f"""
        You are a helpfile assistant. Use only the information provided in the context below to answer the question.
        If the answer is not present in the context, respond with "I don't know"

        Context: {combined_text}

        question: {question}

        answer:
        """

        agent=create_agent(
            model=self.llm,
            system_prompt="You are a helpful assistant"
        )

        result=agent.invoke({
            "messages":[
                {"role":"user", "content":prompt_template}
            ]
        }) 

        return result['messages'][-1].content