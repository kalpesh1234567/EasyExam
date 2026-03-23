from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from classroom import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('teacher/signup/', views.teacher_signup, name='teacher_signup'),
    path('student/login/', auth_views.LoginView.as_view(template_name='classroom/student_login.html'), name='student_login'),
    path('teacher/login/', auth_views.LoginView.as_view(template_name='classroom/teacher_login.html'), name='teacher_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Teacher URLs
    path('classroom/create/', views.create_classroom, name='create_classroom'),
    path('classroom/<int:pk>/', views.view_classroom, name='view_classroom'),
    path('classroom/<int:pk>/test/create/', views.create_test, name='create_test'),
    path('test/<int:pk>/', views.view_test, name='view_test'),
    path('test/<int:pk>/question/add/', views.add_question, name='add_question'),
    path('test/<int:pk>/students/', views.students_work, name='students_work'),
    path('answer/<int:pk>/review/', views.review_answer, name='review_answer'),
    path('answer/<int:pk>/update-score/', views.update_score, name='update_score'),

    # Student URLs
    path('classroom/join/', views.join_classroom, name='join_classroom'),
    path('test/<int:pk>/attend/', views.attend_test, name='attend_test'),
    path('test/<int:pk>/submit/', views.submit_test, name='submit_test'),
    path('test/<int:pk>/result/', views.test_result, name='test_result'),

    # API
    path('api/evaluate/', views.evaluate_answer_api, name='evaluate_answer_api'),
]
