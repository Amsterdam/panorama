from django.conf.urls import url

from health import views

urlpatterns = [
    url(r'^health$', views.health),
    url(r'^data$', views.check_data),

]