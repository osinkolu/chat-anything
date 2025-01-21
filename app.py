import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from snowflake.snowpark import Session
from snowflake.core import Root
import os
from utils import (get_youtube_transcript, extract_text_from_pdf, 
                   extract_text_from_docx, extract_text_from_txt, 
                   fetch_url_content, extract_audio_from_video, 
                   translate_audio_to_text, generate_speech)
from streamlit_option_menu import option_menu
import os, json
import dotenv

dotenv.load_dotenv()

# Snowflake Connection Configuration

SNOWFLAKE_CONFIG = json.loads(os.environ['SNOWFLAKE_CONFIG'])

# Constants
NUM_CHUNKS = 3
CHUNK_SIZE = 1512
CHUNK_OVERLAP = 256

# Initialize Snowflake Session
if "snowflake_session" not in st.session_state:
    st.session_state.snowflake_session = Session.builder.configs(SNOWFLAKE_CONFIG).create()

session = st.session_state.snowflake_session

root = Root(session)
svc = root.databases[SNOWFLAKE_CONFIG["database"]].schemas[SNOWFLAKE_CONFIG["schema"]].cortex_search_services[SNOWFLAKE_CONFIG["search_service"]]

# Streamlit App
st.title("Chat Anything 🗨️")

# Sidebar Navigation
st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["Upload Files", "Chat with Documents", "Manage Documents"])
with st.sidebar:
        page = option_menu(
            menu_title=None,
            options = ["Chat", "Upload Files", "Manage Documents", "About"],
            icons=["snow", "cloud-upload", "file-earmark-diff", "plus"],
        )

if page == "Upload Files":
    st.header("Upload and Process Media")
    media_type = st.selectbox("Select Media Type", ["PDF", "DOCX", "TXT", "YouTube", "Web URL", "Audio", "Video"])

    def process_and_store(text, filename, category):
        """Chunks and stores the text in Snowflake."""
        if text.startswith("Error:"):
            st.error(text)
        else:
            chunks = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            ).split_text(text)
            for chunk in chunks:
                session.sql(
                    "INSERT INTO DOCS_CHUNKS_TABLE (CHUNK, RELATIVE_PATH, CATEGORY) VALUES (?, ?, ?)",
                    params=[chunk, filename, category]
                ).collect()
            st.success(f"Your {category} has been processed successfully You can now go to the chat section to converse.")

    if media_type == "PDF":
        uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            text = extract_text_from_pdf(uploaded_file.name)
            process_and_store(text, uploaded_file.name, "PDF")

    elif media_type == "DOCX":
        uploaded_file = st.file_uploader("Upload DOCX file", type=["docx"])
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            text = extract_text_from_docx(uploaded_file.name)
            process_and_store(text, uploaded_file.name, "DOCX")

    elif media_type == "TXT":
        uploaded_file = st.file_uploader("Upload TXT file", type=["txt"])
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            text = extract_text_from_txt(uploaded_file.name)
            process_and_store(text, uploaded_file.name, "TXT")

    elif media_type == "YouTube":
        youtube_url = st.text_input("Enter YouTube Video URL")
        if youtube_url:
            text = get_youtube_transcript(youtube_url)
            process_and_store(text, youtube_url, "YouTube")

    elif media_type == "Web URL":
        web_url = st.text_input("Enter Web URL")
        if web_url:
            text = fetch_url_content(web_url)
            process_and_store(text, web_url, "Web URL")

    elif media_type == "Audio":
        uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            text = translate_audio_to_text(uploaded_file.name)
            process_and_store(text, uploaded_file.name, "Audio")

    elif media_type == "Video":
        uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mkv", "mov"])
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            audio_path = extract_audio_from_video(uploaded_file.name)
            if audio_path and not audio_path.startswith("Error:"):
                text = translate_audio_to_text(audio_path)
                process_and_store(text, uploaded_file.name, "Video")
            elif audio_path.startswith("Error:"):
                st.error(audio_path)


