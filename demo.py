import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import streamlit as st
from PIL import Image
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import pygame
import pyttsx3
import json
import base64
from io import BytesIO
import time

# Set your Gemini API keys
genai.configure(api_key="AIzaSyCbZD_n69EjLEKqTQ1_nNZta4iwnPCyHq0")
model = genai.GenerativeModel("gemini-2.0-flash")
model_flash = genai.GenerativeModel("gemini-1.5-flash")

# Initialize session state
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'welcome'
if 'show_animation' not in st.session_state:
    st.session_state.show_animation = False
if 'selected_app' not in st.session_state:
    st.session_state.selected_app = None
if 'flashcard_progress' not in st.session_state:
    st.session_state.flashcard_progress = {"correct": 0, "incorrect": 0}
if 'current_card' not in st.session_state:
    st.session_state.current_card = 0

# Sample flashcards data (you can expand this)
FLASHCARDS = [
    {"word": "Cat", "image": "🐱", "description": "A small domesticated carnivorous mammal"},
    {"word": "Dog", "image": "🐶", "description": "A domesticated carnivorous mammal that typically has a long snout"},
    {"word": "Apple", "image": "🍎", "description": "A round fruit of a tree of the rose family"},
    {"word": "Car", "image": "🚗", "description": "A road vehicle, typically with four wheels"},
    {"word": "House", "image": "🏠", "description": "A building for human habitation"},
    {"word": "Tree", "image": "🌳", "description": "A woody perennial plant with a trunk"},
    {"word": "Book", "image": "📚", "description": "A written or printed work consisting of pages"},
    {"word": "Sun", "image": "☀️", "description": "The star around which the earth orbits"}
]

