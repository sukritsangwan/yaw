from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recruit.views import get_candidate_filter
from .models import Candidate, UserProfile

# Register your models here.
admin.site.register(Candidate)


class RecruiterAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the recruiter app.
    Copied from django admin, and removinf check for user.is_staff
    """
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class RecruiterAdminSite(AdminSite):
    login_form = RecruiterAuthenticationForm

    def has_permission(self, request):
        return request.user.is_active


class CandidateRecruiterAdmin(admin.ModelAdmin):
    """
    Restrict the recruiter site from adding, changing or deleting candidates
    It is intended that recruiter user will have change permission given by admin, but should not be able to edit anything
    """

    change_list_template = 'candidate_filter.html'

    def changelist_view(self, request, extra_context=None):
        f = get_candidate_filter(request)
        return render(request, self.change_list_template or 'candidate_filter.html', {'filter': f})

    def get_actions(self, request):
        actions = super(CandidateRecruiterAdmin, self).get_actions(request)
        # if not actions and request.user.has_perm('candidate.view'):
        #     actions = []
        return actions

    def save_model(self, request, obj, form, change):
        raise PermissionDenied

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


recruiter_site = RecruiterAdminSite(name='recruit')
recruiter_site.register(Candidate, CandidateRecruiterAdmin)


# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'userprofile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
