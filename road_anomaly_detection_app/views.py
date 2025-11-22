from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages

from road_anomaly_detection_app.forms import *
from road_anomaly_detection_app.models import *
from road_anomaly_detection_app.backend import *

from road_anomaly_detection_app.tasks import data_classifier

from threading import Thread

import plotly.express as px
import plotly.io as pio
# import pandas as pd


from functools import lru_cache


# Create your views here.
def index(request):
    print(f"View user: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
    return render(request, 'home.html', context={
        "data": {
            "total_reports": RoadAnomalyReport.objects.count(),
        }
    })

def custom_404(request):
    return render(request, '404.html', status=404)

def sign_up(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print(form.check_password())
            if not form.check_password():
                messages.error(request, "Password must contain 8 characters and special characters.")
                return render(request, 'signup.html', context={
                    'form':form
                })
            
            print(form.check_duplicates())
            if form.check_duplicates():  
                messages.error(request, "Email already exists.")
                return render(request, 'signup.html', context={
                    'form':form
                })
            
            user = form.save()
            print(user)
            if user is not None:
                login(request, user, backend ='road_anomaly_detection_app.backend.EmailBackend')
                messages.success(request, 'Registration successful!')
                return redirect('/')
            else:
                messages.success(request, 'Authentication Failed!')
                return redirect('/')
        else:
            form = UserRegistrationForm()
            messages.error(request, "Form is not Valid.")
            return render(request, 'signup.html', context={
                'form':form
            })
    else:
        return render(request, 'signup.html')
    
def sign_in(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            authenticated_user = EmailBackend().authenticate(request, email=form.get_email, password=form.get_password)
            print(authenticated_user)    
            if authenticated_user is not None:
                print(authenticated_user.email, authenticated_user.is_active)
                login(request,  authenticated_user, backend = 'road_anomaly_detection_app.backend.EmailBackend')
                print("login successful")
                messages.success(request, 'Login successful!')
                return redirect('/')
            else:
                form = UserLoginForm()
                messages.error(request, "Form is not Valid.")
                return render(request, 'login.html', context={
                    'form':form
                })
    else:
        return render(request, 'login.html')

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/')

@login_required
def upload_anomaly_report_page(request):
    if request.method == 'POST':
        try:
            print(request)
            print(request.POST)
            print(request.FILES)
            print(request.POST.get('register'))
            form = RoadAnomalyReportForm(request.POST, request.FILES, request.user)
            if form.is_valid():
                # form.clean()
                instance = form.save()
                if instance:
                    messages.success(request, 'Form Uploaded Successfully!')

                    # data_classifier(instance)
                    thread = Thread(target=data_classifier, args=(instance, ))
                    thread.daemon = True
                    thread.start()

                    # return 
                else:
                    messages.error(request, 'Form upload failed!')
                return redirect('/')
            else:
                messages.success(request, 'Form not valid.')
                return redirect('report')
        except ValidationError as v:
            messages.error(request, v.message)
            return redirect('report')
        except Exception as e:
            messages.error(request, "An error occurs.")
            return redirect('report')
    else:
        return render(request, 'upload_form.html')
    

@login_required
@lru_cache(maxsize=8)
def view_reports_page(request):
    try:
        dataset: RoadAnomalyReport = RoadAnomalyReport.objects.all()
    
        if dataset.count() == 0:
            messages.info(request, "No reports found.")
            return render(request, 'view_reports.html', context={
                "dataset": dataset,
                "graph" : ""
            })
        
        df_data = [{
                    "centroid_lat": i.geolocation.get('lat'),
                    "centroid_lon": i.geolocation.get('lng'),
                    "names": i.roadname
                } for i in dataset]
        fig = px.scatter_map(df_data,
                            lat="centroid_lat",
                            lon="centroid_lon",
                            hover_name="names",
                            zoom=5)
        return render(request, 'view_reports.html', context={
            "dataset": dataset,
            "graph" : pio.to_html(fig, full_html=False)
        })
    except Exception as e:
        print(e)
        messages.error(request, "An error occurs while loading the reports.")
        return redirect('/')

    

@login_required
@require_POST
def report_search_request(request):
    """
    only handel post-json request and send jsonresponse
    """
    ...

@login_required
def report_load_request(request):
    ...


class AnomalyImageView(View):
    def get(self, request, report_id):
        try:
            report = RoadAnomalyReport.objects.only('anomalyImage').filter(pk=report_id)[0]
        except RoadAnomalyReport.DoesNotExist:
            raise Http404("Report not found")

        if not report.anomalyImage:
            raise Http404("No image attached")

        # Guess MIME type (fallback to jpeg)
        from PIL import Image
        import io
        try:
            img = Image.open(io.BytesIO(report.anomalyImage))
            mime = f"image/{img.format.lower()}"
        except Exception:
            mime = "image/jpeg"

        response = HttpResponse(report.anomalyImage, content_type=mime)
        response['Content-Disposition'] = f'inline; filename="anomaly_{report_id}.jpg"'
        return response

@login_required
def report_detailed_view_page(request, report_id):
    data = RoadAnomalyReport.objects.filter(pk=report_id)
    return render(request, 'detailed_report_view.html', context={
        'data': data[0], 
    })
