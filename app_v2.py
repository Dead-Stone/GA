import streamlit as st
import os
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from grading_v2 import GradingService
from preprocessing_v2 import FilePreprocessor
from utils.logging_utils import setup_logging, StreamlitHandler
import google.generativeai as genai
from prompts.image_prompt import get_image_description_prompt
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Set Tesseract path
os.environ["TESSDATA_PREFIX"] = "C:\\Program Files\\Tesseract-OCR\\tessdata"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "grading_results")
RUBRIC_FILE_PATH = os.path.join(BASE_DIR, "rubric.json")
os.makedirs(RESULTS_DIR, exist_ok=True)

# UI Configuration
st.set_page_config(page_title="Assignment Grading Assistant", page_icon="📚")

# Initialize Session State
if 'grading_complete' not in st.session_state:
    st.session_state.grading_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Setup Logging
logger = setup_logging()
streamlit_handler = StreamlitHandler(st.session_state.logs)
logger.addHandler(streamlit_handler)

class FileHandler:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.temp_dir = self.base_dir / "uploads"
        
    def setup(self):
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def save_file(self, uploaded_file, filename: str) -> Path:
        if not uploaded_file:
            return None
        file_path = self.temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(uploaded_file, f)
        return file_path
    
    def cleanup(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def display_results(results: dict):
    """Display grading results"""
    st.header("Grading Results")
    
    if not results or "student_results" not in results:
        st.warning("No results to display")
        return

    # Summary Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Submissions", results["summary_stats"]["submission_count"])
    with col2:
        st.metric("Average Score", f"{results['summary_stats']['average_score']:.2f}%")
    with col3:
        st.metric("Passing Students", results["summary_stats"]["passing_count"])

    # Detailed Results
    st.subheader("Individual Results")
    for student, result in results["student_results"].items():
        with st.expander(f"📝 {student} - Score: {result['score']}%"):
            st.write("**Feedback:**")
            st.write(result["grading_feedback"])
            if result.get("mistakes"):
                st.write("**Deductions:**")
                for section, details in result["mistakes"].items():
                    st.write(f"- {section}: -{details['deductions']} points")
                    st.write(f"  • {details['reasons']}")


def get_rubric_from_text(rubric_text: str) -> dict:
    """
    Generate a grading rubric from the given text using Gemini API.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "You are an expert in educational assessment. "
            "Generate a detailed grading rubric in JSON format from the following text. "
            "Ensure the JSON includes sections, criteria, and points for each criterion. "
            "The JSON should be structured with 'total_points', 'sections', and each section should have 'max_points' and 'criteria'. "
            "Each criterion should have 'name', 'points', and 'description'.\n\n"
            f"{rubric_text}"
        )
        response = model.generate_content(prompt)
        # logger.info(f"Rubric generation response: {response.text}")
        # Extract JSON from the response text
        start_index = response.text.find('{')
        end_index = response.text.rfind('}') + 1
        json_text = response.text[start_index:end_index]
        return json.loads(json_text)
    except Exception as e:
        logging.error(f"Error generating rubric from text: {e}")
        raise

def main():
    st.title("Assignment Grading Assistant")
    st.write("Upload student submissions and grading materials to begin grading.")
    

    
    # File Upload Form
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        with col1:
            submissions_zip = st.file_uploader(
                "Upload Submissions (ZIP)", 
                type="zip",
                help="ZIP file containing student submissions"
            )
            question_paper = st.file_uploader(
                "Upload Question Paper (PDF)", 
                type="pdf"
            )
        with col2:
            answer_key = st.file_uploader(
                "Upload Answer Key (Optional)", 
                type="txt"
            )
            strictness = st.slider(
                "Grading Strictness", 
                min_value=1, 
                max_value=5, 
                value=1
            )
        rubric_option = st.radio(
            "Rubric Option",
            ("Upload Rubric Text", "Upload Rubric JSON")
        )
        rubric_file = st.file_uploader(
            "Upload Rubric",
            type=["txt", "json"]
        )
        submit = st.form_submit_button("Start Grading")

    if submit:
        if not submissions_zip or not question_paper:
            st.error("Please upload required files")
            return

        file_handler = FileHandler(BASE_DIR)
        try:
            with st.spinner("Processing submissions and grading..."):
                # Setup and save files
                file_handler.setup()
                submissions_path = file_handler.save_file(submissions_zip, "submissions.zip")
                question_path = file_handler.save_file(question_paper, "question.pdf")
                answer_path = file_handler.save_file(answer_key, "answer.txt") if answer_key else None

                # Process rubric
                rubric = None
                if rubric_file:
                    rubric_path = file_handler.save_file(rubric_file, "rubric.txt" if rubric_option == "Upload Rubric Text" else "rubric.json")
                    if rubric_option == "Upload Rubric Text":
                        with open(rubric_path, 'r') as f:
                            rubric_text = f.read()
                        rubric = get_rubric_from_text(rubric_text)
                    else:
                        with open(rubric_path, 'r') as f:
                            rubric = json.load(f)
                
                # Save rubric to rubric.json
                with open(RUBRIC_FILE_PATH, 'w') as f:
                    json.dump(rubric, f, indent=2)
                logger.info(f"Rubric saved to {RUBRIC_FILE_PATH}")

                # Process files
                preprocessor = FilePreprocessor()
                # logger.info("Processing files: %s, %s, %s", str(submissions_path), str(question_path), str(answer_path))
                processed_files = preprocessor.process_files(
                    str(submissions_path),
                    str(question_path),
                    str(answer_path) if answer_path else None,
                    rubric
                )
                logger.info("Files processed successfully")
                logger.info(f"Processed files: {processed_files['submissions']}")
                # logger.info(processed_files)
                
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    logger.error("No API_KEY found. Please set the GEMINI_API_KEY environment variable.")
                    raise ValueError("No API_KEY found. Please set the GEMINI_API_KEY environment variable.")
                print(api_key,"api_key")
                grading_service = GradingService(api_key=api_key)
                logger.info("Grading submissions with rubric: %s", rubric["total_points"])
                results = grading_service.batch_grade(
                    processed_files["submissions"],
                    processed_files["answer_key"],
                    rubric
                )
                logger.info("Grading completed successfully with results: %s", results)
                logger.info(f"Results: {results}")
                
                # Generate summary
                summary = grading_service.generate_summary(results)
                logger.info(f"Grading summary: {summary}")
                # Save summary and results to file
                result_path = Path(RESULTS_DIR) / "grading_results.json"
                with open(result_path, 'w') as f:
                    json.dump(summary, f, indent=2)
                logger.info(f"Results saved to {result_path}")

                # Store results
                if results:
                    st.session_state.results = summary
                    st.session_state.grading_complete = True
                    
                    st.success("Grading completed successfully!")

        except Exception as e:
            logger.error(f"Error during grading: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
        finally:
            # file_handler.cleanup()
            pass

    # Display Results if Available
    if st.session_state.grading_complete and st.session_state.results:
        display_results(st.session_state.results)
        
        # Download Results Button
        if st.download_button(
            "Download Results (JSON)",
            data=json.dumps(st.session_state.results, indent=2),
            file_name=f"grading_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        ):
            st.success("Results downloaded successfully!")

if __name__ == "__main__":
    main()