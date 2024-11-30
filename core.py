from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()


# docs = PyPDFLoader("constitution_of_india.pdf").load()
llm = ChatOpenAI(model='gpt-4o-mini')

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000, chunk_overlap=200, add_start_index=True
# )

# all_splits = text_splitter.split_documents(docs)

# embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
embeddings = HuggingFaceEmbeddings(  
model_name='sentence-transformers/all-mpnet-base-v2',    
)

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  
)

# print(vector_store,"This is the vector store")
# vector_store.add_documents(documents=all_splits)
retriever = vector_store.as_retriever()

# print(retriever,"THis is the retriever")

system_prompt = (
    '''
You are an assistant specialized in the Indian Constitution.
For queries not related to the Indian constitution:
Respond only with: "I am designed to answer questions about the Indian Constitution. I cannot answer other queries"
For queries about the Indian Constitution:
Use {context} if provided; otherwise, rely on your knowledge base.
Always maintain a professional tone and ensure relevance.
'''
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)                                                                                                       


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# results = rag_chain.invoke({"input": "State  243N Continuance of existing laws and Panchayats"})

# print(results['answer'])

