import streamlit as st
import pandas as pd
from task_generator import generate_quiz, save_quiz_data
from constants import get_parameters, update_parameters

def main():
    st.title("Country-Capital Annotation using DDAP")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'task_generation'
    
    if st.session_state.page == 'task_generation':
        
        num_questions, validation_size, questions_per_group, cost_of_mistake = get_parameters()
        
        # Add parameter inputs
        st.markdown("### Quiz Parameters")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            questions_per_group = st.number_input(
                "Questions per Group",
                min_value=1,
                max_value=5,
                value=questions_per_group,
                help="Number of questions in each group"
            )
        with col2:
            num_questions = st.number_input(
                "Number of Groups",
                min_value=1,
                max_value=20,
                value=num_questions,
                help="Number of question groups in the quiz"
            )
        with col3:
            validation_size = st.number_input(
                "Number of Validation Groups",
                min_value=1,
                max_value=10,
                value=validation_size,
                help="Number of groups in the validation set"
            )
        with col4:
            cost_of_mistake = st.number_input(
                "Cost of Mistake",
                min_value=0,
                max_value=100,
                value=cost_of_mistake,
                help="Maximum cost value for hash verification"
            )
        
        if st.button("Generate Tasks"):
                # Update constants with user parameters
                update_parameters(num_questions, validation_size, questions_per_group, cost_of_mistake)
                
                # Generate quiz with user parameters
                questions, validation_set = generate_quiz(num_questions, validation_size, questions_per_group)
                
                # Save quiz data
                save_quiz_data(questions, validation_set)
                
                # Switch to quiz page
                st.session_state.page = 'quiz'
                st.rerun()
    
    elif st.session_state.page == 'quiz':
        # Import quiz interface here to avoid circular imports
        from quiz_generator import show_quiz_interface
        show_quiz_interface()

if __name__ == "__main__":
    main() 