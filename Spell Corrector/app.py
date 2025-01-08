import streamlit as st
from spellchecker import SpellChecker
from fuzzywuzzy import process, fuzz
import os

# Initialize PySpellChecker
def initialize_pyspellchecker():
    spell = SpellChecker(language=None)
    custom_word_list = "word_list.txt"
    if os.path.exists(custom_word_list):
        with open(custom_word_list, "r", encoding="utf-8") as file:
            words = file.read().splitlines()
            spell.word_frequency.load_words(words)
    return spell

# Correct Word Using PySpellChecker
def correct_word_pyspellchecker(spell, word):
    return spell.correction(word) or word

# Correct Word Using FuzzyWuzzy
def correct_word_fuzzywuzzy(word, dictionary):
    best_match = process.extractOne(word, dictionary, scorer=fuzz.ratio)
    return best_match[0] if best_match and best_match[1] > 80 else word

# Correct and Evaluate Paragraph
def correct_paragraph(paragraph, spell, dictionary):
    words = paragraph.split()
    corrected_pyspell = []
    corrected_fuzzywuzzy = []

    for word in words:
        corrected_pyspell.append(correct_word_pyspellchecker(spell, word))
        corrected_fuzzywuzzy.append(correct_word_fuzzywuzzy(word, dictionary))

    return corrected_pyspell, corrected_fuzzywuzzy

# Load Word List
def load_word_list(word_list_path):
    try:
        with open(word_list_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        st.error(f"Word list file '{word_list_path}' not found.")
        return []

# Calculate Accuracy
def calculate_accuracy(corrected_words, reference_words):
    correct_count = sum(1 for c, r in zip(corrected_words, reference_words) if c == r)
    accuracy = correct_count / len(reference_words) if reference_words else 0
    return accuracy * 100  # Percentage

# Streamlit UI
def main():
    # Page Layout and Custom Styles
    st.set_page_config(page_title="Flawless Text Enhancer", layout="wide")

    # Custom CSS for Styling
    st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f7f7f7;
            color: #333;
        }
        h1 {
            color: #4CAF50;
            font-size: 3em;
            text-align: center;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1.1em;
            border: none;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .stTextArea textarea {
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 20px;
            font-size: 1.1em;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
        }
        .stTextArea textarea:focus {
            border-color: #4CAF50;
            outline: none;
        }
        .column-container {
            display: flex;
            justify-content: center;
            gap: 100px;
            width: 50%;
        }
        .stContainer {
            padding: 15px;
            width: 50%;
        }
        .stSubheader {
            color: #4CAF50;
            font-size: 1.5em;
        }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<h1>Flawless Text Enhancer 🌟</h1>", unsafe_allow_html=True)

    # Initialize SpellChecker
    spell = initialize_pyspellchecker()

    # Load Dictionary
    word_list_path = "word_list.txt"
    dictionary = load_word_list(word_list_path)

    # Input and Output Columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Text")
        paragraph_to_correct = st.text_area("Enter a paragraph:", "", height=200)

        # Centered Correct Button
        correct_button = st.empty()
        with correct_button.container():
            if st.button("Correct Spelling", key="correct_button_input"):
                if paragraph_to_correct.strip():
                    # Perform Correction
                    corrected_pyspell, corrected_fuzzywuzzy = correct_paragraph(paragraph_to_correct, spell, dictionary)

                    # Combine Results
                    combined_results_text = "PySpellChecker Result:\n" + " ".join(corrected_pyspell)
                    combined_results_text += "\n\nFuzzyWuzzy Result:\n" + " ".join(corrected_fuzzywuzzy)

                    # Calculate and Include Accuracy
                    reference_text = "මිනිසුන් දෙදනෙකු මටර් රථ ක්‍රීඩවක යෙදෙයි. .තරඟකරුවෙක් අනකා හඹා යයි. මිනිසෙක් ධානය වන මොටර් රයක එල්ල සිටිය."
                    reference_words = reference_text.split()

                    accuracy_pyspell = calculate_accuracy(corrected_pyspell, reference_words)
                    accuracy_fuzzywuzzy = calculate_accuracy(corrected_fuzzywuzzy, reference_words)

                    accuracy_text = f"\n\nAccuracy Results:\nPySpellChecker Accuracy: {accuracy_pyspell:.2f}%\nFuzzyWuzzy Accuracy: {accuracy_fuzzywuzzy:.2f}%"
                    combined_results_text += accuracy_text

                    # Display Results
                    st.session_state['combined_results'] = combined_results_text
                else:
                    st.warning("Please enter text to correct.")

    with col2:
        st.subheader("Corrected Text")
        combined_results = st.text_area("Results:", st.session_state.get('combined_results', ''), height=200, disabled=True)

        # Centered Clear Button
        clear_button = st.empty()
        with clear_button.container():
            if st.button("Clear Text", key="clear_button_output"):
                st.session_state['combined_results'] = ""
                st.rerun()

if __name__ == "__main__":
    main()
