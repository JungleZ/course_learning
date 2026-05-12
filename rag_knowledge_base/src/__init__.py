# src package - RAG Knowledge Base
# 纯 Python 实现，不依赖 langchain
from data_processing import process_documents, load_database
from retriever import create_retriever, get_relevant_documents, is_off_topic, get_top_k_texts, Document
from generator import create_generator, RAGGenerator, MockGenerator