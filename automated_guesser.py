import numpy as np
from typing import List, Dict, Set, Optional

class AutomatedGuesser:
    def __init__(
            self, 
            num_capitals: List[str], 
            test_countries_ids: List[str], 
            validation_countries_ids: List[str], 
            validation_capitals_ids: List[str]
        ):
        self.test_countries_ids = test_countries_ids
        self.num_test = len(test_countries_ids)
        self.validation_countries_ids = validation_countries_ids
        self.num_validation = len(validation_countries_ids)
        self.num_capitals = num_capitals
        self.guesses = np.ones(self.num_test)*(-1)
        self.answers_ids = validation_capitals_ids
        self.probs = np.ones(self.num_test) / self.num_test
        self.alpha = 0.01
        
    def make_guess(self) -> List[str]:
        """Make a guess based on current probability distributions"""

        question_ids = np.random.choice(
            self.num_test, 
            size=self.num_validation, 
            replace=False,
            p=self.probs
        )
        
        guesses_ids = self.guesses[question_ids]
        s = np.sum(guesses_ids == -1)
        guesses_ids[guesses_ids == -1] = np.random.choice(self.num_capitals, size=s)
        return self.test_countries_ids[question_ids], guesses_ids
    
    def update_after_wrong_guess(self, question_idx: int):
        """Update probabilities after a wrong guess"""
        # Lower probability that this question is in validation set
        guessed_sum = self.p[question_idx].sum()
        self.probs *= (1-guessed_sum+self.alpha*self.num_validation) / (1-guessed_sum)
        self.probs[question_idx] *= (1-guessed_sum) / (1-guessed_sum+self.alpha*self.num_validation)
        self.probs[question_idx] -= self.alpha
        self.probs = np.clip(self.probs, 0, 1)
        return

    
    def update_after_new_info(self, question_idx: int, guess_idx: str):
        """Update probabilities after receiving new information"""
        self.probs *= 0.1 / (1 - min(self.probs[question_idx]), 0.9)
        self.probs[question_idx] = max(0.9, self.probs[question_idx])
        self.guesses[question_idx] = guess_idx
        return
    
    def check_if_correct(self, question_ids: list[int], guesses_ids: list[int]) -> bool:
        # print(question_ids, guesses_ids)
        """Check if all guessed questions are validation questions with correct answers"""
        # print(question_ids)
        # print(guesses_ids)
        # print()
        # print(self.validation_countries_ids)
        # print(self.answers_ids)
        # print()
        # print()
        if np.any(self.validation_countries_ids != question_ids):
            return False
        
        if np.any(self.answers_ids != guesses_ids):
            return False
        
        return True

def test_automated_guesser():
    from capitals_gt import country_capitals as COUNTRY_CAPITALS
    
    num_questions = 4
    num_validation = 2
    all_countries = list(COUNTRY_CAPITALS.keys())
    all_capitals = np.sort(list(COUNTRY_CAPITALS.values()))
    all_capitals_ids = {c: n for n, c in enumerate(all_capitals)}

    test_countries_ids = np.random.choice(np.arange(len(all_countries)), size=num_questions, replace=False)
    validation_countries_ids = np.random.choice(test_countries_ids, size=num_validation, replace=False)
    validation_answers_ids = np.array([all_capitals_ids[COUNTRY_CAPITALS[all_countries[i]]] for i in validation_countries_ids])

    guesser = AutomatedGuesser(
        len(all_capitals), 
        test_countries_ids, 
        validation_countries_ids,
        validation_answers_ids
    )
    
    max_guesses = 1000000
    guess_count = 0
    question_idx, guess_idx = validation_countries_ids[0], validation_answers_ids[0]
    guesser.update_after_new_info(question_idx, guess_idx)
    while guess_count < max_guesses:
        question_ids, answers_ids = guesser.make_guess()
        guess_count += 1
        
        if guesser.check_if_correct(question_ids, answers_ids):
            print(f"Found correct validation set after {guess_count} guesses!")
            break
        

    
    if guess_count == max_guesses:
        print(f"Did not find correct validation set after {max_guesses} guesses")

if __name__ == "__main__":
    test_automated_guesser() 