from django.urls import path, include
from wcms import views

urlpatterns = [
    path('', include(views.router.urls)),
    path('csrf/', views.get_csrf_token, name='csrf'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
