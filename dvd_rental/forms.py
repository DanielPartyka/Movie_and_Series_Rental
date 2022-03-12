from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

class NewUserForm(UserCreationForm):
    username = forms.CharField(label="Username",max_length=130,required=True,widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'size':'30',
        }
    ))
    password1 = forms.CharField(label="Password",widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'size': '50',
            'type':'password',
            'minlength' : '8',
        }
    ))
    password2 = forms.CharField(label="Repeat password",widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'size': '50',
            'type':'password',
            'minlength' : '8',
        }
    ))
    email = forms.EmailField(label="Email", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'size': '50',
            'type':'email',
        }
    ))

    class Meta:
        model = User
        fields = ("username","email","password1","password2")

    def save(self,commit=True):
        user = super(NewUserForm,self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class MovieSearch(forms.Form):
    movie_search = forms.CharField(label="Seach movie",max_length=130)

class Rate(forms.Form):
    rate_value = forms.IntegerField(label="Add movie rate 1-5")

class IndexSearch(forms.Form):
    search = forms.CharField(label="Search movie, categories etc:",max_length=130)

class CaptchaTestForm(forms.Form):
    subject = forms.CharField(label="Subject", max_length=130, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'size': '30',
            'placeholder' : 'Subject...'
        }
    ))
    text = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder' : 'Write a message...'
        }
    ))
    captcha = CaptchaField()