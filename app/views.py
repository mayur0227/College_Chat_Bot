from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.verify import authentication, form_varification
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import *
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .modify import *
import speech_recognition as sr
import re
from django.utils.safestring import mark_safe

# Create your views here.
def index(request):    
    return render(request, "index.html")

def voice(request):
    current_user = request.user    
    context = {
        'fname': current_user.first_name,
    }

    return render(request, "voice.html",context)

def log_in(request):
    if request.method == "POST":
        # return HttpResponse("This is Home page")  
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            request.session.pop('conversation', None)
            messages.success(request, "Log In Successful...!")
            return redirect("chat_without_username")
        else:
            messages.error(request, "Invalid User...!")
            return redirect("log_in")
    # return HttpResponse("This is Home page")    
    return render(request, "log_in.html")

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        # print(fname, contact_no, ussername)
        verify = authentication(fname, lname, password, password1)
        if verify == "success":
            user = User.objects.create_user(username, password, password1)          #create_user
            user.first_name = fname
            user.last_name = lname
            user.save()
            messages.success(request, "Your Account has been Created.")
            return redirect("/")
            
        else:
            messages.error(request, verify)
            return redirect("register")
    # return HttpResponse("This is Home page")    
    return render(request, "register.html")

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def log_out(request):
    ChatMessage.objects.filter(sender=request.user).delete()
    logout(request)
    messages.success(request, "Log out Successfuly...!")
    return redirect("/")


@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def dashboard(request):
    context = {
        'fname': request.user.first_name, 
        }
   
        
    return render(request, "dashboard.html",context)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.db.models import Q
import joblib
import os
import pandas as pd
import speech_recognition as sr
import re
from fuzzywuzzy import fuzz, process

# Load AI Model and Dataset
MODEL_PATH = os.path.join('dataset/chat_model.pkl')
DATASET_PATH = os.path.join('dataset/avcoe.csv')

try:
    chat_model = joblib.load(MODEL_PATH)
    dataset = pd.read_csv(DATASET_PATH)
    valid_questions = dataset['Questions'].str.strip().str.lower().tolist()
except Exception as e:
    chat_model = None
    valid_questions = []

def find_best_match(query, valid_questions):
    best_match = process.extractOne(query, valid_questions, scorer=fuzz.partial_ratio)
    return best_match[0] if best_match and best_match[1] >= 70 else None

def generate_ai_response(message):
    if chat_model:
        try:
            return chat_model.predict([message])[0]
        except Exception:
            return "Sorry, I encountered an error processing your request."
    return "AI model not loaded."

@login_required(login_url="log_in")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def chat(request):
    current_user = request.user
    conversation = ChatMessage.objects.filter(sender=current_user).order_by('sendtime')

    return render(request, "chat.html", {'conversation': conversation, 'current_user': current_user})

@login_required(login_url="log_in")
def send_message(request):
    if request.method == 'POST':
        current_user = request.user
        user_input = request.POST.get('message', '').strip().lower()

        # Ensure chatbot user exists
        receiver, created = User.objects.get_or_create(username="chatbot")

        # Create user message
        ChatMessage.objects.create(sender=current_user, receiver=receiver, message=user_input)

        # Generate AI response
        predicted_response = generate_ai_response(user_input)

        # Save AI response
        ChatMessage.objects.create(sender=receiver, receiver=current_user, message=predicted_response)

        return JsonResponse({'message': predicted_response})

    return JsonResponse({'message': "Invalid request"})



def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()


@login_required(login_url="log_in")
def record_and_transcribe(request):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized Speech: {text}")  # Debugging
        cleaned_text = clean_text(text)
        
        # Find best matching question
        matched_question = find_best_match(cleaned_text, valid_questions)
        
        if matched_question:
            ai_response = generate_ai_response(matched_question)
            return JsonResponse({'transcribed_text': cleaned_text, 'matched_question': matched_question, 'response': ai_response})
        else:
            return JsonResponse({'transcribed_text': cleaned_text, 'response': "Sorry, I couldn't find a relevant answer."})

    except sr.UnknownValueError:
        return JsonResponse({'error': "Could not understand the audio"})
    except sr.RequestError as e:
        return JsonResponse({'error': f"Speech API error: {e}"})


def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            messages.success(request, "Password Changed Successfully")
            return redirect("log_in")
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("forgot_password")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return redirect("forgot_password")
    return render(request, "forgot_password.html")