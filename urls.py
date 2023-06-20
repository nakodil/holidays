from django.urls import path
from .views import get_holidays

app_name = "holidays"

urlpatterns = [
    path('<str:start_date>/<str:stop_date>/', get_holidays, name='get_holidays'),
]