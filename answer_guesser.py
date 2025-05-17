import pandas as pd
import hashlib
from typing import List, Tuple, Set, Dict, Optional
import itertools
from collections import defaultdict
from constants import get_parameters
import time
import streamlit as st

def load_answers() -> pd.DataFrame:
    """Load answers from session state"""
    if 'answers_df' not in st.session_state:
        return pd.DataFrame()
    return st.session_state.answers_df

def load_target_hash() -> str:
    """Load target hash from session state"""
    if 'target_hash' not in st.session_state:
        raise ValueError("Target hash not found in session state")
    return st.session_state.target_hash

def get_country_variants(df: pd.DataFrame) -> List[Tuple[str, List[str]]]:
    """Get list of (country, capitals) tuples sorted by number of capitals"""
    country_variants = []
    for _, row in df.iterrows():
        capitals = row['capitals'].split('|')
        country_variants.append((row['country'], capitals))
    
    # Sort by number of variants (capitals) in increasing order
    return sorted(country_variants, key=lambda x: len(x[1]))

def generate_combinations(n: int, k: int, variants: List[Tuple[str, List[str]]]):
    if k == 0:
        yield [], []
        return
    for i in range(k-1, n):
        country, capitals = variants[i]
        for prev_countries, prev_capitals in generate_combinations(i, k-1, variants):
            yield prev_countries + [country], prev_capitals + [capitals]

def find_validation_set() -> Tuple[Optional[List[Tuple[str, str]]], Dict[str, Optional[str]]]:
    """Find validation set that matches target hash and return last attempted answers for all questions"""
    # Load data
    answers_df = load_answers()
    if answers_df.empty:
        return [], {}
    
    target_hash = load_target_hash()
    
    # Get current parameters
    _, validation_size, timeout = get_parameters()
    country_variants = get_country_variants(answers_df)
    n_countries = len(country_variants)
    
    # Initialize last_attempts with None for all countries
    last_attempts: Dict[str, Optional[str]] = {row['country']: None for _, row in answers_df.iterrows()}
    
    try:
        start_time = time.time()
        for countries, capitals_lists in generate_combinations(n_countries, validation_size, country_variants):
            if time.time() - start_time > timeout:
                return ['timeout'], last_attempts
                
            for capital_combination in itertools.product(*capitals_lists):
                # Store the last attempted answer for each country
                for country, capital in zip(countries, capital_combination):
                    last_attempts[country] = capital
                
                # Try all possible permutations of the country-capital pairs
                pairs = list(zip(countries, capital_combination))
                for perm in itertools.permutations(pairs):
                    # First concatenate all countries, then all capitals
                    perm_countries, perm_capitals = zip(*perm)
                    combined = ''.join(perm_countries) + ''.join(perm_capitals)
                    current_hash = hashlib.sha256(combined.encode()).hexdigest()
                    
                    if current_hash == target_hash:
                        return list(perm), last_attempts
        
        return [], last_attempts
    except Exception as e:
        print(f"Error: {e}")
        return [], last_attempts

if __name__ == "__main__":
    try:
        validation_set, last_attempts = find_validation_set()
        if validation_set is None:
            print("Algorithm was unable to find an answer in a minute. Try to lower the range of your answers")
            print("\nLast attempted answers:")
            for country, capital in last_attempts.items():
                print(f"{country}\t{capital}")
        elif validation_set:
            print("Found validation set:")
            for country, capital in validation_set:
                print(f"{country}\t{capital}")
            print("\nLast attempted answers for other questions:")
            for country, capital in last_attempts.items():
                if country not in [c for c, _ in validation_set]:
                    print(f"{country}\t{capital}")
        else:
            print("No matching validation set found!")
            print("\nLast attempted answers:")
            for country, capital in last_attempts.items():
                print(f"{country}\t{capital}")
    except Exception as e:
        print(f"Error: {e}") 