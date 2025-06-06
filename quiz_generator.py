import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
import random
import time
from datetime import datetime
from constants import get_parameters
from answer_guesser import find_validation_set, count_complexity
from capitals_gt import country_capitals as COUNTRY_CAPITALS


def load_tasks() -> pd.DataFrame:
    """Load tasks from session state"""
    if 'tasks_df' not in st.session_state:
        return pd.DataFrame()
    return st.session_state.tasks_df

def save_answers():
    """Save answers to session state"""
    # Convert answers to DataFrame format
    answers_data = []
    for idx, q in enumerate(st.session_state.quiz):
        selected_capitals = st.session_state.selected[idx]
        # If no capitals selected, use all capitals
        if not selected_capitals:
            selected_capitals = q['capitals']
        
        answers_data.append({
            'country': q['country'],
            'capitals': '|'.join(selected_capitals),
            'group': q['group']
        })
    
    st.session_state.answers_df = pd.DataFrame(answers_data)

def get_quiz(tasks_df: pd.DataFrame) -> List[Dict]:
    """Generate quiz questions from tasks dataframe"""
    questions = []
    for _, row in tasks_df.iterrows():
        questions.append({
            'country': row['country'],
            'capitals': row['capitals'].split('|'),
            'group': row['group']
        })
    
    return questions

