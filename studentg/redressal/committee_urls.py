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

from accounts.views import SignupView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from . import views
from studentg.views import overall_status_stats_chart

chartpatterns = [
    path('', views.charts, name="charts"),
    path('stats/status-chart/', views.status_stats_chart, name="status_stats_chart"),
    path('stats/subcat-chart/', views.subcategory_stats_chart, name="subcat_stats_chart"),
    path('stats/subcat-dependent-chart/', views.status_chart_for_subcategory, name="subcat_dependent_chart"),
    path('rating-chart/', views.rating_bar_chart, name="rating_bar_chart"),
    path('grievance-chart/', views.grievances_line_chart, name="grievance-chart"),
    path('stats/overall-status-chart/', overall_status_stats_chart, name="overall_status_chart"),
]
dashpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('all/grievances/', views.AllGrievances.as_view(), name="all_grievances"),
    path('view/subcategories/', views.ViewSubcategories.as_view(), name="view_subcategories"),
    path('view/grievance/<token>/', views.ViewGrievance.as_view(), name="view_grievance"),
    path('view/members/', views.ViewMembers.as_view(), name="view_members"),
    path('add/member/', views.AddMember.as_view(), name="add_member"),
    path('remove/member/<pk>/', views.DeleteMember.as_view(), name="delete_member"),
    path('remove/invited-member/<pk>/', views.DeleteInvitedMember.as_view(), name="delete_invited_member"),
    path('view/bodies/', views.ViewBodies.as_view(), name="view_bodies"),
    path('add/body/', views.AddBody.as_view(), name="add_body"),
    path('remove/body/<pk>/', views.DeleteBody.as_view(), name="delete_body"),
    path('view/students/', views.ViewStudents.as_view(), name="view_students"),
    path('add/student/', views.AddStudent.as_view(), name="add_student"),

    path('my/account/', PasswordChangeView.as_view(template_name="redressal/view_profile.html"),
         name="password_change"),
    path('settings/password/done/', PasswordChangeDoneView.as_view(template_name="redressal/password_change_done.html"),
         name="password_change_done"),
    path('charts/', include(chartpatterns)),
]
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('accounts/signup/<uidb64>/<token>/', SignupView.as_view(template_name="redressal/signup.html"), name='signup'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include(dashpatterns)),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
