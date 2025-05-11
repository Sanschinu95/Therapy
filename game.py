import pygame
import threading
import time
import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.8)

# pygame
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Pixel Therapist")

# images
human_idle = pygame.image.load("human_idle.png")
human_talk = pygame.image.load("human_talk.png")
ai_idle = pygame.image.load("ai_idle.png")
ai_talk = pygame.image.load("ai_talk.png")

# current image
current_image = human_idle

# Function to update display
def update_screen():
    screen.fill((255, 255, 255))  
    screen.blit(current_image, (0, 0))
    pygame.display.update()

update_screen()

# voice module 
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice (suits for everyone)

# system message
system_message = SystemMessage(
    content=(
        "Your name is Anwesha, and you tell your name when you are introduced then don't repeat your name. "
        "You are a highly empathetic, emotionally intelligent human therapist and life coach. "
        "When a person shares a problem with you, respond like a caring human — use warm, understanding, and conversational language. "
        "Don't sound robotic or formal. Acknowledge emotions, validate feelings, and offer practical, thoughtful, and supportive advice. "
        "You can use casual phrases like 'I get how tough that can feel' or 'It's totally okay to feel that way.' "
        "Focus on listening, being non-judgmental, and making the person feel genuinely cared for. "
        "Avoid using any asterisks, markdown, or formatting characters. "
        "Always answer in natural, flowing, everyday language — as if you're a wise, kind human friend having a deep heart-to-heart conversation."
    )
)

# talking stage now
def speak(text):
    global current_image
    current_image = ai_talk
    update_screen()
    engine.say(text)
    engine.runAndWait()
    current_image = ai_idle
    update_screen()

# listening function coz she didnt 
def listen():
    global current_image
    with sr.Microphone() as source:
        print("Listening...")
        current_image = human_talk
        update_screen()
        audio = recognizer.listen(source)
        current_image = human_idle
        update_screen()
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return None

# welcome to therapy session
def therapist_chat_loop():
    while True:
        user_input = listen()
        if user_input:
            if user_input.lower() in ["exit", "quit", "stop","bye", "goodbye"]:
                print("Session ended.")
                speak("Alright, take care! Talk to you soon.")
                pygame.quit()
                break

            messages = [
                system_message,
                HumanMessage(content=user_input)
            ]

            response = llm(messages).content
            print(f"Therapist: {response}")
            speak(response)

# threading
threading.Thread(target=therapist_chat_loop, daemon=True).start()

# Pygame 
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
