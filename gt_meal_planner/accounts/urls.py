from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('reset-password/', views.reset_password, name='accounts.reset_password'),
    path('baseplans/', views.baseplans, name='accounts.baseplans'),
    path('map/', views.map, name='accounts.map'),
    path('inputspending/', views.inputspending, name='accounts.inputspending')
]