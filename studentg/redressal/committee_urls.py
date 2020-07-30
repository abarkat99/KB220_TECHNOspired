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

from accounts.views import CustomPasswordChangeView, SignupView
from . import views
from studentg.views import overall_status_stats_chart

dashpatterns = [
    # path('', views.dash_home, name="dash_home"),
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('all/grievances/', views.AllGrievances.as_view(), name="all_grievances"),
    path('set/grievance/<token>/status-pending/', views.SetGrievancePending.as_view(), name="set_status_pending"),
    path('set/grievance/<token>/status-rejected/', views.SetGrievanceRejected.as_view(), name="set_status_rejected"),
    path('set/grievance/<token>/status-review/', views.SetGrievanceReview.as_view(), name="set_status_review"),
    path('set/grievance/<token>/status-resolved/', views.SetGrievanceResolved.as_view(), name="set_status_resolved"),
    path('view/subcategories/', views.ViewSubcategories.as_view(), name="view_subcategories"),
    path('view/grievance/<token>/', views.ViewGrievance.as_view(), name="view_grievance"),
    path('view/messages/<token>/', views.ViewGrievanceMessages.as_view(), name="view_messages"),
    path('view/members/', views.ViewMembers.as_view(), name="view_members"),
    path('add/member/', views.AddMember.as_view(), name="add_member"),
    path('remove/member/<pk>/', views.DeleteMember.as_view(), name="delete_member"),
    path('remove/invited-member/<pk>/', views.DeleteInvitedMember.as_view(), name="delete_invited_member"),
    path('view/bodies/', views.ViewBodies.as_view(), name="view_bodies"),
    path('add/body/', views.AddBody.as_view(), name="add_body"),
    path('remove/body/<pk>/', views.DeleteBody.as_view(), name="delete_body"),
    path('view/students/', views.ViewStudents.as_view(), name="view_students"),
    path('add/student/', views.AddStudent.as_view(), name="add_student"),

    path('stats/status-chart/', views.status_stats_chart, name="status_stats_chart"),

    path('my/account/', CustomPasswordChangeView.as_view(template_name="redressal/view_profile.html"),
         name="password_change"),
    # path('add/body/<str:body_type>/', r_views.add_body, name="add_body"),
    # path('manage/members/', r_views.manage_members, name="manage_members"),
    # path('remove/member/<pk>', r_views.remove_member, name="remove_member"),
    # path('add/subcategory/',r_views.add_subcategory, name="add_subcategory"),
    # path('add/student/', r_views.add_student, name="add_student"),
    # path('view/grievances/',r_views.view_grievances, name="view_grievances"),
    #
    # path('update/grievance/<token>/', r_views.update_grievance, name="update_grievance"),
    # path('charts/', r_views.charts, name="charts"),
    # path('grievance-chart/', r_views.grievances_line_chart, name="grievance-chart"),
]
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    # path('faq/', views.faq, name="faq"),
    path('accounts/signup/<uidb64>/<token>/', SignupView.as_view(template_name="redressal/signup.html"), name='signup'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include(dashpatterns)),
    path('stats/status-chart/', overall_status_stats_chart, name="overall_status_chart"),
    # path('contact/', views.contact,name="contact"),
    # path('about_us/',views.about_us,name="about_us"),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
