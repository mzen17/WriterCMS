from django.urls import path, include, re_path
from wcms import views

urlpatterns = [
    path('', include(views.router.urls)),
    re_path(r'^file/(?P<file_name>[^/]+)/$', views.get_file_url, name='get-file-url'),
    # Note: Removed csrf/, login/, and logout/ endpoints - using Firebase authentication
]
