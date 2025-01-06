import streamlit as st
from spellchecker import SpellChecker
from fuzzywuzzy import process, fuzz
import os
import time

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

# Evaluate Accuracy of Each Method
def evaluate_accuracy(correct_word, ground_truth):
    return 1 if correct_word == ground_truth else 0

# Correct Word and Evaluate Accuracy
def correct_word_and_evaluate(word, ground_truth, spell, dictionary):
    corrected_pyspell = correct_word_pyspellchecker(spell, word)
    accuracy_pyspell = evaluate_accuracy(corrected_pyspell, ground_truth)
    
    corrected_fuzzywuzzy = correct_word_fuzzywuzzy(word, dictionary)
    accuracy_fuzzywuzzy = evaluate_accuracy(corrected_fuzzywuzzy, ground_truth)
    
    return corrected_pyspell, corrected_fuzzywuzzy, accuracy_pyspell, accuracy_fuzzywuzzy

# Load Word List (Correct Words Only)
def load_word_list(word_list_path):
    dictionary = []
    try:
        with open(word_list_path, "r", encoding="utf-8") as file:
            for line in file:
                dictionary.append(line.strip())
    except FileNotFoundError:
        print(f"Word list file '{word_list_path}' not found.")
        exit()
    return dictionary

# Correct and Evaluate Paragraph
def correct_paragraph(paragraph, spell, dictionary):
    words = paragraph.split()  # Split paragraph into words
    corrected_paragraph_pyspell = []
    corrected_paragraph_fuzzywuzzy = []
    total_accuracy = {"pyspell": 0, "fuzzywuzzy": 0}
    total_words = len(words)

    # Simulate processing
    for word in words:
        # Find the closest match from the word list (ground truth)
        best_match = process.extractOne(word, dictionary, scorer=fuzz.ratio)
        if best_match and best_match[1] > 80:
            ground_truth = best_match[0]
        else:
            ground_truth = word  # If no close match, use the original word as ground truth
        
        corrected_pyspell, corrected_fuzzywuzzy, accuracy_pyspell, accuracy_fuzzywuzzy = correct_word_and_evaluate(
            word, ground_truth, spell, dictionary)

        corrected_paragraph_pyspell.append(corrected_pyspell)
        corrected_paragraph_fuzzywuzzy.append(corrected_fuzzywuzzy)

        total_accuracy["pyspell"] += accuracy_pyspell
        total_accuracy["fuzzywuzzy"] += accuracy_fuzzywuzzy

    return corrected_paragraph_pyspell, corrected_paragraph_fuzzywuzzy, total_accuracy, total_words

# Streamlit UI
def main():
    # Set up page layout and title
    st.set_page_config(page_title="Text Correction App", layout="wide")

    # Add custom styles for a more dynamic UI
    st.markdown("""
    <style>
    body {
        background-color: #f7f7f7;
        color: #333;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput, .stTextArea {
        border-radius: 10px;
        padding: 10px;
        background-color: #000000;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
    }
    .stTextInput:focus, .stTextArea:focus {
        background-color: #fff;
        border-color: #4e73df;
    }
    .stButton>button {
        background-color: #3e9c35;
        color: white;
        font-size: 16px;
        padding: 10px 20px;
        border-radius: 5px;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.15);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2f8b2d;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.2);
    }
    .stMarkdown {
        font-size: 16px;
        color: #444;
    }
    .progress-bar {
        height: 10px;
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 5px;
        margin-top: 20px;
    }
    .progress-bar > div {
        height: 100%;
        background-color: #4e73df;
        border-radius: 5px;
        transition: width 0.5s ease-in-out;
    }
    .button-container {
        display: flex;
        justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("Spell Corrector")

    # Initialize PySpellChecker
    pyspell = initialize_pyspellchecker()

    # Load dictionary from word list (correct words only)
    word_list_path = "word_list.txt"
    dictionary = load_word_list(word_list_path)

    # Ensure word list is not empty
    if not dictionary:
        st.error("No valid words found in the word list. Please check the file format.")
        return

    # Two columns for input and corrected text
    col1, col2 = st.columns(2)

    with col1:
        # Input box for incorrect text
        paragraph_to_correct = st.text_area("Enter a paragraph to correct:", "", height=200)

    with col2:
        # Display corrected text with accuracies
        if paragraph_to_correct:
            corrected_paragraph_pyspell, corrected_paragraph_fuzzywuzzy, total_accuracy, total_words = correct_paragraph(
                paragraph_to_correct, pyspell, dictionary)

            # Show corrected text with accuracies
            corrected_text = "\n".join([ 
                f"PySpellChecker: {' '.join(corrected_paragraph_pyspell)} \nAccuracy: {total_accuracy['pyspell'] / total_words * 100:.2f}%", 
                f"\n\nFuzzyWuzzy: {' '.join(corrected_paragraph_fuzzywuzzy)} \nAccuracy: {total_accuracy['fuzzywuzzy'] / total_words * 100:.2f}%" 
            ])
            
            # Use unique key for text_area
            st.text_area("Corrected Text with Accuracy:", value=corrected_text, height=200, disabled=True, key="corrected_text_area")

    # Row for buttons
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    
    # Correct Spelling button and Clear Text button in one row
    col1, col2 = st.columns([3, 1])  # Adjusting column widths for button alignment

    with col1:
        if st.button("Correct Spelling"):
            if paragraph_to_correct:
                # Start processing with progress bar
                progress_bar = st.progress(0)
                st.spinner('Processing...')
                
                # Simulate text correction with a 2-second delay for dynamic feel
                time.sleep(2)

                corrected_paragraph_pyspell, corrected_paragraph_fuzzywuzzy, total_accuracy, total_words = correct_paragraph(
                    paragraph_to_correct, pyspell, dictionary)

                # Show progress bar completion
                progress_bar.progress(100)

    with col2:
        if st.button("Clear Text"):
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
