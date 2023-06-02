from .models import User
from django import forms

class MyForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=200, required=True)
    password2 = forms.CharField(max_length=200, required=True)
    # email = forms.EmailField(max_length=100, required=True)
    # captcha = CaptchaField(label='验证码')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username



"""class login_form(forms.Form):
    name = forms.CharField(max_length=100)
    password = forms.CharField"""



