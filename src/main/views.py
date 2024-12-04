import csv
import pandas as pd
import yagmail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .forms import SignUpForm, UpdateUserForm, UpdateUserProfileForm, CustomerRegistrationForm, CustomerLoginForm
from .models import AddRecordForm, Record, UserProfile


def send_email(subject, message, from_email, to_email):
    yag = yagmail.SMTP(from_email, '?emaxafuh23')
    yag.send(to_email, subject, message)

def main_page(request):
    records = Record.objects.all()

    if request.method == 'POST':
        if 'forgot_password' in request.POST:
            password_reset_form = PasswordResetForm(request.POST)
            if password_reset_form.is_valid():
                data = password_reset_form.cleaned_data['email']
                associated_users = User.objects.filter(Q(email=data))
                if associated_users.exists():
                    for user in associated_users:
                        subject = "Password Reset Requested"
                        email_template_name = "password_reset_email.txt"
                        c = {
                            "email": user.email,
                            'domain': '127.0.0.1:8000',  # your domain
                            'site_name': 'Your Site Name',
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "user": user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        email = render_to_string(email_template_name, c)
                        try:
                            send_email(subject, email, 'deepakdube1102@gmail.com', user.email)
                        except Exception as e:
                            return HttpResponse('Invalid header found.')
                        messages.success(request, "Password reset email sent. Check your email.")
                        return redirect('main')

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Successfully Logged In!")
            return redirect('home')  # Redirect to the home page
        else:
             messages.success(request, "There Was An Error Logging In, Please Try Again...")
             return redirect('main')
    else:
        return render(request, "views/main.html", {'records':records})
    
    
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('main')
	

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'user_profile.html', {'user': user})

def logout_users(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('main')

def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})

def customer_record(request, pk):
	if request.user.is_authenticated:
		customer_record = Record.objects.get(id=pk)
		return render(request, 'record.html', {'customer_record':customer_record})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('main')
      
def delete_record(request, pk):
	if request.user.is_authenticated:
		delete_it = Record.objects.get(id=pk)
		delete_it.delete()
		messages.success(request, "Record Deleted Successfully...")
		return redirect('main')
	else:
		messages.success(request, "You Must Be Logged In To Do That...")
		return redirect('main')



def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if 'add_record' in request.POST:
                if form.is_valid():
                    add_record = form.save()
                    messages.success(request, "Record Added...")
                    return redirect('main')
            elif 'import_data' in request.POST:
                try:
                    if 'file' not in request.FILES:
                        raise ValueError("No file was uploaded")
                    
                    file = request.FILES['file']
                    if not file.name.endswith('.csv'):
                        raise ValueError("File is not a CSV")
                    
                    df = pd.read_csv(file)
                    if df.empty:
                        raise ValueError("The CSV file is empty")
                    
                    required_columns = ['First Name', 'Last Name', 'Email', 'Phone Number', 'Address', 'City', 'State', 'Zipcode']
                    if not all(col in df.columns for col in required_columns):
                        raise ValueError("CSV is missing required columns")
                    
                    records = []
                    for index, row in df.iterrows():
                        record = Record(
                            first_name=row['First Name'],
                            last_name=row['Last Name'],
                            email=row['Email'],
                            phone=row['Phone Number'],
                            address=row['Address'],
                            city=row['City'],
                            state=row['State'],
                            zipcode=row['Zipcode']
                        )
                        records.append(record)
                    
                    Record.objects.bulk_create(records)
                    messages.success(request, f"Successfully imported {len(records)} records!")
                    return redirect('main')
                except Exception as e:
                    messages.error(request, f"Error importing data: {str(e)}")
                    return redirect('add_record')
        return render(request, 'add_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('main')

def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		form = AddRecordForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('main')
		return render(request, 'update_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('main')
	
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


def download_all_records(request):
    records = Record.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone Number', 'Zipcode', 'Created At'])
    for record in records:
        writer.writerow([record.id, record.first_name + ' ' + record.last_name, record.email, record.phone, record.zipcode, record.created_at])

    return response

def password_reset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',  # your domain
                        'site_name': 'Your Site Name',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_email(subject, email, 'your_email@example.com', user.email)
                        messages.success(request, "Password reset email sent. Check your email.")
                        return redirect('main')
                    except Exception as e:
                        messages.error(request, "Error sending email: " + str(e))
                        return redirect('main')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})


@login_required
def user_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()

    return render(request, 'user_profile.html', {'user': request.user})

@login_required
def update_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateUserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('user_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateUserProfileForm(instance=profile)

    return render(request, 'update_profile.html', {'user_form': user_form, 'profile_form': profile_form})



#customer tasks


def customer_registration(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'customer_registration.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print("User  authenticated:", user)  # Check if user is not None
            if user is not None:
                login(request, user)
                print("User  logged in:", request.user)  # Check if request.user is set to the correct user
                return redirect('customer_dashboard')
        else:
            print("Form errors:", form.errors)  # Check if there are any errors
    else:
        form = CustomerLoginForm()
    return render(request, 'customer_login.html', {'form': form})

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

def customer_logout(request):
    logout(request)
    return redirect('customer_login')