import random
from datetime import datetime
from collections import Counter
from textblob import TextBlob
from spellchecker import SpellChecker
from transformers import BartForConditionalGeneration, BartTokenizer
from translate import Translator
from unidecode import unidecode
import streamlit as st

st.title("Chatbot")
st.write("Hello, I am a chatbot created by students of XI B. How may I help you?")

options = [
    "What's the time right now?",
    "Number guessing game",
    "Rock Paper Scissors with Prediction",
    "Emotion analysis",
    "Text summarization",
    "Translate text",
    "Spell Checker",
    "Exit"
]

choice = st.selectbox("Choose an option:", options)

if choice == "What's the time right now?":
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    st.write(f"The current time is {current_time}")

elif choice == "Number guessing game":
    if "secret_number" not in st.session_state or "win" in st.session_state and st.session_state.win:
        st.session_state.secret_number = random.randint(1, 50)
        st.session_state.attempts = 0
        st.session_state.win = False

    secret_number = st.session_state.secret_number
    attempts = st.session_state.attempts
    win = st.session_state.win

    if win:
        st.write(f"Congratulations! You guessed the number in {attempts} attempts.")
        if st.button("Play Again"):
            st.session_state.secret_number = random.randint(1, 50)
            st.session_state.attempts = 0
            st.session_state.win = False
    else:
        st.write("I have chosen a number between 1 and 50. Can you guess it?")
        guess = st.number_input("Enter your guess:", min_value=1, max_value=50, step=1, key="guess")

        if st.button("Submit Guess"):
            st.session_state.attempts += 1
            attempts = st.session_state.attempts

            if guess < secret_number:
                st.write("Too low! Try again.")
            elif guess > secret_number:
                st.write("Too high! Try again.")
            else:
                st.write(f"Congratulations! You guessed the number in {attempts} attempts.")
                st.session_state.win = True

elif choice == "Rock Paper Scissors with Prediction":
    st.write("Enter 'rock', 'paper', or 'scissors' to play.")
    moves = ["rock", "paper", "scissors"]
    player_move = st.selectbox("Your move:", moves)
    player_history = st.session_state.get("player_history", [])
    ai_score = st.session_state.get("ai_score", 0)
    player_score = st.session_state.get("player_score", 0)

    if st.button("Play Round"):
        # AI move logic
        if not player_history:
            ai_move = random.choice(moves)
        else:
            move_counts = Counter(player_history)
            predicted_player_move = max(move_counts, key=move_counts.get)
            ai_move = "rock" if predicted_player_move == "scissors" else (
                "paper" if predicted_player_move == "rock" else "scissors")

        # Update player history
        player_history.append(player_move)
        st.session_state.player_history = player_history

        # Display AI's choice
        st.write(f"AI chose: {ai_move}")

        # Determine game outcome
        if player_move == ai_move:
            st.write("It's a tie!")
        elif (player_move == "rock" and ai_move == "scissors") or \
             (player_move == "paper" and ai_move == "rock") or \
             (player_move == "scissors" and ai_move == "paper"):
            st.write("You win this round!")
            player_score += 1
        else:
            st.write("AI wins this round!")
            ai_score += 1

        # Save session state
        st.session_state.ai_score = ai_score
        st.session_state.player_score = player_score

        # Show scores
        st.write(f"Score - You: {player_score}, AI: {ai_score}")


elif choice == "Emotion analysis":
    user_text = st.text_area("Enter your text for sentiment analysis:")

    if st.button("Analyze Sentiment"):
        analysis = TextBlob(user_text)
        sentiment_score = analysis.sentiment.polarity
        sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
        st.write(f"The sentiment of your message is '{sentiment}'.")

elif choice == "Text summarization":
    user_text = st.text_area("Enter the text to summarize:")

    if st.button("Summarize"):
        model_name = "facebook/bart-large-cnn"
        tokenizer = BartTokenizer.from_pretrained(model_name)
        model = BartForConditionalGeneration.from_pretrained(model_name)

        inputs = tokenizer.encode("summarize: " + user_text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=130, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        st.write(summary)

elif choice == "Translate text":
    user_text = st.text_input("Enter text to translate:")
    language = st.selectbox("Choose a language:", ["Spanish", "Korean", "Japanese"])
    lang_code = {"Spanish": "es", "Korean": "ko", "Japanese": "ja"}[language]

    if st.button("Translate"):
        translator = Translator(from_lang="en", to_lang=lang_code)
        translated_text = translator.translate(user_text)
        transliterated_text = unidecode(translated_text)
        st.write(f"Translated Text: {transliterated_text}")

elif choice == "Spell Checker":
    user_text = st.text_input("Enter text to check spelling:")

    if st.button("Check Spelling"):
        spell = SpellChecker()
        misspelled_words = spell.unknown(user_text.split())

        if misspelled_words:
            st.write("Potential spelling mistakes:")
            for word in misspelled_words:
                st.write(f"'{word}' -> {', '.join(spell.candidates(word))}")
        else:
            st.write("No spelling mistakes found.")

elif choice == "Exit":
    st.write("Goodbye!")