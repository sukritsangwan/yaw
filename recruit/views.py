# Create your views here.
import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

from recruit.models import CandidateFilter, Candidate


def get_candidate_filter(request):
    """
    Filter the candidates list

    If no filter is applied, nothing will be returned.
    :param request:
    :return:
    """
    qs = Candidate.objects.none()
    for k, v in request.GET.items():
        if len(v) > 0 and k in CandidateFilter.base_filters:
            qs = Candidate.objects.all()
            break
    return CandidateFilter(request.GET, queryset=qs)


@login_required(login_url='/login/')
def candidate_csv_download(request):
    """
    View to allow downloading csv of filtered candidates
    :param request:
    :return:
    """
    # find how many downloads are allowed today
    up = request.user.userprofile
    if up.last_profile_download.date() < timezone.now().date():
        today_download_count = 0
    else:
        today_download_count = up.daily_download_count

    # get filtered candidates
    f = get_candidate_filter(request)

    # create csv response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="candidates.csv"'

    writer = csv.writer(response)

    headers = []
    fields = []
    for field in f.queryset.model._meta.fields:
        fields.append(field.name)
        headers.append(field.verbose_name)
    writer.writerow(headers)
    for obj in f:
        # check if today's download limit
        if today_download_count >= up.daily_download_limit:
            writer.writerow(['You have reached your download limit for the day', ])
            break
        row = []
        for field in fields:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            row.append(val)
        writer.writerow(row)
        today_download_count += 1

    # update download_count
    up.daily_download_count = today_download_count
    up.last_profile_download = timezone.now()
    up.save()

    return response
