from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_assignment_notification(assignment):
    """Send email notification when doctor is assigned to patient"""
    try:
        subject = "New Patient Assignment"
        message = f"""
            Hello Dr. {assignment.doctor.user.full_name},

            You have been assigned to a new patient: {assignment.patient.user.full_name}.
            You can now view and annotate their health records through the system.

            Assignment details:
            - Patient: {assignment.patient.user.full_name}
            - Assigned by: {assignment.assigned_by.full_name if assignment.assigned_by else 'System'}
            - Date: {assignment.created.strftime('%Y-%m-%d %H:%M')}
            - Notes: {assignment.notes or 'No additional notes'}

            Please log in to the system to access the patient's records.

            Best regards,
            Health Record System
        """
        
        # Send email if email backend is configured
        if hasattr(settings, 'EMAIL_HOST_USER') and settings.EMAIL_HOST_USER:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[assignment.doctor.user.email],
                fail_silently=True,  # Don't break the app if email fails
            )
            logger.info(f"Assignment notification sent to {assignment.doctor.user.email}")
        else:
            # Log the notification if email is not configured
            logger.info(f"Assignment notification (email not configured): {subject}")
            
    except Exception as e:
        logger.error(f"Error sending assignment notification: {e}")

def send_health_record_notification(health_record, notification_type="created"):
    """Send notification for critical health records"""
    if health_record.priority not in ['high', 'critical']:
        return
        
    try:
        # Get assigned doctors
        assigned_doctors = health_record.patient.doctor_assignments.filter(is_active=True)
        
        for assignment in assigned_doctors:
            doctor = assignment.doctor.user
            
            subject = f"[{health_record.priority.upper()}] Health Record {notification_type.title()}"
            message = f"""
                Hello Dr. {doctor.full_name},

                A {health_record.priority} priority health record has been {notification_type}:

                Patient: {health_record.patient.user.full_name}
                Record Type: {health_record.get_record_type_display()}
                Title: {health_record.title}
                Priority: {health_record.get_priority_display()}
                Date: {health_record.date_of_record.strftime('%Y-%m-%d %H:%M')}

                Please review the record and add annotations if necessary.

                Best regards,
                Health Record System
            """
            
            if hasattr(settings, 'EMAIL_HOST_USER') and settings.EMAIL_HOST_USER:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[doctor.email],
                    fail_silently=True,
                )
                logger.info(f"Health record notification sent to {doctor.email}")
            else:
                logger.info(f"Health record notification (email not configured): {subject}")
                
    except Exception as e:
        logger.error(f"Error sending health record notification: {e}")
