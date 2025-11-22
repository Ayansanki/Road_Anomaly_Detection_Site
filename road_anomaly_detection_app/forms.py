from django import forms
from django.core.exceptions import ValidationError
from road_anomaly_detection_app.models import *
from django.utils import timezone
from road_anomaly_detection_app.utils import validate_password

    
class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(
        max_length=128, 
        required=True, 
        widget=forms.PasswordInput  # Good practice to hide password input
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def check_password(self):
        password = self.cleaned_data.get('password')
        if password and validate_password(password):
            return True
        return False
    
    def check_duplicates(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            return True
        return False

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            name=self.cleaned_data['name'],
            password=self.cleaned_data['password']
        )
        return user
    

class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(
        max_length=128, 
        required=True, 
        widget=forms.PasswordInput  # Good practice to hide password input
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    @property
    def get_email(self):
        return self.cleaned_data.get('email')
    
    @property
    def get_password(self):
        return self.cleaned_data.get('password')


# class RoadAnomalyReportForm(forms.ModelForm):
#     """
#     A form to handle the creation of a new RoadAnomalyReport.
    
#     This form will:
#     - Accept user input for the report details.
#     - Accept multiple file uploads.
#     - On save, create new MediaContent objects for each uploaded file.
#     - Store a list of references to these MediaContent objects in the
#       RoadAnomalyReport's 'files' JSONField.
#     """

#     # 1. Add a field for file uploads.
#     # This field is not on the model, so we add it directly to the form.
#     # We use ClearableFileInput with 'multiple': True to allow multiple files.
#     uploaded_files = forms.FileField(
#         widget=forms.ClearableFileInput(attrs={'multiple': True}),
#         required=False, # Set to True if uploads should be mandatory
#         label="Upload Images/Videos"
#     )

#     class Meta:
#         model = RoadAnomalyReport
        
#         # 2. List all fields the user WILL provide.
#         # Fields like 'status', 'posted_at', etc., are excluded
#         # because the model handles them with defaults or auto_now_add.
#         fields = [
#             'registerID',
#             'areaName',
#             'pincode',
#             'roadname',
#             'geolocation',
#             'fileType',
#             'instructions',
#         ]
        
#         # 3. Make the 'registerID' field hidden, as requested.
#         widgets = {
#             'registerID': forms.HiddenInput(),
#         }

#     def clean_geolocation(self):
#         """
#         Validate and process the geolocation string.
#         Assumes input format is a string: "latitude, longitude".
#         Converts it to the JSON format (dict) the model expects.
#         """
#         geo_string = self.cleaned_data.get('geolocation')
        
#         # Handle empty geolocation if it's not required
#         if not geo_string:
#             if self.fields['geolocation'].required:
#                  raise ValidationError("This field is required.")
#             return None

#         try:
#             # Parse the "lat, lng" string
#             lat_str, lng_str = geo_string.split(',')
#             lat = float(lat_str.strip())
#             lng = float(lng_str.strip())
            
#             # 4. Return the data as a dictionary.
#             # The JSONField will automatically serialize this dict to JSON.
#             return {'latitude': lat, 'longitude': lng}
#         except (ValueError, IndexError, TypeError):
#             raise ValidationError("Invalid geolocation format. Please use 'latitude, longitude'.")

#     def save(self, commit=True):
#         """
#         Override the save method to handle file processing.
#         """
#         # 5. Get the RoadAnomalyReport instance, but don't save to DB yet.
#         # This gives us a chance to modify it before the final save.
#         report_instance = super().save(commit=False)
        
#         file_references = []
        
#         # 6. Loop through each file uploaded in the 'uploaded_files' field.
#         # We access files from 'self.files', not 'self.cleaned_data'.
#         for uploaded_file in self.files.getlist('uploaded_files'):
#             # Generate a unique ID for the file
#             file_id = str(uuid.uuid4())
            
#             # Determine the file type (e.g., IMAGE, VIDEO)
#             # This is a simple example; you might need more robust logic.
#             content_type = uploaded_file.content_type
#             file_type_choice = FileTypeChoise.IMAGE  # Default
#             if 'video' in content_type:
#                 file_type_choice = FileTypeChoise.VIDEO
#             # ... add other types as needed
            
#             # 7. Create and save the MediaContent object with the file's binary data
#             MediaContent.objects.create(
#                 file_id=file_id,
#                 binary_data=uploaded_file.read(),
#                 content_type=file_type_choice
#             )
            
#             # 8. Create the reference dictionary to store in the JSON field
#             file_references.append({
#                 'file_type': file_type_choice,
#                 'file_id': file_id
#             })

#         # 9. Assign the list of references to the 'files' JSONField
#         report_instance.files = file_references
        
#         # 10. Now, save the complete RoadAnomalyReport instance to the DB
#         if commit:
#             report_instance.save()
            
#         return report_instance


# class RoadAnomalyReportForm(forms.ModelForm):
#     # # User-provided fields
#     # # register_ID = forms.CharField(max_length=255, required=True)
#     # register_ID = forms.CharField(widget=forms.HiddenInput())
#     # areaName = forms.CharField(max_length=255, required=False, label='Area Name')
#     # pincode = forms.IntegerField(required=False, label='Pincode')
#     # roadName = forms.CharField(max_length=255, required=True, label='Road Name')
    
#     # location = forms.CharField(max_length=255, required=True, label="Geo Location")
    
#     # file_type = forms.ChoiceField(choices=FileTypeChoise.choices, initial=FileTypeChoise.IMAGE, label='Default File Type')
    
#     # # Handle multiple file uploads
#     # files = forms.FileField(
#     #     # widget=forms.ClearableFileInput(attrs={'multiple': True}),
#     #     required=False,
#     #     label='Upload Files (Images/Videos etc.)'
#     # )

#     # instructions = forms.CharField(widget=forms.Textarea, required=False, label='Instructions')
    
#     # class Meta:
#     #     model = RoadAnomalyReport
#     #     fields = ['register_ID', 'areaName', 'pincode', 'roadName', 'location', 'file_type', 'files', 'instructions']  # No direct model fields; we're overriding everything for custom processing
#     #     # Excludes: posted_at, status, anomalyType, anomalyImage (auto-handled)
#     #     # registerID: auto-generated UUID


#     # files = forms.FileField(
#     #     widget=forms.ClearableFileInput(attrs={'multiple': True}),
#     #     required=False, # Set to True if uploads should be mandatory
#     #     label="Upload Images/Videos"
#     # )
#     files = forms.FileField(
#         # widget=forms.ClearableFileInput(attrs={'multiple': True}),
#         required=False,
#         label='Upload Files (Images/Videos etc.)'
#     )

#     geolocation = forms.JSONField(
#         required = True
#     )

#     class Meta:
#         model = RoadAnomalyReport
        
#         # 2. List all fields the user WILL provide.
#         # Fields like 'status', 'posted_at', etc., are excluded
#         # because the model handles them with defaults or auto_now_add.
#         fields = [
#             'register',
#             'areaname',
#             'pincode',
#             'roadname',
#             'filetype',
#             'instructions',
#         ]
        
#         # 3. Make the 'registerID' field hidden, as requested.
#         widgets = {
#             'register': forms.HiddenInput(),
#         }



#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # print(self.fields)
#         # for i in self.fields:
#         #     print(i)

#         # print(self.fields['register_ID'])
#         # print(self.fields['location'])

#         # Map form fields to model field names for internal use
#         # self.fields['registerID'] = self.fields.pop('register_ID')
#         # self.fields['areaName'] = self.fields.pop('area_name')
#         # self.fields['roadname'] = self.fields.pop('road_name')
#         # self.fields['location'] = self.fields.pop('geo_location')

#     def clean(self):
#         cleaned_data = super().clean()
#         print(cleaned_data)
#         geo_location:str = cleaned_data.get('location')
#         geo_location = geo_location[0].split(',')
#         if len(geo_location) > 2:
#             raise forms.ValidationError("Invalid Location.")
        
#         latitude, longitude = float(geo_location[0]), float(geo_location[1])
        
#         if latitude is not None and longitude is not None:
#             # Validate geolocation bounds (optional)
#             if not (-90 <= latitude <= 90):
#                 raise forms.ValidationError("Latitude must be between -90 and 90.")
#             if not (-180 <= longitude <= 180):
#                 raise forms.ValidationError("Longitude must be between -180 and 180.")
            
#         self.fields['latitude'] = latitude
#         self.fields['longitude'] = longitude
#         return cleaned_data

#     def save(self, commit=True):
#         # Create the base instance
#         instance = RoadAnomalyReport(
#             register=self.cleaned_data['register'],  # Auto-generate UUID if not defaulted in model
#             areaname=self.cleaned_data['areaname'],
#             pincode=self.cleaned_data['pincode'],
#             roadname=self.cleaned_data['roadname'],
#             geolocation={
#                 'lat': self.cleaned_data['latitude'],
#                 'lng': self.cleaned_data['longitude']
#             },
#             fileType=FileTypeChoise.IMAGE,  # Default file type for the report
#             instructions=self.cleaned_data['instructions'],
#             # Auto-set non-user fields
#             # posted_at=timezone.now(),  # Or let auto_now_add handle it
#             status=StatusTypeChoise.PROCESS,
#             anomalyType=None,  # Blank
#             anomalyImage=None,  # Blank
#             files=[]  # Will populate below
#         )

#         if commit:
#             # instance.save()
#             # Process uploaded files: Create MediaContent instances and populate files JSON
#             files_data = self.cleaned_data.get('files')
#             if files_data:  # It's a list of files due to multiple=True
#                 media_files = []
#                 default_file_type = self.cleaned_data['file_type']
                
#                 for uploaded_file in files_data:
#                     # Determine file_type based on extension or default (simplified)
#                     file_extension = uploaded_file.name.split('.')[-1].lower()
#                     file_type = default_file_type
#                     if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
#                         file_type = FileTypeChoise.IMAGE
#                     elif file_extension in ['mp4', 'avi', 'mov']:
#                         file_type = FileTypeChoise.VIDEO  # Assuming VIDEO choice exists
#                     else:
#                         forms.ValidationError("Unknown File Type.")
#                     # Add more mappings as needed
#                     file_id = f"{uuid.uuid4()} - {self.cleaned_data['registerID']}"
#                     # Create MediaContent instance
#                     media_content = MediaContent(
#                         file_id = file_id,
#                         binary_data = uploaded_file,
#                         content_type = file_type
#                     )
#                     media_content.save()

#                     # Append to files JSON: {'file_type': str, 'file_id': str(media_content.id)}
#                     media_files.append({
#                         'file_type': file_type,
#                         'file_id': str(media_content.file_id)
#                     })

#                 # Update the report's files field
#                 instance.files = media_files
#                 # instance.save(update_fields=['files'])
#                 instance.save()

#         return instance


class RoadAnomalyReportForm():
    def __init__(self, data, files, user, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self.fields = {k: v[0] if isinstance(v, list) else v for k, v in data.items()}
        self.fields.update(files)

        self.clean_keys = ['register_ID', 'areaname', 'pincode', 'roadname', 'geolocation', 'instruction']

        self.fields.update({'register_ID': f"{user.name} - {user.email}"})

        self.clean()

    def clean(self):       
        geo_location : str = self.fields['geolocation']

        # print(geo_location, type(geo_location), geo_location[0], type(geo_location[0]))
        geo_location = geo_location.split(', ')

        latitude, longitude = float(geo_location[0]), float(geo_location[1])
        
        # if latitude is not None and longitude is not None:
        #     # Validate geolocation bounds (optional)
        #     if not (-90 <= latitude <= 90):
        #         raise ValidationError("Latitude must be between -90 and 90.")
        #     if not (-180 <= longitude <= 180):
        #         raise ValidationError("Longitude must be between -180 and 180.")
            
        self.fields['latitude'] = latitude
        self.fields['longitude'] = longitude

        return self.fields


    def is_valid(self):
        if all(key in self.fields.keys() for key in self.clean_keys):
            self.cleaned_data = self.fields
            return True
        return False
        
    def save(self, commit=True):
        # Create the base instance
        instance = RoadAnomalyReport(
            register=self.cleaned_data['register_ID'],  # Auto-generate UUID if not defaulted in model
            areaname=self.cleaned_data['areaname'],
            pincode=self.cleaned_data['pincode'],
            roadname=self.cleaned_data['roadname'],
            geolocation={
                'lat': self.cleaned_data['latitude'],
                'lng': self.cleaned_data['longitude']
            },
            filetype=FileTypeChoise.IMAGE,  # Default file type for the report
            instructions=self.cleaned_data['instruction'],
            # Auto-set non-user fields
            posted_at=timezone.now(),  # Or let auto_now_add handle it
            status=StatusTypeChoise.PROCESS,
            anomalyType=None,  # Blank
            anomalyImage=None,  # Blank
            files=[]  # Will populate below
        )

        if commit:
            # instance.save()
            # Process uploaded files: Create MediaContent instances and populate files JSON
            files_data = self.cleaned_data.get('files')
            if files_data:  # It's a list of files due to multiple=True
                media_files = []
                default_file_type = FileTypeChoise.IMAGE
                
                for uploaded_file in files_data:
                    # Determine file_type based on extension or default (simplified)
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    file_type = default_file_type
                    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                        file_type = FileTypeChoise.IMAGE
                    elif file_extension in ['mp4', 'avi', 'mov']:
                        file_type = FileTypeChoise.VIDEO  # Assuming VIDEO choice exists
                    else:
                        ValidationError("Unknown File Type.")
                    # Add more mappings as needed
                    file_id = f"{uuid.uuid4()} - {self.cleaned_data['register_ID']}"
                    # Create MediaContent instance
                    media_content = MediaContent(
                        file_id = file_id,
                        binary_data = uploaded_file.read(),
                        content_type = file_type
                    )
                    media_content.save()

                    # Append to files JSON: {'file_type': str, 'file_id': str(media_content.id)}
                    media_files.append({
                        'file_type': file_type,
                        'file_id': str(media_content.file_id)
                    })

                # Update the report's files field
                instance.files = media_files
                # instance.save(update_fields=['files'])
                instance.save()

        return instance

