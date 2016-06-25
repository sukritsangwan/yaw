from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import django_filters
from django.db.models import signals


class Candidate(models.Model):
    with_resume = models.BooleanField(verbose_name="Resume (Yes/No)")
    name = models.CharField(verbose_name="Name of the Candidate", max_length=200)
    mobile = models.CharField(verbose_name="Mobile No", max_length=14)
    email = models.EmailField(verbose_name="Email address")
    work_exp = models.FloatField(verbose_name="Work Experience")
    analytics_exp = models.FloatField(verbose_name="Experience in Analytics")
    current_location = models.CharField(max_length=200, verbose_name="Current Location")
    corrected_location = models.CharField(max_length=200, verbose_name="Corrected Location")
    nearest_city = models.CharField(max_length=200, verbose_name="Nearest City")
    preferred_location = models.CharField(max_length=200, verbose_name="Preferred Location", blank=True)
    ctc = models.FloatField(verbose_name="CTC", blank=True)
    current_employer = models.CharField(max_length=200, verbose_name="Current Employer", blank=True)
    current_designation = models.CharField(max_length=200, verbose_name="Current Designation", blank=True)
    skills = models.CharField(max_length=200, blank=True)
    ug_course = models.CharField(max_length=200, verbose_name="U.G. Course", blank=True)
    ug_course_corrected = models.CharField(max_length=200, verbose_name="Corrected U.G. Course", blank=True)
    ug_institute = models.CharField(max_length=200, verbose_name="U.G. Institute Name", blank=True)
    ug_trier_1 = models.BooleanField(verbose_name="Trier 1")
    ug_passing_year = models.CharField(max_length=200, verbose_name="U.G. Passing year", blank=True)
    pg_course = models.CharField(max_length=200, verbose_name="P.G. Course", blank=True)
    pg_course_corrected = models.CharField(max_length=200, verbose_name="Corrected P.G. Course", blank=True)
    pg_institute = models.CharField(max_length=200, verbose_name="P.G. Institute Name", blank=True)
    pg_trier_1 = models.BooleanField(verbose_name="Trier 1")
    pg_passing_year = models.CharField(max_length=200, verbose_name="P.G. Passing year", blank=True)
    post_pg_course = models.CharField(max_length=200, verbose_name="Post PG Course", blank=True)
    post_pg_course_corrected = models.CharField(max_length=200, verbose_name="Corrected Post PG Course", blank=True)


class CandidateFilter(django_filters.FilterSet):
    """
    To filter out the candidates
    using the package django_filters
    """
    with_resume = django_filters.BooleanFilter(label="Resume Available")
    work_exp__gte = django_filters.NumberFilter(name='work_exp', lookup_expr='gte', label="Min Work Experience")
    work_exp__lte = django_filters.NumberFilter(name='work_exp', lookup_expr='lte', label="Max Work Experience")
    analytics_exp__gte = django_filters.NumberFilter(name='analytics_exp', lookup_expr='gte', label="Min Analytics Experience")
    ctc__lte = django_filters.NumberFilter(name='ctc', lookup_expr='lte', label="Max CTC")

    class Meta:
        model = Candidate
        fields = {
            'skills': ['icontains'],
            'preferred_location': ['icontains'],
            'ug_institute': ['icontains'],
        }


class UserProfile(models.Model):
    """
    To save information about the number of daily downloads by a recruiter,
    and to limit it, we use following fields
    """
    user = models.OneToOneField(User)
    last_profile_download = models.DateTimeField(default=timezone.now)
    daily_download_count = models.IntegerField(default=0)
    daily_download_limit = models.IntegerField(default=settings.DAILY_DOWNLOAD_LIMIT)


# trigger user profile creation on user creation
def handle_user_save(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
signals.post_save.connect(handle_user_save, sender=User)
