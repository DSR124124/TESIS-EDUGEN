from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('access-denied/', views.AccessDeniedView.as_view(), name='access_denied'),
    path('social-auth-error/', views.SocialAuthErrorView.as_view(), name='social_auth_error'),
]
