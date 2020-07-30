from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

reset_patterns = [
    path('',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ),
         name='password_reset'),
    path('done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]
# change_password_patterns = [
#     # path('', auth_views.PasswordChangeView.as_view(template_name='accounts/view_profile.html',
#     #                                                success_url=reverse_lazy('dashboard')),
#     #      name='password_change'),
#     path('', views.CustomPasswordChangeView.as_view(), name='password_change'),
#     # path('done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
#     #      name='password_change_done'),
# ]
urlpatterns = [
    # path('signup/<uidb64>/<token>/', views.signup, name='signup'),

    #     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name="login"),

    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name="logout"),

    path('reset/', include(reset_patterns)),

    # path('settings/password/', include(change_password_patterns)),
]
