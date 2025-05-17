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
        # Add description
        st.markdown("""
        This is a toy example of a Distributed Data Annotation Protocol (DDAP) implementation. 
        You are a data annotator and you are given a set of random country-capital questions.
    
        ### How it works:
        1. After generating the quiz, you will be given a set of country-capital questions
        2. For each country, you can select multiple capitals that you think might be correct
        3. The system will try to find a subset of your answers that matches a pre-computed hash (see code in Github repo)
        4. If found, this subset serves as a validation set, proving that your answers contain the correct information
        5. Algorithm also returns the last attempted answers for all questions, so you can see how is your time spent on finding hash correlates with quality outside validation set
        
        ### Parameters:
        - **Number of Questions**: Total number of country-capital pairs in the quiz. More questions mean more possible combinations to check.
        - **Validation Set Size**: Number of pairs that need to match the hash. This determines how many correct answers you need to find.
        - **Timeout**: Maximum time (in seconds) the algorithm will spend searching for a valid combination. If exceeded, you'll need to adjust your answers.
        """)
        
        st.write("First, let's generate the quiz tasks...")
        
        # Get current parameters
        num_questions, validation_size, timeout = get_parameters()
        
        # Add parameter inputs
        st.markdown("### Quiz Parameters")
        col1, col2, col3 = st.columns(3)
        with col1:
            num_questions = st.number_input(
                "Number of Questions",
                min_value=1,
                max_value=20,
                value=num_questions,
                help="Number of questions in the quiz"
            )
        with col2:
            validation_size = st.number_input(
                "Validation Set Size",
                min_value=1,
                max_value=10,
                value=validation_size,
                help="Number of questions in the validation set"
            )
        with col3:
            timeout = st.number_input(
                "Timeout (seconds)",
                min_value=5,
                max_value=300,
                value=timeout,
                help="Timeout for the quiz"
            )
        
        if st.button("Generate Tasks"):
            try:
                # Update constants with user parameters
                update_parameters(num_questions, validation_size, timeout)
                
                # Generate quiz with user parameters
                questions, validation_set = generate_quiz(num_questions, validation_size)
                
                # Save quiz data
                save_quiz_data(questions, validation_set)
                
                # Switch to quiz page
                st.session_state.page = 'quiz'
                st.rerun()
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")
    
    elif st.session_state.page == 'quiz':
        # Import quiz interface here to avoid circular imports
        from quiz_generator import show_quiz_interface
        show_quiz_interface()

if __name__ == "__main__":
    main() 