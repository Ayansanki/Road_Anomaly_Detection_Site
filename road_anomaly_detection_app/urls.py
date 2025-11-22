from django.contrib import admin
from django.urls import path, include
from road_anomaly_detection_app import views

urlpatterns = [
    path('', views.index, name='index'),

    path('auth/signin', views.sign_in, name='login'),
    path('auth/signup', views.sign_up, name='signup'),
    path('auth/logout', views.logout_user, name='logout'),

    path('report', views.upload_anomaly_report_page, name="uploadReport"),
    path('view', views.view_reports_page, name="viewReport"),
    path('view/<int:report_id>', views.report_detailed_view_page, name="detailedViewReport"),
    path('view/<int:report_id>/image/', views.AnomalyImageView.as_view(), name='anomaly_image'),
    
    
    path('404', views.custom_404, name='custom_404'),
    # path('silent-form/', views.silent_form_view, name='silent-form'),
    # path('submit-silent-form/', views.silent_form_submit_view, name='silent-submit')
]
