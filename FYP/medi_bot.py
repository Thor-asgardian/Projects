import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import gradio as gr
import tempfile

load_dotenv()

HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
HUGGINGFACE_REPO_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

if not HF_TOKEN:
    raise ValueError("Set HUGGINGFACEHUB_API_TOKEN in .env file")

CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know.

Context: {context}
Question: {question}

Answer:"""

DB_FAISS_PATH = "vectorstore/db_faiss"
DOCUMENT_PATH = "docs/sample.txt"  # Ensure this file exists or update the path

def build_faiss_db_if_not_exists():
    if not os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss")):
        os.makedirs(DB_FAISS_PATH, exist_ok=True)
        loader = TextLoader(DOCUMENT_PATH)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(docs, embedding_model)
        db.save_local(DB_FAISS_PATH)
        print("FAISS vector store created.")

def load_llm(repo_id):
    try:
        return InferenceClient(model=repo_id, token=HF_TOKEN)
    except Exception as e:
        raise Exception(f"LLM load error: {str(e)}")

def load_faiss_db():
    try:
        build_faiss_db_if_not_exists()
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        return FAISS.load_local(
            folder_path=DB_FAISS_PATH,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True
        )
    except ImportError:
        raise ImportError("FAISS module not installed. Install it with `pip install faiss-cpu` or `faiss-gpu`")
    except Exception as e:
        raise Exception(f"FAISS DB load error: {str(e)}")

def process_query_with_client(client, db, question):
    try:
        docs = db.similarity_search(question, k=3)
        context = " ".join([doc.page_content for doc in docs])
        prompt = CUSTOM_PROMPT_TEMPLATE.format(context=context, question=question)
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.5
        )
        return {"result": response.choices[0].message.content.strip(), "source_documents": docs}
    except Exception as e:
        if "402" in str(e):
            return {"result": "", "source_documents": []}
        raise Exception(f"Inference error: {str(e)}")

def get_voice_input(audio_path, language_code):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language=language_code), None
    except sr.UnknownValueError:
        return None, "Could not understand the audio."
    except sr.RequestError as e:
        return None, f"Speech recognition error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected audio error: {str(e)}"

def translate_to_english(text, src_lang):
    if src_lang == "en":
        return text, None
    try:
        translated = GoogleTranslator(source=src_lang, target="en").translate(text)
        return translated, None
    except Exception as e:
        return None, f"Translation error: {str(e)}"

def translate_to_kannada(text):
    try:
        translated = GoogleTranslator(source="en", target="kn").translate(text)
        return translated, None
    except Exception as e:
        return None, f"Kannada translation error: {str(e)}"

def generate_audio(text, lang):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name, None
    except Exception as e:
        return None, f"Text-to-speech error: {str(e)}"

def process_query(audio, language, text_input=None):
    lang_code = "en-US" if language == "English" else "kn-IN"
    lang_short = "en" if language == "English" else "kn"

    if text_input:
        text = text_input
        voice_error = None
    elif audio:
        text, voice_error = get_voice_input(audio, lang_code)
        if voice_error:
            return f"Error: {voice_error}", text, None, None, None, None, None
    else:
        return "Error: Provide either audio or text input.", None, None, None, None, None, None

    query_in_english, trans_error = translate_to_english(text, lang_short)
    if trans_error:
        return f"Error: {trans_error}", text, None, None, None, None, None

    try:
        db = load_faiss_db()
        client = load_llm(HUGGINGFACE_REPO_ID)
        response = process_query_with_client(client, db, query_in_english)
        english_answer = response["result"]
        sources = response["source_documents"]

        if not english_answer:
            return "Error: No response from model (maybe credit limit).", text, query_in_english, None, None, None, None

        if language == "Kannada":
            kannada_answer, kan_err = translate_to_kannada(english_answer)
            if kan_err:
                return f"Error: {kan_err}", text, query_in_english, english_answer, None, None, None
            answer_to_display = kannada_answer
            answer_to_speak = kannada_answer
        else:
            answer_to_display = english_answer
            kannada_answer = None
            answer_to_speak = english_answer

        audio_file, audio_err = generate_audio(answer_to_speak, lang_short)
        if audio_err:
            return f"Error: {audio_err}", text, query_in_english, answer_to_display, kannada_answer, None, None

        sources_text = "\n".join([f"{i+1}. {doc.page_content[:200]}..." for i, doc in enumerate(sources)])

        return None, text, query_in_english if language == "Kannada" else None, answer_to_display, kannada_answer, audio_file, sources_text
    except Exception as e:
        return f"Error: {str(e)}", text, query_in_english, None, None, None, None

with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("## 🩺 Bilingual Medical QA Chatbot")

        with gr.Row():
            language = gr.Dropdown(["English", "Kannada"], label="Language", value="English")
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙 Speak Your Query")

        text_input = gr.Textbox(label="📝 Or Type Your Query", placeholder="Type your medical question here...")

        submit_button = gr.Button("Submit Query")

        error_output = gr.Textbox(label="Error", visible=False)
        original_query = gr.Textbox(label="Recognized Query")
        english_query = gr.Textbox(label="Translated (English)", visible=False)
        answer = gr.Textbox(label="Answer")
        kannada_answer = gr.Textbox(label="Answer (Kannada)", visible=False)
        sources_output = gr.Textbox(label="Source Documents")
        audio_output = gr.Audio(label="🔊 Audio Response")

        submit_button.click(
            fn=process_query,
            inputs=[audio_input, language, text_input],
            outputs=[error_output, original_query, english_query, answer, kannada_answer, audio_output, sources_output]
        )

demo.launch()