from django.urls import path
from core.views import *

from config import settings

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('favourite/', FavouriteView.as_view(), name='favourite'),
    path('add-to-cart/', OrderItemView.as_view(), name='add-to-cart'),
    path('search/', SearchView.as_view(), name='search'),
    path('subscription/', SubscriptionCreateView.as_view(), name='subscription'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('register/', RegisterCreatView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]