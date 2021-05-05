"""plantifultest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from plantifultest import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from plantifultest.views import update_settings_dropdown

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('app/share/', views.share, name='share'),
    path('app/',views.dashboard,name='dashboard'),
    path('app/newproject/',views.newproject,name='newproject'),
    
    path('change_password/', views.change_password, name='change_password'),
    path('app/newgroup/<str:project_id>/<str:groups_num>/',views.newgroup,name='newgroup'),
    path('app/project_settings/',views.project_settings,name='project_settings'),
    path('app/group_settings/',views.group_settings,name='group_settings'),
  
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="passwordr.html"), name="reset_password"),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="passwordr_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name="passwordr_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="passwordr_complete.html"), name="password_reset_complete"),
    
    path('app/newgroup/<str:project_id>/<str:groups_num>/ajax_settings_dropdown', views.update_settings_dropdown)
]
