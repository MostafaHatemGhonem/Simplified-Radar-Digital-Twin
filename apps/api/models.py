from django.conf import settings
from django.db.models import RESTRICT
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # username = models.CharField(max_length=112, unique=True)
    # password = models.CharField(_("password"), max_length=128)
    # email = models.EmailField(blank=True)
    # first_name = models.CharField(blank=True,max_length=112)
    # last_name = models.CharField(blank=True,max_length=112)
    # is_active = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    # date_joined = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email']


class RadarConfiguration(models.Model):
    """
    In This Models:
        create_by => User.
        A configuration can be referenced by many experiments.
        Define whether sharing is allowed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=112)
    description = models.TextField(blank=True)
    carrier_frequency_hz = models.DecimalField(
        max_digits=20, decimal_places=4, validators=[MinValueValidator(0)]
    )
    bandwidth_hz = models.DecimalField(
        max_digits=20, decimal_places=4, validators=[MinValueValidator(0)]
    )
    chirp_duration_s = models.DecimalField(
        max_digits=15, decimal_places=9, validators=[MinValueValidator(0)],
        help_text="Chirp duration in seconds (supports microsecond precision)"
    )
    sample_rate_hz = models.DecimalField(
        max_digits=20, decimal_places=4, validators=[MinValueValidator(0)]
    )
    transmit_power_w = models.DecimalField(
        max_digits=10, decimal_places=4, validators=[MinValueValidator(0)]
    )
    is_public = models.BooleanField(
        default=False, 
        help_text="Allow other users/experiments to access this configuration"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="radar_configurations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Experiment(models.Model):
    """
    In This Models:
        owner => User.
        configuration => RadarConfiguration.
        Snapshot preserves the parameters used for that run.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=112)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    configuration = models.ForeignKey(
        RadarConfiguration,
        on_delete=models.RESTRICT,
        related_name='experiments'
    )
    configuration_snapshot = models.JSONField(
        default=dict,
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="experiments"
    )

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"


class DetectionResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_label = models.CharField(max_length=112)
    range_m = models.DecimalField(
        max_digits=12, 
        decimal_places=9,
        validators=[MinValueValidator(0)]
    )
    radial_velocity_mps = models.DecimalField(
        max_digits=12, 
        decimal_places=9,
    )
    azimuth_deg = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        null=True,
        blank=True,
    )
    
    elevation_deg = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        null=True,
        blank=True,
    )
    confidence = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    experiment = models.ForeignKey(
        Experiment, 
        on_delete=models.CASCADE, 
        related_name='detections'
    )

    detected_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.target_label} | Range: {self.range_m} | Velocity: {self.radial_velocity_mps}m/s"