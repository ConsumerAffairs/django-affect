from decimal import Decimal
from urlparse import urlparse
import random

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, m2m_changed

from .models import Criteria, Flag


settings.AFFECTED_COOKIE = getattr(settings, 'AFFECTED_COOKIE', 'dac_%s')
settings.AFFECTED_TESTING_COOKIE = getattr(
    settings, 'AFFECTED_TESTING_COOKIE', 'dact_%s')
settings.AFFECTED_NONENTRY_DOMAINS = getattr(
    settings, 'AFFECTED_NONENTRY_DOMAINS', [])
ALL_CRITERIA_KEY = 'criteria:all'
CRITERIA_KEY = 'criteria:%s'
CRITERIA_FLAGS_KEY = 'criteria:%s:flags'
CRITERIA_USERS_KEY = 'criteria:%s:users'
CRITERIA_GROUPS_KEY = 'criteria:%s:groups'
FLAG_CONFLICTS_KEY = 'flag_conflicts:%s'


def set_persist_criteria(request, criteria_name, active=True):
    """Set a criteria value on a request object."""
    if not hasattr(request, 'affect_persist'):
        request.affect_persist = {}
    request.affect_persist[criteria_name] = active


def meets_criteria(request, criteria_name):
    criteria = cache.get(CRITERIA_KEY % criteria_name)
    if criteria is None:
        try:
            criteria = Criteria.objects.get(name=criteria_name)
            cache_criteria(instance=criteria)
        except Criteria.DoesNotExist:
            return False

    if criteria.everyone:
        return True
    elif criteria.everyone is False:
        return False

    if criteria.testing:
        tc = settings.AFFECTED_TESTING_COOKIE % criteria_name
        if tc in request.GET:
            active = request.GET[tc] == '1'
            if not hasattr(request, 'affected_tests'):
                request.affected_tests = {}
            request.affected_tests[criteria_name] = active
            return active
        if tc in request.COOKIES:
            return request.COOKIES[tc] == 'True'

    user = request.user

    if criteria.authenticated and user.is_authenticated():
        return True

    if criteria.staff and user.is_staff:
        return True

    if criteria.superusers and user.is_superuser:
        return True

    referrer = urlparse(request.META.get('HTTP_REFERER', '')).hostname

    if criteria.referrer:
        criteria_referrers = criteria.referrer.split(',')
        if referrer in criteria_referrers:
            return True

    if criteria.entry_url:
        if (referrer != request.META.get('HTTP_HOST', '') and
                not referrer in settings.AFFECTED_NONENTRY_DOMAINS):
            urls = criteria.entry_url.split(',')
            if request.path in urls:
                return True

    if criteria.query_args:
        for k, v in criteria.query_args.items():
            req_arg = request.GET.get(k, '')
            if req_arg:
                if isinstance(v, list) and req_arg in v:
                    return True
                if v == req_arg or v == '*':
                    return True

    criteria_users = cache.get(CRITERIA_USERS_KEY % criteria_name)
    if criteria_users is None:
        criteria_users = criteria.users.all()
        cache_criteria(instance=criteria)
    if user in criteria_users:
        return True

    criteria_groups = cache.get(CRITERIA_GROUPS_KEY % criteria_name)
    if criteria_groups is None:
        criteria_groups = criteria.groups.all()
        cache_criteria(instance=criteria)
    user_groups = user.groups.all()
    for group in criteria_groups:
        if group in user_groups:
            return True

    if criteria.percent > 0:
        cookie = settings.AFFECTED_COOKIE % criteria
        if cookie in request.COOKIES:
            criteria_active = request.COOKIES[cookie] == 'True'
            set_persist_criteria(request, criteria_name, criteria_active)
            return criteria_active
        if Decimal(str(random.uniform(0, 100))) <= criteria.percent:
            set_persist_criteria(request, criteria_name, True)
            return True
        set_persist_criteria(request, criteria_name, False)
    return False


def cache_criteria(**kwargs):
    action = kwargs.get('action', None)
    if not action or action in ['post_add', 'post_remove', 'post_clear']:
        criteria = kwargs.get('instance')
        cache.add(CRITERIA_KEY % criteria, criteria)
        cache.add(CRITERIA_FLAGS_KEY % criteria, criteria.flags.all())
        cache.add(CRITERIA_USERS_KEY % criteria, criteria.users.all())
        cache.add(CRITERIA_GROUPS_KEY % criteria, criteria.groups.all())


def uncache_criteria(**kwargs):
    criteria = kwargs.get('instance')
    cache.set_many({
        CRITERIA_KEY % criteria.name: None,
        CRITERIA_FLAGS_KEY % criteria.name: None,
        CRITERIA_USERS_KEY % criteria.name: None,
        CRITERIA_GROUPS_KEY % criteria.name: None,
        ALL_CRITERIA_KEY: None}, 5)

post_save.connect(uncache_criteria, sender=Criteria,
                  dispatch_uid='save_criteria')
post_delete.connect(uncache_criteria, sender=Criteria,
                    dispatch_uid='delete_criteria')
m2m_changed.connect(uncache_criteria, sender=Criteria.users.through,
                    dispatch_uid='m2m_criteria_users')
m2m_changed.connect(uncache_criteria, sender=Criteria.groups.through,
                    dispatch_uid='m2m_criteria_groups')
m2m_changed.connect(uncache_criteria, sender=Criteria.flags.through,
                    dispatch_uid='m2m_criteria_flags')


def uncache_flag(**kwargs):
    flag = kwargs.get('instance')
    cache.set(FLAG_CONFLICTS_KEY % flag.name, None, 5)

    for criteria in flag.criteria_set.all():
        uncache_criteria(instance=criteria)

post_save.connect(uncache_flag, sender=Flag, dispatch_uid='save_flag')
post_delete.connect(uncache_flag, sender=Flag, dispatch_uid='delete_flag')
m2m_changed.connect(uncache_flag, sender=Flag.conflicts.through,
                    dispatch_uid='m2m_flag_conflicts')
