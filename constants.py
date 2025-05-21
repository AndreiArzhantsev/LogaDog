from typing import Tuple

NUM_QUESTIONS = 10
QUESTIONS_PER_GROUP = 3
VALIDATION_SIZE = 5
COST_OF_MISTAKE = 10


def update_parameters(num_questions: int, validation_size: int, questions_per_group: int = None, cost_of_mistake: int = None):
    """Update the parameters"""
    global NUM_QUESTIONS, VALIDATION_SIZE, QUESTIONS_PER_GROUP, COST_OF_MISTAKE
    NUM_QUESTIONS = num_questions
    VALIDATION_SIZE = validation_size
    if questions_per_group is not None:
        QUESTIONS_PER_GROUP = questions_per_group
    if cost_of_mistake is not None:
        COST_OF_MISTAKE = cost_of_mistake

def get_parameters():
    """Get current parameters"""
    return NUM_QUESTIONS, VALIDATION_SIZE, QUESTIONS_PER_GROUP, COST_OF_MISTAKE 