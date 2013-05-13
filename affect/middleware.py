from django.core.cache import cache
from django.utils.encoding import smart_str

from .models import Criteria
from .utils import (ALL_CRITERIA_KEY, CRITERIA_FLAGS_KEY, FLAG_CONFLICTS_KEY,
                    cache_criteria, meets_criteria, settings)


class AffectMiddleware(object):
    def process_request(self, request):
        request.affected_persist = {}
        flags = {}

        all_criteria = cache.get(ALL_CRITERIA_KEY)
        if all_criteria is None:
            all_criteria = Criteria.objects.all()
            cache.add(ALL_CRITERIA_KEY, all_criteria)

        for criteria in all_criteria:
            criteria_cookie = request.COOKIES.get(
                settings.AFFECTED_COOKIE % criteria.name, '')
            if criteria_cookie and criteria.persistent:
                active = criteria_cookie == 'True'
            else:
                active = meets_criteria(request, criteria)

            if criteria.persistent:
                request.affected_persist[criteria] = active

            if active:
                criteria_flags = cache.get(CRITERIA_FLAGS_KEY % criteria.name)
                if criteria_flags is None:
                    criteria_flags = criteria.flags.filter(active=True)
                    cache_criteria(instance=criteria)
                for flag in criteria_flags:
                    flags[flag.name] = flag

        for name, flag in flags.items():
            flag_conflicts = cache.get(FLAG_CONFLICTS_KEY % name)
            if flag_conflicts is None:
                flag_conflicts = flag.conflicts.filter(
                    active=True, priority__gte=flag.priority)
                cache.add(FLAG_CONFLICTS_KEY % name, flag_conflicts)
            for conflict in flag_conflicts:
                if conflict in flags.values():
                    flags.pop(name)

        request.affected_flags = flags.keys()

    def process_response(self, request, response):
        secure = getattr(settings, 'AFFECTED_SECURE_COOKIE', False)

        for criteria, active in request.affected_persist.items():
            name = smart_str(settings.AFFECTED_COOKIE % criteria.name)
            if criteria.max_cookie_age:
                age = criteria.max_cookie_age
            else:
                age = None
            response.set_cookie(name, value=active, max_age=age, secure=secure)

        if hasattr(request, 'affected_tests'):
            for criteria, active in request.affected_tests.items():
                name = smart_str(
                    settings.AFFECTED_TESTING_COOKIE % criteria.name)
                if criteria.max_cookie_age:
                    age = criteria.max_cookie_age
                else:
                    age = None
                response.set_cookie(
                    name, value=active, max_age=age, secure=secure)

        return response
