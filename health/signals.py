from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import DoctorPatientAssignment
from .models import HealthRecord
from .notifications import send_assignment_notification, send_health_record_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=DoctorPatientAssignment)
def notify_doctor_on_assignment(sender, instance, created, **kwargs):
    """Send notification when doctor is assigned to a patient"""
    if created and instance.is_active:
        try:
            send_assignment_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send assignment notification: {e}")

@receiver(post_save, sender=HealthRecord)
def notify_doctor_on_health_record(sender, instance, created, **kwargs):
    """Send notification for high/critical priority health records"""
    if created and instance.priority in ['high', 'critical']:
        try:
            send_health_record_notification(instance, "created")
        except Exception as e:
            logger.error(f"Failed to send health record notification: {e}")
