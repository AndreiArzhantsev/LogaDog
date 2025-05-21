import pandas as pd
import numpy as np
import random
import hashlib
import itertools
from typing import List, Tuple, Dict
from constants import get_parameters
from capitals_gt import country_capitals as COUNTRY_CAPITALS
import streamlit as st


N = 100

def generate_quiz(
        num_questions: int = None, 
        validation_size: int = None, 
        questions_per_group: int = None
    ) -> Tuple[List[Dict], List[Tuple[str, str]]]:
    """Generate a quiz with the specified number of question groups and validation set size"""
    current_num_questions, current_validation_size, current_questions_per_group, _ = get_parameters()
    num_questions = num_questions or current_num_questions
    validation_size = validation_size or current_validation_size
    questions_per_group = questions_per_group or current_questions_per_group
    
    # Randomly select countries for each group
    all_countries = list(COUNTRY_CAPITALS.keys())
    questions = []
    allgroup_countries = random.sample(all_countries, questions_per_group*num_questions)
    for group_idx in range(num_questions):
        group_countries = allgroup_countries[
            group_idx*questions_per_group : (group_idx+1)*questions_per_group
        ]
        
        group_questions = []
        for country in group_countries:
            correct = COUNTRY_CAPITALS[country]
            wrong_answers = random.sample([c for c in COUNTRY_CAPITALS.values() if c != correct], 3)
            options = wrong_answers + [correct]
            random.shuffle(options)
            group_questions.append({
                'country': country,
                'capitals': options,
                'group': group_idx + 1
            })
        questions.extend(group_questions)
    
    # Generate validation set
    validation_set = generate_validation_set(questions, validation_size, questions_per_group)
    
    return questions, validation_set

def generate_validation_set(questions: List[Dict], validation_size: int, questions_per_group: int) -> List[Tuple[str, str]]:
    """Generate validation set from questions, ensuring we take complete groups"""
    # Group questions by their group number
    grouped_questions = {}
    for q in questions:
        group = q['group']
        if group not in grouped_questions:
            grouped_questions[group] = []
        grouped_questions[group].append(q)
    
    # Randomly select validation groups
    validation_groups = random.sample(list(grouped_questions.keys()), validation_size)
    
    # For each validation group, use the correct capital for each country
    validation_set = []
    for group in validation_groups:
        for q in grouped_questions[group]:
            country = q['country']
            capital = COUNTRY_CAPITALS[country]
            validation_set.append((country, capital))
    print(validation_set)
    return validation_set

def save_quiz_data(questions: List[Dict], validation_set: List[Tuple[str, str]]):
    """Save quiz data to session state"""
    # Convert questions to DataFrame format
    tasks_data = []
    for q in questions:
        tasks_data.append({
            'country': q['country'],
            'capitals': '|'.join(q['capitals']),
            'group': q['group']
        })
    
    # Store in session state
    st.session_state.tasks_df = pd.DataFrame(tasks_data)
    
    # Calculate and store validation hash
    countries = ''.join(country for country, _ in validation_set)
    capitals = ''.join(capital for _, capital in validation_set)
    combined = countries + capitals
    
    # Add random cost to the hash
    _, _, _,  cost_of_mistake = get_parameters()
    cost = str(random.randint(0, cost_of_mistake))
    combined = combined + cost
    print(combined)
    hash_value = hashlib.sha256(combined.encode()).hexdigest()
    st.session_state.target_hash = hash_value
    st.session_state.cost = cost  # Store the cost for verification

def main():
    # Get current parameters
    num_questions, validation_size, _, questions_per_group = get_parameters()
    
    # Generate quiz
    questions, validation_set = generate_quiz(num_questions, validation_size, questions_per_group)
    
    # Save quiz data
    save_quiz_data(questions, validation_set)
    
    print(f"Generated {len(questions)} questions in {num_questions} groups with {len(validation_set)} validation pairs")

if __name__ == "__main__":
    main() 