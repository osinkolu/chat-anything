# Retrieval Augmented Generation (RAG) with Snowflake, Mistral LLM, and Streamlit

## Project Overview

This project leverages the power of **Cortex Search** for efficient document retrieval, **Mistral LLM** (mistral-large2) for natural language generation, and **Streamlit** for a user-friendly frontend interface. It allows users to upload various types of media (PDFs, DOCX files, YouTube videos, audio, etc.) and interact with documents in a conversational manner. The system retrieves relevant document chunks based on the user's input and generates detailed responses using Mistral LLM. Additionally, a Text-to-Speech (TTS) feature is integrated for audio-based responses.

This project is built for the **RAG ‘n’ ROLL** hackathon, which aims to showcase the potential of **Retrieval Augmented Generation (RAG)** to enhance the way we interact with information using cutting-edge AI technologies.

---

## Key Features

- **Media Upload**: Supports various media types including PDF, DOCX, TXT, YouTube videos, Web URLs, Audio, and Video.
- **Document Retrieval**: Uses Snowflake's Cortex Search to fetch relevant document chunks.
- **Natural Language Generation**: Generates AI-driven responses based on document context using the **Mistral LLM** (mistral-large2) model.
- **Text-to-Speech (TTS)**: A toggle to listen to AI-generated responses instead of reading them.
- **Clear Chat**: A button to clear the conversation history and start a new session.
- **Multiple Document Deletion**: Users can select and delete multiple documents from the database at once.

---

## Project Setup

### Prerequisites

Before you start, ensure that you have the following:

- **Snowflake Account**: Set up a Snowflake account and configure the necessary Snowflake services.
- **Streamlit Account**: Make sure you have a Streamlit account to host the app on Streamlit Community Cloud.
- **Python Libraries**: Install the required Python libraries.

```bash
pip install snowflake-snowpark-python streamlit langchain pytube youtube-transcript-api moviepy PyPDF2 requests beautifulsoup4 docx groq
```

### Environment Setup

1. **Snowflake Configuration**:
   - Ensure your Snowflake environment is set up with the required databases, schemas, and the `Cortex Search` service.
   - Add your Snowflake credentials to the project as environment variables or within a configuration file.

2. **Mistral LLM Integration**:
   - Configure the Mistral LLM model (mistral-large2) for text generation via Snowflake Cortex.

3. **Streamlit Deployment**:
   - Deploy the application to **Streamlit Community Cloud** for public access.
   - Ensure that the app is accessible by providing the URL once it's live.

### Usage

1. **Upload Documents**:
   - Choose a document type (PDF, DOCX, TXT, YouTube, Web URL, Audio, Video) and upload it to the app.
   - The app will automatically process the file and extract relevant content.

2. **Chat with Documents**:
   - Enter a question or statement related to the uploaded documents.
   - The app will retrieve relevant document chunks and generate an AI-based response.
   - You can choose to enable or disable the Text-to-Speech (TTS) feature to hear the response instead of reading it.

3. **Manage Documents**:
   - Use the “Manage Documents” page to delete documents from the database. You can select multiple documents to delete at once.

---

## Project Demonstration

A video demonstration showcasing the functionality of the project is available. The demo includes:

- Uploading and processing various media files.
- Asking questions and receiving AI-generated answers.
- Using the TTS feature to listen to responses.
- Managing and deleting documents.


---

## Contributions

This project is part of the **RAG ‘n’ ROLL** Hackathon organized by **Snowflake & Mistral**. It leverages the following technologies:

- **Cortex Search**: For efficient document retrieval.
- **Mistral LLM**: For natural language generation.
- **Streamlit**: For the user interface.
- **PyPDF2, docx, pytube, moviepy, and other libraries**: For extracting and processing content from different media types.

---

## License

This project is open-source and available under the MIT License.
