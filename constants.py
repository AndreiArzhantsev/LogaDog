from typing import Tuple

# Default values
NUM_QUESTIONS = 10
VALIDATION_SIZE = 5
TIMEOUT = 30

# Current values (can be updated)
_current_num_questions = NUM_QUESTIONS
_current_validation_size = VALIDATION_SIZE
_current_timeout = TIMEOUT

def update_parameters(num_questions: int = None, validation_size: int = None, timeout: int = None):
    """Update the current parameters"""
    global _current_num_questions, _current_validation_size, _current_timeout
    if num_questions is not None:
        _current_num_questions = num_questions
    if validation_size is not None:
        _current_validation_size = validation_size
    if timeout is not None:
        _current_timeout = timeout

def get_parameters():
    """Get the current parameters"""
    return _current_num_questions, _current_validation_size, _current_timeout 