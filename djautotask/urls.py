from django.urls import re_path
from djautotask import views

app_name = 'djautotask'

urlpatterns = [
    re_path(
        r'^callback/$',
        view=views.CallBackView.as_view(),
        name='callback'
    ),
]
