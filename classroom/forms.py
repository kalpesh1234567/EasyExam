from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Classroom, Test, Question


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_teacher = forms.BooleanField(required=False, label='Register as Teacher')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_teacher']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Data Structures - Batch A'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class JoinClassroomForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label='Classroom Code',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter 6-character code', 'style': 'text-transform:uppercase'})
    )


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'description', 'start_time', 'end_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Test name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'reference_answer', 'max_score']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Enter the question'}),
            'reference_answer': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Enter the ideal/reference answer'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 100}),
        }
