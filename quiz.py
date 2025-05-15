import streamlit as st
import random
from typing import List, Set, Dict, Optional
import math
import numpy as np

from capitals_gt import country_capitals as COUNTRY_CAPITALS

NUM_QUESTIONS = 20
NUM_VALIDATION = 10

def calculate_optimal_guesses(selected_options: List[List[str]], validation_indices: Set[int], questions: List[Dict]) -> Optional[int]:
    """
    Calculate optimal number of guesses needed to find validation set and correct answers.
    
    Args:
        selected_options: List of lists containing selected options for each question
        validation_indices: Set of indices of validation questions
        questions: List of question dictionaries containing correct answers
    
    Returns:
        Optimal number of guesses or None if impossible
    """
    # Convert empty selections to all options selected
    processed_selections = []
    for i, selections in enumerate(selected_options):
        if not selections:  # If no options selected, consider all options selected
            processed_selections.append((4, questions[i]['options'].index(questions[i]['correct'])))
        else:
            if questions[i]['correct'] not in selections:
                return None
            correct_idx = selections.index(questions[i]['correct'])
            processed_selections.append((len(selections), correct_idx))
    
    # Sort by number of selected options (ascending)
    processed_selections.sort(key=lambda x: x[0])
    print(processed_selections)
    # Filter validation questions and sort by their position in the sorted list
    validation_selections = [(i+1, t[1]) for i, t in enumerate(processed_selections) if i in validation_indices]
    validation_selections.sort()
    print(validation_selections)
    ks = [i+1 for i in range(len(validation_indices))]

    total_guesses = 0
    for val, k in zip(validation_selections[::-1], ks[::-1]):
        m, t = val
        print(m,k,t)
        if m > k:
            total_guesses += (math.factorial(m-1) // math.factorial(k))
        total_guesses += (t * k * math.factorial(m-1) // math.factorial(k-1))
    
    return total_guesses

def get_quiz():
    countries = random.sample(list(COUNTRY_CAPITALS.keys()), NUM_QUESTIONS)
    questions = []
    for country in countries:
        correct = COUNTRY_CAPITALS[country]
        # Get 3 random wrong answers
        wrong_answers = random.sample([c for c in COUNTRY_CAPITALS.values() if c != correct], 3)
        options = wrong_answers + [correct]
        random.shuffle(options)
        questions.append({
            'country': country,
            'correct': correct,
            'options': options
        })
    validation_indices = set(random.sample(range(NUM_QUESTIONS), NUM_VALIDATION))
    return questions, validation_indices

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.quiz, st.session_state.validation_indices = get_quiz()
    st.session_state.selected = [[] for _ in range(NUM_QUESTIONS)]
    st.session_state.clicks = 0
    st.session_state.non_validation_clicks = 0
    st.session_state.finished = False
    st.session_state.initialized = True

st.title("Country-Capital Quiz")
st.write("Select the capital for each country. 5 questions are validation questions (chosen randomly).")

def check_win_condition():
    # Check if all validation questions are answered correctly
    for idx in st.session_state.validation_indices:
        ans = st.session_state.selected[idx]
        if ans is None or ans != st.session_state.quiz[idx]['correct']:
            return False
    return True

if not st.session_state.finished:
    # Display quiz for user
    for idx, q in enumerate(st.session_state.quiz):
        st.markdown(f"**{idx+1}. {q['country']}**")
        cols = st.columns(4)
        for opt_idx, opt in enumerate(q['options']):
            if cols[opt_idx].button(
                opt, 
                key=f"{idx}-{opt_idx}",
                type="primary" if opt in st.session_state.selected[idx] else "secondary"
            ):
                if opt in st.session_state.selected[idx]:
                    st.session_state.selected[idx].remove(opt)
                else:
                    st.session_state.selected[idx].append(opt)
                st.session_state.clicks += 1
                if idx not in st.session_state.validation_indices:
                    st.session_state.non_validation_clicks += 1
                st.rerun()

    if st.button("Submit Answers"):
        st.session_state.finished = True

if st.session_state.finished:
    # Calculate optimal number of guesses
    optimal_guesses = calculate_optimal_guesses(
        st.session_state.selected,
        st.session_state.validation_indices,
        st.session_state.quiz
    )
    
    # Count correct answers (final answer) for all questions
    correct_final = 0
    for idx, ans in enumerate(st.session_state.selected):
        if ans and st.session_state.quiz[idx]['correct'] in ans:
            correct_final += 1

    # Count non-validation questions with no choice
    no_choice_non_validation = 0
    for idx in range(NUM_QUESTIONS):
        if idx not in st.session_state.validation_indices and not st.session_state.selected[idx]:
            no_choice_non_validation += 1

    # Count correct answers in validation and non-validation sets
    correct_validation = 0
    correct_non_validation = 0
    for idx, ans in enumerate(st.session_state.selected):
        if ans and st.session_state.quiz[idx]['correct'] in ans:
            if idx in st.session_state.validation_indices:
                correct_validation += 1
            else:
                correct_non_validation += 1

    if optimal_guesses is not None:
        st.write("**Right answer is inside your answer!**")
        formatted_guesses = f"{optimal_guesses:.2e}"
        st.write(f"**Actual number of guesses needed to find it, based on your answers:** {formatted_guesses}")
    else:
        st.write("**Impossible to find validation set with current selections**")
