from django.urls import path
from core.views import *

from config import settings

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
]