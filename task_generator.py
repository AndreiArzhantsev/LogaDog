import pandas as pd
import random
import hashlib
import itertools
from typing import List, Tuple, Dict
from constants import get_parameters
from capitals_gt import country_capitals as COUNTRY_CAPITALS
import streamlit as st

def generate_quiz(num_questions: int = None, validation_size: int = None) -> Tuple[List[Dict], List[Tuple[str, str]]]:
    """Generate a quiz with the specified number of questions and validation set size"""
    # Get current parameters if not provided
    current_num_questions, current_validation_size, _ = get_parameters()
    num_questions = num_questions or current_num_questions
    validation_size = validation_size or current_validation_size
    
    # Randomly select countries
    selected_countries = random.sample(list(COUNTRY_CAPITALS.keys()), min(num_questions, len(COUNTRY_CAPITALS)))
    
    questions = []
    for country in selected_countries:
        correct = COUNTRY_CAPITALS[country]
        # Get 7 random wrong answers
        wrong_answers = random.sample([c for c in COUNTRY_CAPITALS.values() if c != correct], 7)
        options = wrong_answers + [correct]
        random.shuffle(options)
        questions.append({
            'country': country,
            'capitals': options
        })
    
    # Generate validation set
    validation_set = generate_validation_set(questions, validation_size)
    
    return questions, validation_set

def generate_validation_set(questions: List[Dict], validation_size: int) -> List[Tuple[str, str]]:
    """Generate validation set from questions"""
    # Randomly select questions for validation
    validation_questions = random.sample(questions, validation_size)
    
    # For each validation question, use the correct capital
    validation_set = []
    for q in validation_questions:
        country = q['country']
        capital = COUNTRY_CAPITALS[country]
        validation_set.append((country, capital))
    
    return validation_set

def save_quiz_data(questions: List[Dict], validation_set: List[Tuple[str, str]]):
    """Save quiz data to session state"""
    # Convert questions to DataFrame format
    tasks_data = []
    for q in questions:
        tasks_data.append({
            'country': q['country'],
            'capitals': '|'.join(q['capitals'])
        })
    
    # Store in session state
    st.session_state.tasks_df = pd.DataFrame(tasks_data)
    
    # Calculate and store validation hash
    sorted_set = sorted(validation_set)
    countries = ''.join(country for country, _ in sorted_set)
    capitals = ''.join(capital for _, capital in sorted_set)
    combined = countries + capitals
    hash_value = hashlib.sha256(combined.encode()).hexdigest()
    st.session_state.target_hash = hash_value

def main():
    # Get current parameters
    num_questions, validation_size, _ = get_parameters()
    
    # Generate quiz
    questions, validation_set = generate_quiz(num_questions, validation_size)
    
    # Save quiz data
    save_quiz_data(questions, validation_set)
    
    print(f"Generated {len(questions)} questions with {len(validation_set)} validation pairs")

if __name__ == "__main__":
    main() 