from django.conf.urls import url, include

urlpatterns = [
    url(r'^callback/', include(
        'djautotask.urls', namespace='djautotask')
        ),
]