def show_welcome_screen():
    """Display the welcome screen"""
    st.set_page_config(layout="wide", page_title="🚀 AI Teaching Assistant Suite")
    
    # Custom CSS for welcome screen with animations
    st.markdown("""
    <style>
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 70vh;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA07A);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease-in-out infinite;
        margin-bottom: 2rem;
    }
    
    .welcome-subtitle {
        font-size: 1.5rem;
        color: #666;
        margin-bottom: 3rem;
        animation: fadeInUp 2s ease-out;
    }
    
    .press-enter {
        font-size: 2rem;
        color: #333;
        animation: pulse 2s infinite;
        border: 3px solid #4ECDC4;
        padding: 20px 40px;
        border-radius: 15px;
        background: rgba(78, 205, 196, 0.1);
        cursor: pointer;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">🎓 AI Teaching & Learning Assistant</div>
        <div class="welcome-subtitle">Complete learning solution with AI-powered tools</div>
        <div class="press-enter">Press Enter to Continue ⏎</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle Enter key press (using button as fallback)
    if st.button("Continue", key="continue_btn", use_container_width=True):
        st.session_state.app_state = 'selection'
        st.session_state.show_animation = True
        st.rerun()

def show_app_selection():
    """Display animated app selection screen"""
    st.set_page_config(layout="wide", page_title="🎯 Select Learning Tool")
    
    # Custom CSS for app selection with advanced animations
    st.markdown("""
    <style>
    .selection-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: slideInDown 1s ease-out;
    }
    
    .app-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        text-align: center;
        cursor: pointer;
        transform: translateY(20px);
        opacity: 0;
        animation: slideInCard 0.8s ease-out forwards;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    
    .app-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    .app-card-1 {
        animation-delay: 0.2s;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    }
    
    .app-card-2 {
        animation-delay: 0.4s;
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
    }
    
    .app-card-3 {
        animation-delay: 0.6s;
        background: linear-gradient(135deg, #A8E6CF 0%, #88D8A3 100%);
    }
    
    .app-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
        animation: bounce 2s infinite;
    }
    
    .app-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .app-description {
        font-size: 1rem;
        line-height: 1.5;
        opacity: 0.9;
    }
    
    @keyframes slideInDown {
        0% { opacity: 0; transform: translateY(-50px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInCard {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="selection-title">🎯 Choose Your Learning Tool</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="app-card app-card-1">
            <span class="app-icon">✋🧠</span>
            <div class="app-title">Handwriting Solver</div>
            <div class="app-description">
                Draw mathematical equations with your hand gestures and get instant AI-powered solutions
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Handwriting Solver", key="app1", use_container_width=True):
            st.session_state.selected_app = 'handwriting_solver'
            st.session_state.app_state = 'running'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-card app-card-2">
            <span class="app-icon">🎤</span>
            <div class="app-title">Voice Learning Assistant</div>
            <div class="app-description">
                Boliye aur Seekhiye – Your AI vernacular learning buddy with voice interaction
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Voice Assistant", key="app2", use_container_width=True):
            st.session_state.selected_app = 'voice_assistant'
            st.session_state.app_state = 'running'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="app-card app-card-3">
            <span class="app-icon">🃏</span>
            <div class="app-title">FlashLearn Cards</div>
            <div class="app-description">
                Interactive flashcards with voice recognition and AI feedback for vocabulary learning
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch FlashCards", key="app3", use_container_width=True):
            st.session_state.selected_app = 'flashcards'
            st.session_state.app_state = 'running'
            st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Welcome", use_container_width=True):
        st.session_state.app_state = 'welcome'
        st.rerun()

def run_handwriting_solver():
    """Original Handwriting Solver Code"""
    st.set_page_config(layout="wide", page_title="✋🧠 Handwriting Solver")
    st.title("✋🧠 Question Solver with Whiteboard")
    
    # Back button
    if st.button("← Back to Menu"):
        st.session_state.app_state = 'selection'
        st.rerun()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        run = st.checkbox('Run Webcam', value=False)
        FRAME_WINDOW = st.image([])

    with col2:
        st.subheader("✍️ Index finger to draw")
        st.subheader("✊ Fist to clear")
        st.subheader("🖖 4 fingers to send")
        st.subheader("🧼 Toggle whiteboard background")
        whiteboard_mode = st.checkbox("White Background", value=True)
        output_box = st.empty()

    # Hand detector and camera
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1)

    prev_pos = None
    canvas = None
    output_text = ""

    if run:
        while True:
            success, img = cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)
            h, w, _ = img.shape

            if canvas is None:
                canvas = np.ones_like(img, np.uint8) * 255 if whiteboard_mode else np.zeros_like(img)

            hands, img = detector.findHands(img, draw=True, flipType=True)

            if hands:
                hand = hands[0]
                lmList = hand["lmList"]
                fingers = detector.fingersUp(hand)

                if fingers == [0, 1, 0, 0, 0]:  # Drawing with index finger
                    curr_pos = lmList[8][0:2]
                    if prev_pos is None:
                        prev_pos = curr_pos
                    cv2.line(canvas, prev_pos, curr_pos, (0, 0, 255), 4)
                    prev_pos = curr_pos
                    # Draw pointer
                    cv2.circle(img, curr_pos, 8, (0, 255, 0), cv2.FILLED)
                else:
                    prev_pos = None

                if fingers == [0, 0, 0, 0, 0]:  # Clear canvas with fist
                    canvas = np.ones_like(img, np.uint8) * 255 if whiteboard_mode else np.zeros_like(img)
                    output_text = ""

                if fingers == [0, 1, 1, 1, 1]:  # Send with 4 fingers
                    pil_img = Image.fromarray(canvas)
                    try:
                        response = model.generate_content(["Solve this and give only final answer", pil_img])
                        output_text = response.text
                    except Exception as e:
                        output_text = f"Gemini Error: {str(e)}"

            # Blend canvas and webcam feed based on background
            if whiteboard_mode:
                display_frame = canvas.copy()
                if hands:
                    display_frame = cv2.addWeighted(img, 0.3, canvas, 0.7, 0)
            else:
                display_frame = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)

            FRAME_WINDOW.image(display_frame, channels="BGR")

            if output_text:
                output_box.markdown(f"### 🧠 Gemini Answer:\n{output_text}")

            cv2.waitKey(1)
    else:
        st.warning("👆 Enable the 'Run Webcam' checkbox to start.")

def run_voice_assistant():
    """Original Voice Assistant Code"""
    st.set_page_config(page_title="🎤 Boliye aur Seekhiye", layout="centered")
    st.title("🎤 Boliye aur Seekhiye – AI Vernacular Learning Buddy")
    
    # Back buttonopencv
    if st.button("← Back to Menu"):
        st.session_state.app_state = 'selection'
        st.rerun()

    # ------------------------- LANGUAGE SELECTION -------------------------
    language = st.selectbox("🌐 Bhasha chuniye / Select Language:", ["Hindi", "English"])
    lang_code = "hi" if language == "Hindi" else "en"
    sr_lang_code = "hi-IN" if language == "Hindi" else "en-IN"

    # ------------------------- VOICE INPUT FUNCTION -------------------------
    def recognize_speech(lang):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎙️ Boliye – AI sun raha hai...", icon="📢")
            audio = r.listen(source, phrase_time_limit=6)
        try:
            text = r.recognize_google(audio, language=lang)
            return text
        except sr.UnknownValueError:
            return "❌ Sorry, couldn't understand. Please try again."
        except sr.RequestError:
            return "⚠️ Speech Recognition service unavailable."

    # ------------------------- GEMINI FUNCTION -------------------------
    def get_answer(question, lang):
        if lang == "hi":
            prompt = (
                f"Tum ek friendly teacher ho jo bachchon ko Hindi mein asaan bhaasha mein concepts samjhata hai. "
                f"Is prashn ka saral aur udaharan ke saath uttar do:\n\n{question}"
            )
        else:
            prompt = (
                f"You are a friendly teacher who explains concepts to children in simple English. "
                f"Answer this question clearly with examples:\n\n{question}"
            )
        try:
            response = model_flash.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"

    # ------------------------- TTS FUNCTION using gTTS + pygame -------------------------
    def speak(text, lang):
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
        
        pygame.mixer.init()
        pygame.mixer.music.load(fp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        os.unlink(fp.name)

    # ------------------------- UI LAYOUT -------------------------
    st.subheader("🧠 Apna prashn bol kar puchhiye / Speak your question")

    if st.button("🎤 Click to Speak"):
        with st.spinner("Listening..."):
            user_question = recognize_speech(sr_lang_code)
            st.success(f"🗣️ You asked: {user_question}")
            
            with st.spinner("Gemini is thinking..."):
                answer = get_answer(user_question, lang_code)
                st.session_state['last_answer'] = answer
                st.session_state['last_lang'] = lang_code  # Store language too
                st.markdown("### 📄 Gemini's Answer:")
                st.markdown(answer)
                st.markdown("---")

    # Play the last answer if available
    if 'last_answer' in st.session_state:
        if st.button("🔊 Answer Suno / Hear Answer"):
            speak(st.session_state['last_answer'], st.session_state.get('last_lang', 'hi'))

    # ------------------------- FOOTER -------------------------
    st.markdown("""
    <style>
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def run_flashcards():
    """FlashLearn Cards Application"""
    st.set_page_config(page_title="🃏 FlashLearn Cards", layout="centered")
    
    # Custom CSS for flashcards
    st.markdown("""
    <style>
    .flashcard-container {
        text-align: center;
        padding: 2rem;
    }
    
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin: 2rem auto;
        max-width: 400px;
        color: white;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        animation: cardFlip 0.6s ease-in-out;
    }
    
    .flashcard-emoji {
        font-size: 8rem;
        margin-bottom: 1rem;
        animation: bounce 2s infinite;
    }
    
    .flashcard-word {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .flashcard-description {
        font-size: 1.2rem;
        opacity: 0.9;
        line-height: 1.5;
    }
    
    .progress-stats {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .feedback-correct {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: fadeIn 0.5s ease-in;
    }
    
    .feedback-incorrect {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes cardFlip {
        0% { transform: rotateY(-180deg); opacity: 0; }
        100% { transform: rotateY(0deg); opacity: 1; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-20px); }
        60% { transform: translateY(-10px); }
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🃏 FlashLearn Cards")
    
    # Back button
    if st.button("← Back to Menu"):
        st.session_state.app_state = 'selection'
        st.rerun()
    
    # Initialize current card
    if st.session_state.current_card >= len(FLASHCARDS):
        st.session_state.current_card = 0
    
    current_flashcard = FLASHCARDS[st.session_state.current_card]
    
    # Display current flashcard
    st.markdown(f"""
    <div class="flashcard">
        <div class="flashcard-emoji">{current_flashcard['image']}</div>
        <div class="flashcard-word">{current_flashcard['word']}</div>
        <div class="flashcard-description">{current_flashcard['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress display
    progress = st.session_state.flashcard_progress
    st.markdown(f"""
    <div class="progress-stats">
        <h3>📊 Learning Progress</h3>
        <p>✅ Correct: {progress['correct']} | ❌ Incorrect: {progress['incorrect']}</p>
        <p>Card {st.session_state.current_card + 1} of {len(FLASHCARDS)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➡️ Next Card", use_container_width=True):
            st.session_state.current_card = (st.session_state.current_card + 1) % len(FLASHCARDS)
            st.rerun()
    
    with col2:
        if st.button("🔊 Speak Word", use_container_width=True):
            try:
                tts = gTTS(text=current_flashcard['word'], lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                
                pygame.mixer.init()
                pygame.mixer.music.load(fp.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
                os.unlink(fp.name)
                st.success("🔊 Word spoken!")
            except Exception as e:
                st.error(f"TTS Error: {str(e)}")
    
    with col3:
        if st.button("🎤 Voice Test", use_container_width=True):
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("🎙️ Say the word shown on the card...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, phrase_time_limit=3)
                
                spoken_word = r.recognize_google(audio, language="en-US").lower()
                correct_word = current_flashcard['word'].lower()
                
                # Check if the spoken word matches (allowing for some flexibility)
                is_correct = (spoken_word == correct_word or 
                             spoken_word in correct_word or 
                             correct_word in spoken_word or
                             any(word in correct_word for word in spoken_word.split()))
                
                if is_correct:
                    st.session_state.flashcard_progress['correct'] += 1
                    feedback_message = f"🎉 Great job! You said '{spoken_word}' - That's correct!"
                    
                    st.markdown(f"""
                    <div class="feedback-correct">
                        <h3>{feedback_message}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Speak positive feedback
                    try:
                        tts = gTTS(text="Great job! That's correct!", lang='en')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                        
                        pygame.mixer.init()
                        pygame.mixer.music.load(fp.name)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        pygame.mixer.quit()
                        os.unlink(fp.name)
                    except:
                        pass
                        
                else:
                    st.session_state.flashcard_progress['incorrect'] += 1
                    feedback_message = f"Try again! You said '{spoken_word}', but the correct word is '{current_flashcard['word']}'"
                    
                    st.markdown(f"""
                    <div class="feedback-incorrect">
                        <h3>{feedback_message}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Speak corrective feedback
                    try:
                        tts = gTTS(text=f"Try again! The correct word is {current_flashcard['word']}", lang='en')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                        
                        pygame.mixer.init()
                        pygame.mixer.music.load(fp.name)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        pygame.mixer.quit()
                        os.unlink(fp.name)
                    except:
                        pass
                
                st.rerun()
                
            except sr.UnknownValueError:
                st.error("❌ Sorry, I couldn't understand what you said. Please try again.")
            except sr.RequestError:
                st.error("⚠️ Speech Recognition service is unavailable.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Study mode options
    st.markdown("---")
    st.subheader("📚 Study Options")
    
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("🔄 Reset Progress", use_container_width=True):
            st.session_state.flashcard_progress = {"correct": 0, "incorrect": 0}
            st.success("Progress reset!")
            st.rerun()
    
    with col5:
        if st.button("🎯 Random Card", use_container_width=True):
            import random
            st.session_state.current_card = random.randint(0, len(FLASHCARDS) - 1)
            st.rerun()
    
    # AI-powered explanation
    st.markdown("---")
    if st.button("🤖 AI Explanation", use_container_width=True):
        with st.spinner("AI is generating explanation..."):
            try:
                prompt = f"Explain the word '{current_flashcard['word']}' to a child in simple English with fun examples and interesting facts."
                response = model_flash.generate_content(prompt)
                st.markdown("### 🤖 AI Teacher Says:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")

# Main application logic
def main():
    # Handle keyboard input for Enter key
    if st.session_state.app_state == 'welcome':
        # Check for Enter key simulation (using empty text input)
        enter_key = st.text_input("", placeholder="Press Enter to continue...", key="enter_input", label_visibility="hidden")
        if enter_key == "" and st.session_state.app_state == 'welcome':
            show_welcome_screen()
        elif enter_key:
            st.session_state.app_state = 'selection'
            st.session_state.show_animation = True
            st.rerun()
    
    elif st.session_state.app_state == 'selection':
        show_app_selection()
    
    elif st.session_state.app_state == 'running':
        if st.session_state.selected_app == 'handwriting_solver':
            run_handwriting_solver()
        elif st.session_state.selected_app == 'voice_assistant':
            run_voice_assistant()
        elif st.session_state.selected_app == 'flashcards':
            run_flashcards()

if __name__ == "__main__":
    main()