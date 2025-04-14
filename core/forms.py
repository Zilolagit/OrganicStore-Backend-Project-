
from django.contrib.auth.hashers import make_password
from django.forms import CharField, Form
from django.forms.models import ModelForm

from core.models import Subscription, User


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ('email', 'name')


class RegisterModelForm(ModelForm):
    class Meta:
        model=User
        fields=('name','password','email')
    def clean_password(self):
        password=self.cleaned_data.get('password')
        hash=make_password(password)
        return hash

class LoginForm(Form):
    email=CharField(max_length=255, required=True)
    password=CharField(max_length=255, required=True)
