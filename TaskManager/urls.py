from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tasks.urls.api")),
    path("", include("accounts.urls")),
    path("tasks/", include("tasks.urls.web")), 
]
