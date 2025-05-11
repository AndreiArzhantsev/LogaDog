import streamlit as st
import random

from capitals_gt import country_capitals as COUNTRY_CAPITALS

NUM_QUESTIONS = 20
NUM_VALIDATION = 10
OPTIONS_PER_QUESTION = 4

def get_quiz():
    countries = random.sample(list(COUNTRY_CAPITALS.keys()), NUM_QUESTIONS)
    capitals = list(COUNTRY_CAPITALS.values())
    questions = []
    for country in countries:
        correct = COUNTRY_CAPITALS[country]
        wrong = random.sample([c for c in capitals if c != correct], OPTIONS_PER_QUESTION - 1)
        options = wrong + [correct]
        random.shuffle(options)
        questions.append({
            'country': country,
            'options': options,
            'correct': correct
        })
    validation_indices = set(random.sample(range(NUM_QUESTIONS), NUM_VALIDATION))
    return questions, validation_indices

if 'quiz' not in st.session_state:
    st.session_state.quiz, st.session_state.validation_indices = get_quiz()
    st.session_state.selected = [None] * NUM_QUESTIONS
    st.session_state.clicks = 0
    st.session_state.non_validation_clicks = 0
    st.session_state.finished = False

st.title("Country-Capital Quiz")
st.write("Select the capital for each country. 10 questions are validation questions (chosen randomly).")

def on_select(q_idx, opt_idx):
    st.session_state.clicks += 1
    if q_idx not in st.session_state.validation_indices:
        st.session_state.non_validation_clicks += 1
    st.session_state.selected[q_idx] = opt_idx

    # Check if all validation questions are answered correctly
    all_correct = True
    for idx in st.session_state.validation_indices:
        ans = st.session_state.selected[idx]
        if ans is None or st.session_state.quiz[idx]['options'][ans] != st.session_state.quiz[idx]['correct']:
            all_correct = False
            break
    if all_correct:
        st.session_state.finished = True

if not st.session_state.finished:
    for idx, q in enumerate(st.session_state.quiz):
        st.markdown(f"**{idx+1}. {q['country']}**")
        cols = st.columns(4)
        for opt_idx, opt in enumerate(q['options']):
            if cols[opt_idx].button(opt, key=f"{idx}-{opt_idx}"):
                on_select(idx, opt_idx)
        if st.session_state.selected[idx] is not None:
            st.write(f"Selected: {q['options'][st.session_state.selected[idx]]}")

if st.session_state.finished:
    correct_final = 0
    for idx, ans in enumerate(st.session_state.selected):
        if ans is not None and st.session_state.quiz[idx]['options'][ans] == st.session_state.quiz[idx]['correct']:
            correct_final += 1
    no_choice_non_validation = 0
    for idx in range(NUM_QUESTIONS):
        if idx not in st.session_state.validation_indices and st.session_state.selected[idx] is None:
            no_choice_non_validation += 1
    correct_validation = 0
    correct_non_validation = 0
    for idx, ans in enumerate(st.session_state.selected):
        if ans is not None and st.session_state.quiz[idx]['options'][ans] == st.session_state.quiz[idx]['correct']:
            if idx in st.session_state.validation_indices:
                correct_validation += 1
            else:
                correct_non_validation += 1

    st.success(f"Quiz complete! You got all {NUM_VALIDATION} validation questions correct.")
    st.write(f"**Total clicks:** {st.session_state.clicks}")
    st.write(f"**Non-validation questions with no choice:** {no_choice_non_validation}")
    st.write(f"**Correct answers outside validation questions:** {correct_non_validation} / {NUM_QUESTIONS - len(st.session_state.validation_indices)}")
    st.button("Restart Quiz", on_click=lambda: st.session_state.clear())