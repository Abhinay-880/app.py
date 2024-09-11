import os
import streamlit as st
import pickle
import time
from langchain import OpenAI # type: ignore
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()  # take environment variables from .env (especially openai api key)

st.title("News Research Tool 📈")
st.sidebar.title("News Article URLs")

# Create a list to store URLs entered by the user
urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

# Button to initiate processing of entered URLs
process_url_clicked = st.sidebar.button("Process URLs")
# File path for storing serialized FAISS index 
file_path = "faiss_store_openai.pkl"

# Placeholder for main content area
main_placeholder = st.empty()

# Initialize OpenAI language model 
llm = OpenAI(temperature=0.9, max_tokens=500)

if process_url_clicked: 
    # Load data from the URLs
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading...Started...✅✅✅")
    data = loader.load()

    # Split data into smaller documents
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000
    )
    main_placeholder.text("Text Splitter...Started...✅✅✅")
    docs = text_splitter.split_documents(data)

    # Create embeddings from documents and build FAISS index
    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    pkl = vectorstore_openai.serialize_to_bytes()
    main_placeholder.text("Embedding Vector Started Building...✅✅✅")
    time.sleep(2)  # Simulate processing time

    # Save the FAISS index to a pickle file
    with open(file_path, "wb") as f:
        pickle.dump(pkl, f)

# Input field for user query
query = main_placeholder.text_input("Question: ")

if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            pkl = pickle.load(f)
            # Deserialize the FAISS index and create a retrieval question-answering chain
            vectorstore = FAISS.deserialize_from_bytes(
                embeddings=OpenAIEmbeddings(), 
                serialized=pkl, 
                allow_dangerous_deserialization=True
            )
            chain = RetrievalQAWithSourcesChain.from_llm(
                llm=llm, 
                retriever=vectorstore.as_retriever()
            )
            result = chain({"question": query}, return_only_outputs=True)

            # Display the answer
            st.header("Answer")
            st.write(result["answer"])

            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")
                for source in sources_list:
                    st.write(source)