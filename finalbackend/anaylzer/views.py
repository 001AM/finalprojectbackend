import os
import easyocr
import numpy as np
import spacy
from pdf2image import convert_from_path
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Resume
from .serializers import ResumeSerializer,MockInterviewSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from PIL import Image
import google.generativeai as genai
from .models import MockInterview
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')  
class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the file is present in the request
        if request.POST.get('nottranscript',False) == 'true':
            if 'resume' not in request.FILES:
                return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Combine data and files for serializer
            data = {
                'file': request.FILES['resume'],
            }
            serializer = ResumeSerializer(data=data)
            if serializer.is_valid():
                print("========")
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

            # Process the extracted text with spaCy
        else:
            full_text = request.POST.get('transcript')
        print(full_text,"====hhhh")

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(full_text)

        # Extract keywords (nouns and proper nouns)
        keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]

        # print("Extracted Keywords: ", keywords)
        role = request.POST.get('role')
        questions = GeminiApi(
            prompt = f"{keywords} select the value in array and generate ten question based on that for technical and behvioural question for the {role}"
    
        )
        question_texts = questions.generate_questions()
        print(question_texts)
        questions_list = []
        for question_text in question_texts:
            if question_text.strip():
                print(question_text,'=========================i')
                if any(chr.isdigit() for chr in question_text):
                    parts = question_text.split('\n')
                    # parts = ''.join([i for i in parts if not i.replace('.','').isdigit()])
                    print(parts,"===o")
                    # question = parts[0].strip()
                    questions_list.append({'question': parts})
        interviewcount = MockInterview.objects.filter(user=request.user).count()
        name = f"MockInterview {interviewcount + 1}"
        MockInterview.objects.create(user=request.user,questions=questions_list,role=role,name = name)
        return JsonResponse({"keywords": questions_list}, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')  
class MockInterviewData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            mockinterview_data = MockInterview.objects.filter(user=request.user).values()        
            serailizer_data = MockInterviewSerializer(mockinterview_data,many=True)
            return JsonResponse({"mockinterview_data":serailizer_data.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GeminiApi:
    def __init__(self, **kwargs):
        self.prompt = kwargs.get('prompt')
    
    def configure_genai(self):
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

    def generate_questions(self,**kwargs):
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

        response = model.generate_content(self.prompt)

        response_text = response.text.strip().split('\n')
        print(response_text)
        

        return response_text
