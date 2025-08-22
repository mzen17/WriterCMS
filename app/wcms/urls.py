from django.urls import path, include
from wcms import views

urlpatterns = [
    path('', include(views.router.urls)),
    # Note: Removed csrf/, login/, and logout/ endpoints - using Firebase authentication
]
