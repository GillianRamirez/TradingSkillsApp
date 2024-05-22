from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.forms import UserCreationForm
from App2.forms import ContactForm
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request, "home.html", {})

#Contact Page.

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

        EmailMessage(
            'Contact Form Submission from {}'.format(name),
            message,
            'form-response@example.com', # Send from (your website)
            ['gillianramirez0@gmail.com'], # Send to (your admin email)
            [],
            reply_to=[email] # Email from the form to get back to
        ).send()

        return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def success(request):
   return render(request, 'success.html')


#Registration
def signup(request):
    return render(request, "signup.html")

def login(request):
    return render(request, "login.html")

def authView(request):
    if request.method=="POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
    else:        
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form" :form})