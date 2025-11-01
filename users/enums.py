from django.db import models

class JobStatus(models.TextChoices):
    PROBATION = "Probation", "Probation"
    PERMANENT = "Permanent", "Permanent"
    PART_TIME = "Part-time", "Part-time"
    FULL_TIME = "Full-time", "Full-time"

class Status(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'

class DayOfWeek(models.TextChoices):
    MONDAY = "Monday", "Monday"
    TUESDAY = "Tuesday", "Tuesday"
    WEDNESDAY = "Wednesday", "Wednesday"
    THURSDAY = "Thursday", "Thursday"
    FRIDAY = "Friday", "Friday"
    SATURDAY = "Saturday", "Saturday"
    SUNDAY = "Sunday", "Sunday"
class LeaveStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    APPROVED = "Approved", "Approved"
    REJECTED = "Rejected", "Rejected"

JOB_STATUS_CHOICES = [
    ('PUBLISHED', 'Published'),
    ('UNPUBLISHED', 'Unpublished')
]