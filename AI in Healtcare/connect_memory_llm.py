# connect memory
import os
import speech_recognition as sr 
from deep_translator import GoogleTranslator 
from gtts import gTTS 
import pygame
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import sys
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Step 1: Setup LLM (Mistral with HuggingFace)
HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
HUGGINGFACE_REPO_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

if not HF_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN environment variable not set.")

def load_llm(huggingface_repo_id: str):
    try:
        llm = HuggingFaceEndpoint(
            repo_id=huggingface_repo_id,
            huggingfacehub_api_token=HF_TOKEN,
            task="text-generation",   # specify task explicitly
            model_kwargs={"temperature": 0.5, "max_new_tokens": 512}
        ) # type: ignore
        return llm
    except Exception as e:
        raise Exception(f"Failed to load LLM: {str(e)}")


# Step 2: Define custom prompt
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
Don't provide anything outside of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

def set_custom_prompt(custom_prompt_template): # type: ignore
    return PromptTemplate(
        template=custom_prompt_template, # type: ignore
        input_variables=["context", "question"]
    )

# Step 3: Load FAISS database
DB_FAISS_PATH = "vectorstore/db_faiss"
try:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    db = FAISS.load_local(
        folder_path=DB_FAISS_PATH,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )
except Exception as e:
    raise Exception(f"Failed to load FAISS database: {str(e)}")

# Step 4: Create QA chain
try:
    qa_chain = RetrievalQA.from_chain_type(
        llm=load_llm(huggingface_repo_id=HUGGINGFACE_REPO_ID),
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
    )
except Exception as e:
    raise Exception(f"Failed to create QA chain: {str(e)}")

# Step 5: Voice input and output functions
def select_language():
    while True:
        print("Select language: 1) English 2) Kannada")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "en", "en-US"
        elif choice == "2":
            return "kn", "kn-IN"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_voice_input(language_code):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Please speak your query in {'English' if language_code == 'en-US' else 'Kannada'}...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language=language_code)
            print(f"Recognized text: {text}")
            return text
        except sr.WaitTimeoutError:
            print("Error: No speech detected within 7 seconds.")
            return None
        except sr.UnknownValueError:
            print("Error: Could not understand the audio. Please speak clearly.")
            return None
        except sr.RequestError as e:
            print(f"Error: Speech recognition failed; {str(e)}")
            return None

def translate_to_english(text, src_lang):
    if src_lang == "en":
        return text
    try:
        translator = GoogleTranslator(source="kn", target="en")
        translated = translator.translate(text)
        print(f"Translated to English: {translated}")
        return translated
    except Exception as e:
        print(f"Translation error: {str(e)}")
        retry = input("Translation failed. Type the query in Kannada or 'skip' to continue: ").strip()
        if retry.lower() == "skip":
            return None
        try:
            translated = translator.translate(retry)
            print(f"Translated manual input to English: {translated}")
            return translated
        except Exception as e:
            print(f"Manual translation error: {str(e)}")
            return None

def translate_to_kannada(text):
    try:
        translator = GoogleTranslator(source="en", target="kn")
        translated = translator.translate(text)
        print(f"Translated to Kannada: {translated}")
        return translated
    except Exception as e:
        print(f"Kannada translation error: {str(e)}")
        return text  # Fallback to English if translation fails

def text_to_speech(text, lang):
    try:
        print(f"Generating speech in {'English' if lang == 'en' else 'Kannada'}...")
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_file = "response.mp3"
        tts.save(audio_file)
        print(f"Saved audio file: {audio_file}")
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove(audio_file)
        print("Audio played and file removed.")
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")

# Step 6: Query loop with voice input and output
def run_query_loop():
    print("Welcome to the Bilingual Medical QA System.")
    lang, lang_code = select_language()
    print(f"Selected language: {'English' if lang == 'en' else 'Kannada'}")
    print("Speak your query or type 'exit'/'quit' to stop.")

    while True:
        try:
            exit_check = input("Press Enter to speak, or type 'exit'/'quit' to stop: ").strip().lower()
            if exit_check in ['exit', 'quit']:
                print("Exiting query loop. Goodbye!")
                break

            user_query = get_voice_input(lang_code)
            if not user_query:
                print("Please try speaking again or type 'exit' to stop.")
                continue

            query_in_english = translate_to_english(user_query, lang)
            if not query_in_english:
                print("Unable to process query due to translation failure. Try again.")
                continue

            response = qa_chain.invoke({"query": query_in_english})
            answer = response["result"]
            print("\nRESULT (English):", answer)
            print("\nSOURCE DOCUMENTS:", response["source_documents"])
            print("\n" + "="*50 + "\n")

            # Translate answer to Kannada if language is Kannada
            answer_to_speak = translate_to_kannada(answer) if lang == "kn" else answer
            text_to_speech(answer_to_speak, lang)

        except Exception as e:
            print(f"Error processing query: {str(e)}")
            print("Please try again or type 'exit' to stop.\n")

# Run the query loop
if __name__ == "__main__":
    try:
        run_query_loop()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)