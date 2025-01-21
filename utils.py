from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
import os
from groq import Groq
from moviepy import VideoFileClip
import PyPDF2
import requests
from bs4 import BeautifulSoup
from docx import Document
from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
OpenAIapiKEY = os.environ["OPENAI_API_KEY"]

# Initialize the Groq client
client = Groq(api_key = GROQ_API_KEY)


def get_youtube_transcript(video_url):
    try:
        # Extract video ID from the YouTube URL
        yt = YouTube(video_url)
        video_id = yt.video_id

        # Retrieve the transcript using the YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript text into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript])

        return transcript_text

    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."

    except VideoUnavailable:
        return "Error: The video is unavailable."

    except Exception as e:
        return f"Error: An error occurred: {e}"
    

def translate_audio_to_text(filename):
    """
    Translates the audio content of the given file into text.

    Parameters:
        filename (str): Path to the audio file to be translated.

    Returns:
        str: The translated text from the audio file.
    """

    try:
        # Open the audio file
        with open(filename, "rb") as file:
            # Create a translation of the audio file
            translation = client.audio.translations.create(
            file=(filename, file.read()), # Required audio file
            model="whisper-large-v3", # Required model to use for translation
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            temperature=0.0  # Optional
            )
            # Return the translation text
            return translation.text
        
    except Exception as e:
        return f"Error: An error occurred: {e}"


def extract_audio_from_video(video_path,output_audio_path = "temp_audio.mp3"):
    """
    Extracts the audio from a video file and saves it as a separate audio file.

    :param video_path: Path to the input video file
    :param output_audio_path: Path to save the extracted audio file
    """
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Extract the audio
        audio = video.audio

        if audio is None:
            print("No audio found in the video file.")
            return
        
        # Write the audio to a file
        audio.write_audiofile(output_audio_path)
        print(f"Audio extracted and saved to {output_audio_path}")
        video.close()
        if 'audio' in locals():
            audio.close()
        return(output_audio_path)
    
    except Exception as e:
        if 'video' in locals():
            video.close()
        if 'audio' in locals():
            audio.close()
        return(f"Error: An error occurred: {e}")
    

def extract_text_from_pdf(pdf_filename):
    """
    Extracts and returns the full text from a PDF file using PyPDF2.

    Args:
        pdf_filename (str): The filename (including path) of the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_filename, 'rb') as pdf_file:
            # Create a PDF reader object
            reader = PyPDF2.PdfReader(pdf_file)

            # Initialize a string to hold the extracted text
            full_text = ""

            # Iterate over all the pages and extract text
            for page in reader.pages:
                full_text += page.extract_text()

            return full_text

    except FileNotFoundError:
        return "Error: File not found. Please check the file path."
    except Exception as e:
        return f"Error: An error occurred: {e}"

def extract_text_from_docx(docx_filename):
    """
    Extracts and returns the full text from a DOCX file.

    Args:
        docx_filename (str): The filename (including path) of the DOCX file.

    Returns:
        str: The extracted text from the DOCX file.
    """
    try:
        # Open the DOCX file
        doc = Document(docx_filename)

        # Initialize a string to hold the extracted text
        full_text = ""

        # Iterate over all paragraphs and extract text
        for paragraph in doc.paragraphs:
            full_text += paragraph.text + "\n"

        return full_text.strip()

    except FileNotFoundError:
        return "Error: File not found. Please check the file path."
    except Exception as e:
        return f"Error: An error occurred: {e}"
    

def extract_text_from_txt(txt_filename):
    """
    Extracts and returns the full text from a TXT file.

    Args:
        txt_filename (str): The filename (including path) of the TXT file.

    Returns:
        str: The extracted text from the TXT file.
    """
    try:
        # Open the TXT file in read mode
        with open(txt_filename, 'r', encoding='utf-8') as txt_file:
            # Read the entire content of the file
            full_text = txt_file.read()

        return full_text

    except FileNotFoundError:
        return "Error: File not found. Please check the file path."
    except Exception as e:
        return f"Error An error occurred: {e}"

def fetch_url_content(url):
    """
    Fetches the textual content from a given URL.

    Parameters:
        url (str): The URL of the webpage to fetch content from.

    Returns:
        str: The textual content of the webpage.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text content from the webpage
        text_content = soup.get_text(separator=' ', strip=True)
        
        return text_content
    except requests.exceptions.RequestException as e:
        return f"Error: An error occurred while fetching the URL: {e}"


def generate_speech(text, output_file="output_speech.mp3", model="tts-1", voice="alloy"):
    """
    Converts text to speech using OpenAI's TTS API and saves it to a file.

    Parameters:
        text (str): The text to be converted to speech.
        output_file (str): Path to save the output audio file.
        model (str): The TTS model to use (default: "tts-1").
        voice (str): The voice to use for speech synthesis (default: "alloy").
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=OpenAIapiKEY)

        # Create speech from text
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
        )

        # Stream the response to the specified output file
        response.stream_to_file(output_file)
        print(f"Speech successfully saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")