def show_quiz_interface():
    """Show the quiz interface"""
    st.title("Country-Capital Quiz Generator")
    
    # Initialize quiz state if not already done
    if 'initialized' not in st.session_state:
        st.session_state.tasks_df = load_tasks()
        st.session_state.quiz = get_quiz(st.session_state.tasks_df)
        st.session_state.selected = [[] for _ in range(len(st.session_state.quiz))]
        st.session_state.initialized = True
        st.session_state.guessing = False
        st.session_state.validation_set = None
        st.session_state.start_time = None
        st.session_state.submission_times = []
        st.session_state.guessing_times = []
    
    # Show target hash at the start
    try:
        target_hash = st.session_state.target_hash
        st.markdown("### Target Hash")
        st.code(target_hash, language='text')
        st.markdown("---")
    except:
        st.error("Target hash not found!")
    
    st.write("Select the capitals for each country. If no capitals are selected, all capitals will be considered as selected.")

    # Start timer if not started
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    if not st.session_state.tasks_df.empty:
        # Group questions by their group number
        grouped_questions = {}
        for idx, q in enumerate(st.session_state.quiz):
            group = q['group']
            if group not in grouped_questions:
                grouped_questions[group] = []
            grouped_questions[group].append((idx, q))
        
        # Display questions by group
        for group_num in sorted(grouped_questions.keys()):
            for idx, q in grouped_questions[group_num]:
                st.markdown(f"**{idx+1}. {q['country']}**")
                
                # Create a single row of columns for the 4 options
                cols = st.columns(4)
                
                # Display all 4 capitals
                for cap_idx, capital in enumerate(q['capitals']):
                    if cols[cap_idx].button(
                        capital,
                        key=f"{idx}-{cap_idx}",
                        type="primary" if capital in st.session_state.selected[idx] else "secondary",
                        disabled=st.session_state.guessing
                    ):
                        if capital in st.session_state.selected[idx]:
                            st.session_state.selected[idx].remove(capital)
                        else:
                            st.session_state.selected[idx].append(capital)
                        st.rerun()
            
            st.markdown("---")  # Add separator between groups

        if st.button("Submit Answers", disabled=st.session_state.guessing):
            st.session_state.guessing = True
            st.rerun()

        if st.button("Count Complexity", disabled=st.session_state.guessing):
            answers = []
            for idx, q in enumerate(st.session_state.quiz):
                selected_capitals = st.session_state.selected[idx]
                # If no capitals selected, use all capitals
                if not selected_capitals:
                    selected_capitals = q['capitals']
                
                answers.append({
                    'country': q['country'],
                    'capitals': '|'.join(selected_capitals)
                })
            
            save_answers()
            complexity = count_complexity()
            formatted_complexity = f"{complexity:.2e}"
            base, exponent = formatted_complexity.split("e")
            st.write(f"Expected number of hash computations: {base} e{exponent}")


    if st.session_state.guessing:
        # Record submission time
        submission_time = time.time() - st.session_state.start_time
        st.session_state.submission_times.append(submission_time)
        
        # Prepare answers for saving
        answers = []
        for idx, q in enumerate(st.session_state.quiz):
            selected_capitals = st.session_state.selected[idx]
            # If no capitals selected, use all capitals
            if not selected_capitals:
                selected_capitals = q['capitals']
            
            answers.append({
                'country': q['country'],
                'capitals': '|'.join(selected_capitals)
            })
        
        save_answers()
        
        guess_start_time = time.time()
        validation_set, outside_validation_tasks, cost = find_validation_set()
        guess_time = time.time() - guess_start_time
        st.session_state.guessing_times.append(guess_time)
        st.session_state.validation_set = validation_set
        st.session_state.outside_validation_tasks = outside_validation_tasks
        st.session_state.cost = cost
        st.session_state.guessing = False
        st.rerun()

    if st.session_state.validation_set is not None:
        st.session_state.start_time = time.time()
        if st.session_state.validation_set == []:
            st.error("No matching validation set found! Please change your answers and try again.")
            st.session_state.validation_set = None
            st.session_state.guessing = False
        else:
            st.success("Found validation set!")
            
            # Display validation set in a table
            st.markdown("### Validation Set")
            validation_df = pd.DataFrame(st.session_state.validation_set, columns=['Country', 'Capital'])
            st.dataframe(validation_df, use_container_width=True)
            
            # Display last attempts for other questions
            if st.session_state.outside_validation_tasks:
                st.markdown("### Tasks Outside Validation")
                outside_validation_tasks_data = []
                for country, capital in st.session_state.outside_validation_tasks:
                    if country not in [c for c, _ in st.session_state.validation_set]:
                        correct_capital = COUNTRY_CAPITALS[country]
                        status = 'Skip' if capital is None else ('Correct' if capital == correct_capital else 'Incorrect')
                        outside_validation_tasks_data.append({
                            'Country': country,
                            'Last Attempted Capital': capital if capital is not None else 'Not attempted',
                            'Correct Capital': correct_capital,
                            'Status': status
                        })
                if outside_validation_tasks_data:
                    outside_validation_tasks_df = pd.DataFrame(outside_validation_tasks_data)
                    st.dataframe(outside_validation_tasks_df, use_container_width=True)
            
            # Add verification section
            st.markdown("### Verification")
            st.markdown("You can verify the hash by running this Python code:")
            verification_code = f"""import hashlib

# Validation set
validation_set = {st.session_state.validation_set}
cost = {st.session_state.cost}

# Concatenate countries and capitals
countries = ''.join(country for country, _ in validation_set)
capitals = ''.join(capital for _, capital in validation_set)
combined = countries + capitals + str(cost)

# Calculate hash
calculated_hash = hashlib.sha256(combined.encode()).hexdigest()
print(f"Calculated hash: {{calculated_hash}}")
"""
            st.code(verification_code, language='python')
            st.markdown("### Timing Summary")
            
            # Calculate and show total times first
            total_submission_time = sum(st.session_state.submission_times)
            total_guessing_time = sum(st.session_state.guessing_times)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Submission Time", f"{total_submission_time:.2f}s")
            with col2:
                st.metric("Total Guessing Time", f"{total_guessing_time:.2f}s")
            with col3:
                st.metric("Total Time", f"{total_submission_time + total_guessing_time:.2f}s")
            
            # Show current attempt time
            st.markdown("#### Current Attempt")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Submission Time", f"{st.session_state.submission_times[-1]:.2f}s")
            with col2:
                st.metric("Guessing Time", f"{st.session_state.guessing_times[-1]:.2f}s")
            
            if len(st.session_state.submission_times) > 1:
                st.markdown("#### Previous Attempts")
                # Create a DataFrame for previous attempts
                attempts_data = []
                for i, (sub_time, guess_time) in enumerate(zip(st.session_state.submission_times[:-1], st.session_state.guessing_times[:-1])):
                    attempts_data.append({
                        'Attempt': i + 1,
                        'Submission Time (s)': f"{sub_time:.2f}",
                        'Guessing Time (s)': f"{guess_time:.2f}",
                        'Total Time (s)': f"{sub_time + guess_time:.2f}"
                    })
                attempts_df = pd.DataFrame(attempts_data)
                st.dataframe(attempts_df, use_container_width=True)
    
    # Add Start New Quiz button at the bottom
    st.markdown("---")
    if st.button("Start New Quiz"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Return to task generation
        st.session_state.page = 'task_generation'
        st.rerun()