import os
import easyocr
import numpy as np
import spacy
from pdf2image import convert_from_path
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Resume
from .serializers import ResumeSerializer
from rest_framework.permissions import AllowAny
from PIL import Image
import google.generativeai as genai
class ResumeUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResumeSerializer(data=request.FILES)
        if serializer.is_valid():
            resume = serializer.save()

            # Get the path of the saved resume (PDF)
            resume_path = os.path.join(settings.MEDIA_ROOT, resume.file.name)

            # Convert PDF to images
            images = convert_from_path(resume_path)

            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'])

            extracted_text = []

            # Loop through images and perform OCR
            for image in images:
                # Convert PIL image to NumPy array
                image_np = np.array(image)

                # Perform OCR on the NumPy array
                result = reader.readtext(image_np, detail=0)
                extracted_text.extend(result)

            # Join the text from all pages
            full_text = " ".join(extracted_text)

            # Load spaCy model for NLP processing
            nlp = spacy.load("en_core_web_sm")

            # Process the extracted text with spaCy
            doc = nlp(full_text)

            # Extract keywords (nouns and proper nouns)
            keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]

            # print("Extracted Keywords: ", keywords)
            questions = generate_questions(keywords)
            print(questions)
            return Response({"keywords": questions}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def configure_genai():
    genai.configure(api_key="AIzaSyBvMtbKwkTOo3N7Z934TRCCXZL2dSnF5cw")
    return genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config={
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 100,
        }
    )

def generate_questions(interest):
    genai.configure(api_key="AIzaSyBvMtbKwkTOo3N7Z934TRCCXZL2dSnF5cw")

    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 1000,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config=generation_config
    )

    prompt = f"{interest} select the value in array and generate ten question based on that for technical and behvioural question for the software developement position"
    response = model.generate_content(prompt)
    questions = []

    question_texts = response.text.strip().split('\n')
    print(question_texts)
    for question_text in question_texts:
        if question_text.strip():
            print(question_text,'=========================i')
            if any(chr.isdigit() for chr in question_text):

                parts = question_text.split('\n')
                # parts = ''.join([i for i in parts if not i.replace('.','').isdigit()])
                print(parts,"===o")
                # question = parts[0].strip()
                questions.append({'question': parts})

    return questions
