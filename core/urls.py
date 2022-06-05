"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from eva import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='index'), 
    path('login/', views.login, name='login'), 
    path('login_qr/', views.login_qr, name='login_qr'), 
    path('register/', views.register, name='register'),
    path('evaluate/', views.evaluate, name='evaluate'),
    path('admin/', admin.site.urls),
    path('app/', views.app, name='app'),
    path('evaluation/', views.evaluation, name='evaluation'),
    path('evaluation_sheet/<int:pk>', views.evaluation_sheet, name='evaluation_sheet'),
    path('department/<int:pk>', views.department_detail, name='department_detail'),
    path('departments/', views.departments, name='departments'),
    path('department_delete/<int:pk>', views.department_delete, name='department_delete'),
    path('employees/', views.employees, name='employees'),
    path('employees_new/', views.employees_new, name='employees_new'),
    path('employee_delete/<int:pk>', views.employee_delete, name='employee_delete'),
    path('employee/<int:pk>', views.employee_detail, name='employee_detail'),
    path('reports/', views.reports, name='reports'),
    path('logout/', views.logout, name='logout'),
    path('profile_admin/', views.profile_admin, name='profile_admin'),
    path('admin_detail/<int:pk>', views.admin_detail, name='admin_detail'),
    path('company_detail/', views.company_detail, name='company_detail'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('evaluate_admin/', views.evaluate_admin, name='evaluate_admin'),
    path('evaluate_group_admin/', views.evaluate_group_admin, name='evaluate_group_admin'),
    path('questions/', views.questions, name='questions'),
    path('question_delete/<int:pk>', views.question_delete, name='question_delete'),
    path('question_categories/', views.question_categories, name='question_categories'),
    path('question_category_delete/<int:pk>', views.question_category_delete, name='question_category_delete'),
    path('question_category/<int:pk>', views.question_category_detail, name='question_category_detail'),
    
    path('evaluate_admin/<int:pk>', views.evaluate_group_admin_detail, name='evaluate_admin'),
    
    path('evaluate_employee/<int:pk>', views.evaluate_employee_detail, name='evaluate_employee'),

    path('question_link_category/<int:pk>', views.question_link_category, name='question_link_category'),
    path('question_link_category/<int:pk>/<str:success>', views.question_link_category, name='question_link_category'),

    path('evaluation_link_category/<int:pk>', views.evaluation_link_category, name='evaluation_link_category'),
    path('evaluation_link_category/<int:pk>/<str:success>', views.evaluation_link_category, name='evaluation_link_category'),

    path('add_question_category_link/<int:category_id>/<int:question_id>', views.add_question_category_link, name='add_question_category_link'),
    path('add_evaluation_category_link/<int:evaluation_group_id>/<int:category_id>', views.add_evaluation_category_link, name='add_evaluation_category_link'),


    path('question_category_link_delete/<int:cat>/<int:pk>' , views.question_category_link_delete , name='question_category_link_delete'),

    path('evaluate_list_group/<int:pk>', views.evaluate_list_group, name='evaluate_list_group'),

    
    path('ranking', views.ranking, name='ranking'),
    path('ranking_employee', views.ranking_employee, name='ranking_employee'),

    path('evaluate_list_group_ranking/<int:group_id>/<int:department_id>' , views.evaluate_list_group_ranking , name="evaluate_list_group_ranking"),






    # Employee
    path('profile/', views.profile, name='profile'),
    path('evaluation_employee/', views.evaluation_employee, name='evaluation_employee'),
    path('evaluation_list_sheet/<int:pk>', views.evaluation_list_sheet, name='evaluation_list_sheet'),
    path('evaluate_employee/', views.evaluate_employee, name='evaluate_employee'),
    path('about_employee/', views.about_employee, name='about_employee'),
      

    # POST paths
    path('post_evaluate/', views.post_evaluate, name='post_evaluate'),
    path('post_image_admin_detail/<int:pk>', views.post_image_admin_detail, name='post_image_admin_detail'),
    path('post_image_employee/<int:pk>', views.post_image_employee, name='post_image_employee'),
    path('post_image_company/', views.post_image_company, name='post_image_company'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)