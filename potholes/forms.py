from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
import io
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Pothole, UserProfile


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class UserLoginForm(forms.Form):
    """User login form."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class PotholeReportForm(forms.ModelForm):
    """Form for reporting a pothole."""
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Pothole
        fields = ('image', 'description', 'severity', 'latitude', 'longitude')
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the pothole...'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_image(self):
        image_file = self.cleaned_data.get('image')
        if not image_file:
            return image_file

        try:
            # Open the image using Pillow for "AI Analysis"
            img = Image.open(image_file)
            
            # --- ADVANCED AI ANALYSIS (MobileNetV2) ---
            image_bytes = image_file.read()
            image_file.seek(0) # Reset pointer
            
            from .ai_analyzer import analyze_pothole_image
            status, guesses, message = analyze_pothole_image(image_bytes)
            
            if status != 'Verified':
                guess_text = " | ".join(guesses)
                raise ValidationError(
                    f"AI Analysis Result: {status}. {message} "
                    f"Top 3 AI Guesses: {guess_text}"
                )
            # --- END AI ANALYSIS ---

            return image_file
        except ValidationError as e:
            raise e
        except Exception as e:
            # If image processing fails, allow it but log it (for robustness)
            return image_file


class PotholeUpdateForm(forms.ModelForm):
    """Form for admin to update pothole status."""
    class Meta:
        model = Pothole
        fields = ('status', 'assigned_worker', 'completion_image')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_worker': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Worker name'
            }),
            'completion_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