elif page == "Chat":
    st.header("Chat with any Media (Files, Videos and More!)")

    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Clear Chat Button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

    # Toggle for Text-to-Speech
    tts_enabled = st.checkbox("Enable Text-to-Speech for Responses")

    category = st.selectbox("Select Category", ["All"] + [row["CATEGORY"] for row in session.sql(
        "SELECT DISTINCT CATEGORY FROM DOCS_CHUNKS_TABLE"
    ).collect()])

    # Chat interface using chat_message
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])
            # if tts_enabled and "audio_file" in message:
                #st.audio(message["audio_file"], format="audio/mp3", start_time=0, autoplay = True)
                # play_audio(message["audio_file"])

    # User input
    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        if prompt.lower() in ["hi", "hello", "hey", "thanks", "thank you"]:
            # Simple conversational response
            response = "Hello! How can I assist you?" if "hi" in prompt.lower() else "You're welcome!"
            audio_file = None
            if tts_enabled:
                audio_file = f"{prompt[:10]}_response.mp3"  # Generate unique filename
                generate_speech(text=response, output_file=audio_file)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "audio_file": audio_file if tts_enabled else None
            })
            st.chat_message("assistant").markdown(response)
            if tts_enabled:
                st.audio(audio_file, format="audio/mp3", start_time=0, autoplay = True)
                # play_audio(audio_file)
        else:
            st.write("Searching for relevant chunks...")

            # Build Filter Object
            filter_obj = {"@eq": {"category": category}} if category != "All" else None

            # Query Cortex Search Service
            try:
                response = svc.search(
                    query=prompt,
                    columns=["chunk", "relative_path", "category"],
                    filter=filter_obj,
                    limit=NUM_CHUNKS
                )
                results = response.results

                if results:
                    # Extract relevant chunks and paths
                    chunks = [result["chunk"] for result in results]
                    relative_paths = set(result["relative_path"] for result in results)

                    # Generate Prompt for Mixtral-200
                    context = "\n".join(chunks)
                    query_prompt = f"""
                    You are an AI assistant. Use the CONTEXT below to answer the QUESTION.

                    CONTEXT:
                    {context}

                    QUESTION:
                    {prompt}

                    ANSWER:
                    """

                    st.write("Generating response...")
                    result = session.sql(
                        "SELECT snowflake.cortex.complete(?, ?) AS response",
                        params=["mistral-large2", query_prompt]
                    ).collect()

                    answer = result[0]["RESPONSE"]
                    audio_file = None
                    if tts_enabled:
                        audio_file = f"{prompt[:10]}_response.mp3"  # Generate unique filename
                        generate_speech(text=answer, output_file=audio_file)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "audio_file": audio_file if tts_enabled else None
                    })
                    st.chat_message("assistant").markdown(answer)
                    if tts_enabled:
                        st.audio(audio_file, format="audio/mp3", start_time=0, autoplay = True)
                        # play_audio(audio_file)

                    # Display Related Documents
                    if relative_paths:
                        st.markdown("### Related Documents")
                        for path in relative_paths:
                            doc_url = session.sql(
                                f"SELECT GET_PRESIGNED_URL(@docs, '{path}', 360) AS URL_LINK FROM DIRECTORY(@docs)"
                            ).collect()[0]["URL_LINK"]
                            st.markdown(f"- [{path}]({doc_url})")
                else:
                    no_answer = "No relevant chunks found."
                    st.session_state.chat_history.append({"role": "assistant", "content": no_answer})
                    st.chat_message("assistant").markdown(no_answer)
            except Exception as e:
                error_message = f"Error querying Cortex Search Service: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
                st.chat_message("assistant").markdown(error_message)


elif page == "Manage Documents":
    st.header("Manage Your Documents")

    # Retrieve all documents
    documents = session.sql("SELECT DISTINCT RELATIVE_PATH FROM DOCS_CHUNKS_TABLE").collect()
    document_list = [doc["RELATIVE_PATH"] for doc in documents]

    if document_list:
        selected_documents = st.multiselect("Select documents to delete", document_list)

        if st.button("Delete Selected Documents"):
            try:
                for document in selected_documents:
                    session.sql(
                        "DELETE FROM DOCS_CHUNKS_TABLE WHERE RELATIVE_PATH = ?",
                        params=[document]
                    ).collect()
                st.success(f"Selected documents have been deleted successfully.")
            except Exception as e:
                st.error(f"Error deleting selected documents: {e}")
    else:
        st.info("No documents available to manage.")

elif page == "About":
    # Open and read the README.md file
    with open("README.md", "r", encoding="utf-8") as readme_file:
        readme_content = readme_file.read()
    
    # Render the markdown content in Streamlit
    st.markdown(readme_content, unsafe_allow_html=True)
