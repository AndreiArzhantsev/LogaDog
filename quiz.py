import streamlit as st
import random
from typing import List, Set, Dict, Optional
import math
import numpy as np

from capitals_gt import country_capitals as COUNTRY_CAPITALS

NUM_QUESTIONS = 14
NUM_VALIDATION = 7

def sum_of_k_subset_products(p, k):
    coeffs = [1]
    for x in p:
        new_coeffs = [0] * (min(len(coeffs) + 1, k + 1))
        for i in range(len(coeffs)):
            new_coeffs[i] += coeffs[i]
            if i + 1 <= k:
                new_coeffs[i + 1] += coeffs[i] * x
        coeffs = new_coeffs
    return coeffs[k] if k <= len(coeffs) - 1 else 0

def permutation_rank(a):
    sorted_a = sorted(a)
    perm = [sorted_a.index(x) for x in a]
    n = len(perm)
    rank = 0
    used = [False] * n
    for i in range(n):
        less = sum(1 for j in range(perm[i]) if not used[j])
        rank += less * math.factorial(n - i - 1)
        used[perm[i]] = True
    return rank + 1

def calculate_optimal_guesses(
        selected_options: List[List[str]],
        validation_indices: Set[int], 
        questions: List[Dict]
    ) -> Optional[int]:
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
            processed_selections.append((8, questions[i]['options'].index(questions[i]['correct'])))
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
    processed_selections_guesses = [i[0] for i in processed_selections]
    for val, k in zip(validation_selections, ks):
        m, t = val
        total_guesses += sum_of_k_subset_products(processed_selections_guesses[:m-1], k)
        total_guesses += t * sum_of_k_subset_products(processed_selections_guesses[:m-1], k-1)
    
    total_guesses *= math.factorial(k) 
    total_guesses += permutation_rank(validation_indices)
    return total_guesses

def get_quiz():
    countries = random.sample(list(COUNTRY_CAPITALS.keys()), NUM_QUESTIONS)
    questions = []
    for country in countries:
        correct = COUNTRY_CAPITALS[country]
        # Get 7 random wrong answers
        wrong_answers = random.sample([c for c in COUNTRY_CAPITALS.values() if c != correct], 7)
        options = wrong_answers + [correct]
        random.shuffle(options)
        questions.append({
            'country': country,
            'correct': correct,
            'options': options
        })
    validation_indices = random.sample(range(NUM_QUESTIONS), NUM_VALIDATION)
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
st.write("Select the capital for each country. 7 questions are validation questions.")
st.write("For each choose set of answer, where you are sure that the right answer is inside.")
st.write("After submitting your answers, the program will calculate the optimal number of guesses needed to find the right answer.")

def check_win_condition():
    # Check if all validation questions are answered correctly
    for idx in st.session_state.validation_indices:
        ans = st.session_state.selected[idx]
        if ans is None or ans != st.session_state.quiz[idx]['correct']:
            return False
    return True

if not st.session_state.finished:
    for idx, q in enumerate(st.session_state.quiz):
        st.markdown(f"**{idx+1}. {q['country']}**")
        # Create two rows of 4 columns each
        row1_cols = st.columns(4)
        row2_cols = st.columns(4)
        
        # First row (options 0-3)
        for opt_idx, opt in enumerate(q['options'][:4]):
            if row1_cols[opt_idx].button(
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
        
        # Second row (options 4-7)
        for opt_idx, opt in enumerate(q['options'][4:]):
            if row2_cols[opt_idx].button(
                opt, 
                key=f"{idx}-{opt_idx+4}",
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

        formatted_guesses = f"{optimal_guesses:.2e}"
        e_perfect = (math.factorial(NUM_QUESTIONS) // math.factorial(NUM_QUESTIONS-NUM_VALIDATION) + 1) / 2
        e_perfect_formatted = f"{e_perfect:.2e}"
        std_perfect = math.sqrt(((math.factorial(NUM_QUESTIONS) // math.factorial(NUM_QUESTIONS-NUM_VALIDATION))**2 - 1) / 12)
        std_perfect_formatted = f"{std_perfect:.2e}"
        st.write("**Right answer is inside your answer!**")
        st.write(f"**Actual number of guesses needed to find it, based on your answers:** {formatted_guesses}")
        cnt = []
        for _ in range(1000):
            validation_indices = random.sample(range(NUM_QUESTIONS), NUM_VALIDATION)
            optimal_guesses = calculate_optimal_guesses(
                st.session_state.selected,
                validation_indices,
                st.session_state.quiz
            )
            cnt.append(optimal_guesses)
        st.write(f"**Estimated Average of number of guesses for your answer**: {np.mean(cnt):.2e}")
        st.write(f"**Estimated STD of number of guesses for your answer**: {np.std(cnt):.2e}")
        st.write(f"**Average number of guesses with perfect answers:** {e_perfect_formatted} guesses")
        st.write(f"**STD of number of guesses with perfect answers:** {std_perfect_formatted} guesses")
    else:
        st.write("**Impossible to find validation set with current selections**")
