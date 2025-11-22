import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import BaseUserManager



# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email).lower()
        # email = email.lower()
        extra_fields.setdefault('is_staff', False)  # Default for regular users
        extra_fields.setdefault('is_superuser', False)
        user = self.model(name=name, email=email, **extra_fields)
        user.password = make_password(password, salt=None, hasher='default')  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(name, email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)

class User(models.Model):  # ONLY inherit from models.Model—no PermissionsMixin
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Required for superuser permissions
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Natural key for authentication
    REQUIRED_FIELDS = ['name']  # Fields prompted in createsuperuser

    def __str__(self):
        return self.email


    def check_password(self, raw_password):
        """Check if the provided password matches the stored hashed password."""
        return check_password(raw_password, self.password)
        # return raw_password == self.password

    @property
    def is_authenticated(self):
        """Return True if the user is active (eligible for authentication)."""
        return self.is_active

    @property
    def is_anonymous(self):
        """Return False, as this represents a user instance (not anonymous)."""
        return not self.is_active

    # Manual implementations for permissions (replaces PermissionsMixin—no MRO conflict)
    def has_perm(self, perm, obj=None):
        """Return True if user has specific permission (e.g., 'app.change_model')."""
        if self.is_superuser:
            return True
        # Extend here if adding custom permissions (e.g., check a list or field)
        return False

    def has_module_perms(self, app_label):
        """Return True if user has any permission for the app (fixes admin error)."""
        if self.is_superuser or self.is_staff:
            return True
        # Extend here for granular checks
        return False

    def get_all_permissions(self):
        """Return set of all permission strings (empty for non-superusers)."""
        if self.is_superuser:
            return set()  # Superusers implicitly have all
        return set()

    def get_group_permissions(self, obj=None):
        """Return set of group-based permissions (empty, as no groups)."""
        return set()


class FileTypeChoise(models.TextChoices):
    IMAGE = 'Image'
    VIDEO = 'Video'

class StatusTypeChoise(models.TextChoices):
    PROCESS = 'Processing'
    PENDING = 'Pending'
    PROGRESS = 'In Progress'
    RESOLVE = 'Resolved'
    ERROR = 'Error'

class RoadAnomalyReport(models.Model):
    register = models.CharField(max_length=255)
    areaname = models.TextField(null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    roadname = models.TextField()
    geolocation = models.JSONField()
    filetype = models.TextField(max_length=5, choices=FileTypeChoise.choices, default=FileTypeChoise.IMAGE)
    files = models.JSONField()
    instructions = models.TextField(null=True, blank=True)

    posted_at = models.DateTimeField(auto_now_add=True)

    status = models.TextField(max_length=12, choices=StatusTypeChoise.choices, default=StatusTypeChoise.PROCESS)
    anomalyType = models.TextField(null=True, blank=True)
    anomalyImage = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return str(self.register)
    
    def get_image_data(self):
        """Return base64-encoded image for HTML <img> tag."""
        if self.anomalyImage:
            import base64
            return base64.b64encode(self.anomalyImage).decode('utf-8')
        return None

    def get_image_mime(self):
        """Guess MIME type (optional, for <img src>)"""
        if self.anomalyImage:
            from PIL import Image
            import io
            try:
                img = Image.open(io.BytesIO(self.anomalyImage))
                return f"image/{img.format.lower()}"
            except Exception:
                return "image/jpeg"  # fallback
        return None


class MediaContent(models.Model):
    file_id = models.CharField(max_length=255, primary_key=True, unique=True)
    binary_data = models.BinaryField(blank=True, null=True)
    content_type = models.TextField(max_length=5, choices=FileTypeChoise.choices, default=FileTypeChoise.IMAGE)

    def __str__(self):
        return self.file_id
