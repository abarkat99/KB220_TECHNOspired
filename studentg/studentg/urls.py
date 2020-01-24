"""studentg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from redressal import views as r_views
from studentg import views

dashpatterns = [
    path('', views.dash_home, name="dash_home"),
    path('add/body/<str:body_type>', r_views.add_body, name="add_body"),
    path('add/subcategory',r_views.add_subcategory, name="add_subcategory"),
    path('add/student', views.add_student, name="add_student"),
    path('view/grievances',r_views.view_grievances, name="view_grievances"),

    path('add/grievance', views.addgrievance, name="addgrievance"),
    path('mygrievance', views.my_grievances, name="my_grievances"),
    path('update/grievance/<token>', r_views.update_grievance, name="update_grievance")
]
urlpatterns = [
    path('', views.home, name="home"),
    path('accounts/',include('accounts.urls')),
    path('dashboard/', include(dashpatterns)),
    path('admin/', admin.site.urls),
    path('load/subcategories/', views.load_subcategories,name="load_subcategories"),
    path('contact/', views.contact,name="contact"),
    path('about_us/',views.about_us,name="about_us"),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)