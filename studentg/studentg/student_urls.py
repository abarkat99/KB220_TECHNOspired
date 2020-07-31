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
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.defaults import page_not_found, server_error, permission_denied
from . import views
from accounts.views import SignupView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

dashpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('add/grievance/', views.CreateGrievance.as_view(), name="add_grievance"),
    path('edit-draft/grievance/<token>/', views.EditDraftGrievance.as_view(), name="edit_grievance"),
    path('load/subcategories/', views.LoadSubcategories.as_view(), name="load_subcategories"),
    path('all/grievances/', views.AllGrievances.as_view(), name="all_grievances"),
    path('view/grievance/<token>/', views.ViewGrievance.as_view(), name="view_grievance"),
    # path('view/messages/<token>/', views.ViewGrievanceMessages.as_view(), name="view_messages"),

    path('stats/status-chart/', views.status_stats_chart, name="status_stats_chart"),

    path('my/account/', PasswordChangeView.as_view(template_name="studentg/view_profile.html"),
         name="password_change"),
    path('settings/password/done/', PasswordChangeDoneView.as_view(template_name="studentg/password_change_done.html"),
         name="password_change_done"),
    # path('getgrievance/<token>/',views.getgrievance, name="getgrievance"),
]
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('403/', lambda request: permission_denied(request, None)),
    path('404/', lambda request: page_not_found(request, None)),
    path('500/', lambda request: server_error(request)),
    # path('faq/', views.faq, name="faq"),
    path('accounts/signup/<uidb64>/<token>/', SignupView.as_view(template_name="studentg/signup.html"), name='signup'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include(dashpatterns)),
    path('stats/status-chart/', views.overall_status_stats_chart, name="overall_status_chart"),
    # path('admin/', admin.site.urls),
    # path('contact/', views.contact,name="contact"),
    # path('about_us/',views.about_us,name="about_us"),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
