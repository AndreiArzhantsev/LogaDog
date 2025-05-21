import pandas as pd
import itertools
import math
import hashlib
import streamlit as st
import random
from collections import defaultdict
from constants import get_parameters
from typing import List, Tuple, Optional, Dict

class AllCombinationsIterator:
    def __init__(
        self,
        initial_data: List[List[Tuple[str, List[str]]]],
        k: int,
        target_hash: str,
        cost_of_mistake: int,
    ):
        self.initial_data = initial_data
        self.k = k
        self.n = len(initial_data)
        self.target_hash = target_hash
        self.cost_of_mistake = cost_of_mistake

        self.initial_lengths = [
            [len(options) for _, options in task]
            for task in self.initial_data
        ]

        self.index_subsets = sorted(
            itertools.combinations(range(self.n), k),
            key=self._combo_size
        )

        self.subset_idx = 0
        self.perms = []
        self.perm_idx = 0
        self.bases = []
        self.choice_idx = []
        self.finished = False
        self._init_subset(0) if self.index_subsets else self._finish()

    def _combo_size(self, indices):
        return math.prod(
            length
            for i in indices
            for length in self.initial_lengths[i]
        )

    def _init_subset(self, subset_idx):
        self.subset_indices = list(self.index_subsets[subset_idx])
        self.perms = list(itertools.permutations(range(self.k)))
        self.perm_idx = 0
        self._init_perm(0)

    def _init_perm(self, perm_idx):
        self.perm = self.perms[perm_idx]
        self.bases = list(itertools.chain.from_iterable(
            self.initial_lengths[self.subset_indices[i]] for i in self.perm
        ))
        self.choice_idx = [0] * len(self.bases)

    def _finish(self):
        self.finished = True
        self.choice_idx = []

    def __iter__(self):
        return self

    def __next__(self):
        while not self.finished:
            flat_data = itertools.chain.from_iterable(
                self.initial_data[self.subset_indices[i]] for i in self.perm
            )
            keys = []
            values = []
            for (key, options), idx in zip(flat_data, self.choice_idx):
                keys.append(key)
                values.append(options[idx])

            combined = ''.join(keys) + ''.join(values)
            for cost in range(self.cost_of_mistake + 1):
                test_combined = combined + str(cost)
                current_hash = hashlib.sha256(test_combined.encode()).hexdigest()
                if current_hash == self.target_hash:
                    outside_values = []
                    chosen_keys = set(keys)
                    for group in self.initial_data:
                        for key, options in group:
                            if key not in chosen_keys:
                                outside_values.append((key, random.choice(options)))

                    return list(zip(keys, values)), outside_values, cost

            self._advance()

        return [], [], 0

    def _advance(self):
        i = len(self.choice_idx) - 1
        while i >= 0:
            self.choice_idx[i] += 1
            if self.choice_idx[i] < self.bases[i]:
                return
            self.choice_idx[i] = 0
            i -= 1

        self.perm_idx += 1
        if self.perm_idx < len(self.perms):
            self._init_perm(self.perm_idx)
        else:
            self.subset_idx += 1
            if self.subset_idx < len(self.index_subsets):
                self._init_subset(self.subset_idx)
            else:
                self._finish()


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


def get_group_variants(df: pd.DataFrame) -> List[List[Tuple[str, List[str]]]]:
    """Get list of groups, each is a list of (country, capitals) tuples."""
    grouped_questions = defaultdict(list)

    for _, row in df.iterrows():
        group = row['group']
        capitals = row['capitals'].split('|')
        grouped_questions[group].append((row['country'], capitals))

    return list(grouped_questions.values())

def sum_over_k_subsets(
    A: List[List[Tuple[str, List[str]]]], 
    k: int
) -> int:
    total = 0
    for subset in itertools.combinations(A, k):
        product = 1
        for task in subset:
            for _, vals in task:
                product *= (len(vals)if len(vals) > 0 else 4)
        total += product
    return total

def count_complexity() -> int:
    """Count complexity of the answers"""
    answers_df = load_answers()
    group_variants = get_group_variants(answers_df)
    _, validation_size, _, cost_of_mistake = get_parameters()
    return sum_over_k_subsets(group_variants, validation_size) * (cost_of_mistake + 1) * math.factorial(validation_size) // 2

def find_validation_set() -> Tuple[Optional[List[Tuple[str, str]]], Dict[str, Optional[str]]]:
    """Find validation set that matches target hash and return last attempted answers for all questions"""
    answers_df = load_answers()
    group_variants = get_group_variants(answers_df)
    target_hash = load_target_hash()
    _, validation_size, _, cost_of_mistake = get_parameters()

    combinator = AllCombinationsIterator(
        group_variants, 
        validation_size, 
        target_hash, 
        cost_of_mistake
    )
    return next(combinator)

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