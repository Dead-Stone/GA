import os
import logging
from pathlib import Path
import shutil
import zipfile
import base64
from typing import Dict, Any, List
from PIL import Image
import io
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import NarrativeText, Image as UnstructuredImage
import google.generativeai as genai
from prompts.answer_key_prompt import get_answer_key_prompt
from prompts.image_prompt import get_image_description_prompt

import nltk
print(nltk.data.path)
# Set Tesseract path
os.environ["TESSDATA_PREFIX"] = "C:\Program Files\Tesseract-OCR\tessdata"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FilePreprocessor:
    def __init__(self, temp_dir: str = "temp_uploads"):
        self.temp_dir = Path(temp_dir)
        self.extracted_dir = self.temp_dir / "extracted"
        self.logger = logger
        self._setup_directories()

    def process_files(self, submissions_zip: str, question_paper: str, answer_key_PATH: str = None, rubric: Dict[str, Any] = None):
        try:
            # print("Processing files...")
            zip_path = Path(submissions_zip)
            # print(f"Extracting submissions from {zip_path}")
            submissions = self._extract_submissions(zip_path)
            # print(f"Extracted {len(submissions)} submissions")
            question_text = self._process_pdf_with_unstructured(question_paper)
            # print("Question paper processed")
            answer_key_text = None
            if answer_key_PATH:
                print(f"Processing answer key: {answer_key_PATH}")
                answer_key_text = self._process_pdf_with_unstructured(answer_key_PATH)
            else:
                print("Generating answer key using Gemini 1.5 Flash")
                answer_key_text = self._generate_answer_key(question_text, rubric)
            print("Files processed successfully")
            return {
                "submissions": submissions,
                "question": question_text,
                "answer_key": answer_key_text
            }
        finally:
            print("Cleanup complete")

    def _process_pdf_with_unstructured(self, pdf_path: str) -> str:
        try:
            elements = partition_pdf(pdf_path, extract_images_in_pdf=True)
            text = ""
            print(f"Processing PDF: {pdf_path}")
            print(f"Extracted {len(elements)} elements")
            for element in elements:
                if isinstance(element, NarrativeText):
                    text += element.text + "\n"
                elif isinstance(element, UnstructuredImage):
                    image_path = f"{pdf_path}_image_{id(element)}.png"
                    element.save_image(image_path)
                    image_desc = self._process_image(image_path)
                    text += f"\n[Image: {image_desc}]\n"
                    os.remove(image_path)
            print(f"Processed PDF: {pdf_path}")
            # print(f"Text: {text.strip()}")
            return text.strip()
        except Exception as e:
            print(f"PDF processing failed: {e}")
            raise

    def _process_image(self, image_path: str) -> str:
        try:
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = get_image_description_prompt()
            response = model.generate_content([prompt, img_data])
            print(f"Image processed: {response.text.strip()}")
            return response.text.strip()
        except Exception as e:
            print(f"Image processing failed: {e}")
            return ""

    def _generate_answer_key(self, question_text: str, rubric: Dict[str, Any]) -> str:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = get_answer_key_prompt(question_text, rubric)
            # print(f"Answer key prompt: {prompt}")
            response = model.generate_content(prompt)
            # print(f"Answer key generated: {response.text.strip()}")
            return response.text.strip()
        except Exception as e:
            print(f"Answer key generation failed: {e}")
            return ""

    def _setup_directories(self):
        self.temp_dir.mkdir(exist_ok=True)
        self.extracted_dir.mkdir(exist_ok=True)

    def _save_uploaded_file(self, uploaded_file, filename: str) -> Path:
        save_path = self.temp_dir / filename
        with open(save_path, 'wb') as f:
            shutil.copyfileobj(uploaded_file, f)
        return save_path

    def _extract_submissions(self, zip_path: Path) -> Dict[str, str]:
        submissions = {}
        print(f"Extracting ZIP file: {zip_path}")
        try:
            shutil.unpack_archive(str(zip_path), str(self.extracted_dir))
            print(f"ZIP file extracted to {self.extracted_dir}")
        except Exception as e:
            print(f"Failed to extract ZIP file: {e}")
            return submissions
        print('Extracted files:', list(self.extracted_dir.glob('*\\*.pdf')))
        for pdf_file in self.extracted_dir.glob('*\\*.pdf'):
            try:
                print(f"Processing 123 {pdf_file}")
                student_name = pdf_file.stem
                print(f"Student Name: {student_name}")
                text = self._process_pdf_with_unstructured(str(pdf_file))
                print(f"Extracted textttttttttttttttttttttttttttttttttt: {text.strip()}")
                if text.strip():  # Ensure non-empty content
                    submissions[student_name] = text
                else:
                    print(f"Empty content for {pdf_file}. Skipping.")
            except Exception as e:
                print(f"Failed to process {pdf_file}: {e}")
        
        print(f"Extracted submissions: {len(submissions)} files processed successfully.")
        return submissions

    def cleanup(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Cleanup failed: {e}")
