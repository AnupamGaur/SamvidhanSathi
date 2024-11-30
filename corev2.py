import json
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

# embeddings = HuggingFaceEmbeddings(  
# model_name='sentence-transformers/all-mpnet-base-v2',    
# )

embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  
)

# file_path='./constitution_of_india_edited.json'
# data = json.loads(Path(file_path).read_text(encoding='utf-8'))

# all_splits = [Document(page_content=obj['description'],
#     metadata={'title': obj['title'], 'article': obj['article']}) for obj in data]

retriever = vector_store.as_retriever(search_kwargs={'k': 3})

# print(retriever,"THis is the retriever")

# vector_store.add_documents(documents=all_splits)

system_prompt = (
    '''
Always provide concise answers(within 40-50 words) and ensure relevance.
Use {context}
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

# results = rag_chain.invoke({"input": "How do Articles 14, 19, and 21 interact with each other to protect fundamental rights?"})

# print(results['answer'])