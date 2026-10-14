from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from quests import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='quests/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('', views.dashboard_view, name='dashboard'),
    path('quest/save/', views.create_or_edit_quest, name='create_quest'),
    path('quest/edit/<int:pk>/', views.create_or_edit_quest, name='edit_quest'),
    path('quest/delete/<int:pk>/', views.delete_quest, name='delete_quest'),
    
    # Боевое API
    path('api/quest/<int:pk>/start/', views.start_battle_api, name='start_battle'),
    path('api/quest/<int:pk>/finish/', views.finish_battle_api, name='finish_battle'),
]
