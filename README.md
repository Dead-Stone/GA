# Assignment Grading Assistant

## Overview

The **Assignment Grading Assistant** automates the grading of student submissions using AI-powered models. It provides detailed feedback and summary statistics to enhance the grading process. Built with Python and Streamlit, this tool is designed to save time and improve grading accuracy.

## Features

- **Automated Grading**: Uses AI to evaluate student submissions based on a provided rubric.
- **Detailed Feedback**: Highlights mistakes and areas for improvement for each submission.
- **Summary Statistics**: Displays average scores, passing rates, and other key metrics.
- **File Upload Support**: Accepts ZIP files containing student submissions, along with question papers and optional answer keys.
- **Downloadable Results**: Enables users to download grading results in JSON format.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/assignment-grading-assistant.git
cd assignment-grading-assistant
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and add the following:
```env
GEMINI_API_KEY=your_gemini_api_key
```
Replace `your_gemini_api_key` with your actual Gemini API key.

## Usage

### 1. Run the Application
```bash
streamlit run app_v2.py
```

### 2. Upload Files
- **Submissions ZIP**: Upload a ZIP file containing student submissions in PDF format.
- **Question Paper**: Upload the question paper in PDF format.
- **Answer Key (Optional)**: Upload an answer key in TXT format.
- **Rubric**: Upload a rubric in either TXT or JSON format.

### 3. Start Grading
- Adjust the grading strictness using the slider.
- Click the **Start Grading** button to process submissions.

### 4. View Results
- Results are displayed on the page, including summary statistics and individual feedback.
- Use the **Download Results (JSON)** button to download the results.

## Project Structure

- **`app_v2.py`**: Main Streamlit application.
- **`grading_v2.py`**: Implements the grading logic.
- **`preprocessing_v2.py`**: Handles file extraction and preprocessing.
- **`prompts/`**: Contains templates for AI model prompts.
- **`utils/`**: Utility functions for logging and additional tasks.
- **`requirements.txt`**: Lists project dependencies.
- **`.env`**: Stores environment variables (not included in the repository).

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://ai.google/tools/)
- [Unstructured](https://unstructured.io/)
- [NLTK](https://www.nltk.org/)

## Contact

For questions or issues, open an issue on the GitHub repository or contact the project maintainer at `your.email@example.com`.
