from django.conf.urls import url
from djautotask import views

app_name = 'djautotask'

urlpatterns = [
    url(
        regex=r'^callback/$',
        view=views.CallBackView.as_view(),
        name='callback'
    ),
]
