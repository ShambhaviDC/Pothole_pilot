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
            
            # --- SIMULATED AI DETECTION LOGIC ---
            # In a real-world app, you'd use a model like YOLO or TensorFlow here.
            # For this hackathon version, we use a color profile check.
            # Asphalt/Potholes are usually dark/grey/brown.
            
            # 1. Convert to RGB and resize
            img = img.convert('RGB')
            img.thumbnail((60, 60)) 
            
            pixels = list(img.getdata())
            road_score = 0
            total_pixels = len(pixels)
            
            import statistics
            brightness_values = []
            saturations = []
            
            for r, g, b in pixels:
                # Saturation (high = colorful/indoor/natural, low = asphalt/concrete)
                mx, mn = max(r, g, b), min(r, g, b)
                sat = mx - mn
                saturations.append(sat)
                
                # Brightness
                bright = (r + g + b) / 3
                brightness_values.append(bright)
                
                # --- ULTRA-STRICT ROAD PROFILE ---
                # Real roads/potholes are almost entirely shades of Grey, Mud-Brown, or Black
                if sat < 25: # Very strict neutral check
                    if bright < 70: road_score += 1.8 # Dark shadows/hole (high weight)
                    elif bright < 160: road_score += 1.2 # Grey asphalt
                elif sat < 40 and r > g and g > b: # Very specific mud/dirt brown
                    road_score += 0.6
                else:
                    # HEAVY PENALTY for any vibrant color (Red, Blue, Green, Orange)
                    # This will instantly kill photos of desks, clothing, electronics, etc.
                    if sat > 50:
                        road_score -= 3.0
            
            # --- AGGREGATE METRICS ---
            avg_sat = sum(saturations) / total_pixels
            # Variance helps ignore flat surfaces like a grey wall or uniform carpet
            variance = statistics.stdev(brightness_values) if len(brightness_values) > 1 else 0
            road_ratio = (road_score / total_pixels) * 100
            
            # --- FINAL HEURISTIC GATE ---
            # 1. Global Saturation must be extremely low (Avg < 35)
            # 2. Road score must be dominant (Ratio > 45)
            # 3. Must have enough texture/shadow (Variance > 15)
            if avg_sat > 35 or road_ratio < 45 or variance < 15:
                raise ValidationError(
                    "AI Security Check Failed: This image does not appear to be a road surface. "
                    "Please ensure you are taking a close-up photo of the pothole itself. "
                    "Avoid having colorful objects, people, or indoor backgrounds in the frame."
                )
            # --- END SIMULATED AI ---

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
