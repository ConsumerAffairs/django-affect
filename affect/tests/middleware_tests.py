from django.core.cache import cache
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
import mox

from affect import middleware
from affect.middleware import AffectMiddleware
from affect.models import Criteria, Flag


class AffectMiddlewareRequestTest(TestCase):
    def setUp(self):
        self.criteria = Criteria.objects.create(
            name='test_crit', max_cookie_age=0)
        self.flag1 = Flag.objects.create(name='test_flag', active=True)
        self.flag2 = Flag.objects.create(name='other_flag', active=True)
        self.criteria.flags.add(self.flag1, self.flag2)
        self.request = RequestFactory().get('')
        self.request.affected_persist = {}
        self.mw = AffectMiddleware()
        self.mock = mox.Mox()
        self.mock.StubOutWithMock(middleware, 'meets_criteria')
        self.mock.StubOutWithMock(cache, 'get')
        self.mock.StubOutWithMock(cache, 'add')

    def tearDown(self):
        self.mock.UnsetStubs()

    def test_criteria_active_nothing_cached(self):
        self.mock.StubOutWithMock(middleware, 'cache_criteria')
        cache.get('criteria:all')
        cache.add('criteria:all', mox.SameElementsAs(Criteria.objects.all()))
        middleware.meets_criteria(self.request, self.criteria).AndReturn(True)
        cache.get('criteria:test_crit:flags')
        middleware.cache_criteria(instance=self.criteria)
        cache.get(u'flag_conflicts:test_flag')
        cache.add(u'flag_conflicts:test_flag', mox.SameElementsAs([]))
        cache.get(u'flag_conflicts:other_flag')
        cache.add(u'flag_conflicts:other_flag', mox.SameElementsAs([]))

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(self.request.affected_persist, {})
        self.assertListEqual(self.request.affected_flags,
                             [self.flag1.name, self.flag2.name])

    def test_criteria_active_everything_cached(self):
        self.mock.StubOutWithMock(middleware, 'cache_criteria')
        cache.get('criteria:all').AndReturn(Criteria.objects.all())
        middleware.meets_criteria(self.request, self.criteria).AndReturn(True)
        cache.get('criteria:test_crit:flags').AndReturn(
            self.criteria.flags.all())
        cache.get(u'flag_conflicts:test_flag').AndReturn(Flag.objects.none())
        cache.get(u'flag_conflicts:other_flag').AndReturn(Flag.objects.none())

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(self.request.affected_persist, {})
        self.assertItemsEqual(self.request.affected_flags,
                             [self.flag1.name, self.flag2.name])

    def test_criteria_not_active(self):
        middleware.meets_criteria(self.request, self.criteria).AndReturn(False)
        cache.get('criteria:all')
        cache.add('criteria:all', mox.IgnoreArg())

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(self.request.affected_persist, {})
        self.assertListEqual(self.request.affected_flags, [])

    def test_persistent_wo_cookie(self):
        self.criteria.persistent = True
        self.criteria.save()
        middleware.meets_criteria(self.request, self.criteria).AndReturn(True)
        cache.get('criteria:all')
        cache.add('criteria:all', mox.IgnoreArg())
        cache.get('criteria:test_crit:flags')
        cache.add('criteria:test_crit', mox.IgnoreArg())
        cache.add('criteria:test_crit:flags', mox.IgnoreArg())
        cache.add('criteria:test_crit:users', mox.IgnoreArg())
        cache.add('criteria:test_crit:groups', mox.IgnoreArg())
        cache.get('flag_conflicts:other_flag').InAnyOrder()
        cache.get('flag_conflicts:test_flag').InAnyOrder()
        cache.add('flag_conflicts:test_flag', mox.IgnoreArg()).InAnyOrder()
        cache.add('flag_conflicts:other_flag', mox.IgnoreArg()).InAnyOrder()

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(
            self.request.affected_persist, {self.criteria: True})
        self.assertItemsEqual(
            self.request.affected_flags, [self.flag1.name, self.flag2.name])

    def test_persistent_w_cookie(self):
        self.request.COOKIES['dac_test_crit'] = 'True'
        self.criteria.persistent = True
        self.criteria.save()
        cache.get('criteria:all')
        cache.add('criteria:all', mox.IgnoreArg())
        cache.get('criteria:test_crit:flags')
        cache.add('criteria:test_crit', mox.IgnoreArg())
        cache.add('criteria:test_crit:flags', mox.IgnoreArg())
        cache.add('criteria:test_crit:users', mox.IgnoreArg())
        cache.add('criteria:test_crit:groups', mox.IgnoreArg())
        cache.get('flag_conflicts:other_flag').InAnyOrder()
        cache.get('flag_conflicts:test_flag').InAnyOrder()
        cache.add('flag_conflicts:test_flag', mox.IgnoreArg()).InAnyOrder()
        cache.add('flag_conflicts:other_flag', mox.IgnoreArg()).InAnyOrder()

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(
            self.request.affected_persist, {self.criteria: True})
        self.assertItemsEqual(
            self.request.affected_flags, [self.flag1.name, self.flag2.name])

    def test_flag_conflicts(self):
        middleware.meets_criteria(self.request, self.criteria).AndReturn(True)
        self.flag2.conflicts.add(self.flag1)
        self.flag2.priority = 100
        self.flag2.save()
        cache.get('criteria:all')
        cache.add('criteria:all', mox.IgnoreArg())
        cache.get('criteria:test_crit:flags')
        cache.add('criteria:test_crit', mox.IgnoreArg())
        cache.add('criteria:test_crit:flags', mox.IgnoreArg())
        cache.add('criteria:test_crit:users', mox.IgnoreArg())
        cache.add('criteria:test_crit:groups', mox.IgnoreArg())
        cache.get('flag_conflicts:other_flag').InAnyOrder()
        cache.get('flag_conflicts:test_flag').InAnyOrder()
        cache.add('flag_conflicts:test_flag', mox.IgnoreArg()).InAnyOrder()
        cache.add('flag_conflicts:other_flag', mox.IgnoreArg()).InAnyOrder()

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(
            self.request.affected_persist, {})
        self.assertItemsEqual(
            self.request.affected_flags, [self.flag2.name])

    def test_flag_conflict_not_in_criteria(self):
        middleware.meets_criteria(self.request, self.criteria).AndReturn(True)
        flag3 = Flag.objects.create(name='that_flag', priority=100)
        flag3.conflicts.add(self.flag1, self.flag2)
        cache.get('criteria:all')
        cache.add('criteria:all', mox.IgnoreArg())
        cache.get('criteria:test_crit:flags')
        cache.add('criteria:test_crit', mox.IgnoreArg())
        cache.add('criteria:test_crit:flags', mox.IgnoreArg())
        cache.add('criteria:test_crit:users', mox.IgnoreArg())
        cache.add('criteria:test_crit:groups', mox.IgnoreArg())
        cache.get('flag_conflicts:other_flag').InAnyOrder()
        cache.get('flag_conflicts:test_flag').InAnyOrder()
        cache.add('flag_conflicts:test_flag', mox.IgnoreArg()).InAnyOrder()
        cache.add('flag_conflicts:other_flag', mox.IgnoreArg()).InAnyOrder()

        self.mock.ReplayAll()
        self.mw.process_request(self.request)
        self.mock.VerifyAll()

        self.assertDictEqual(
            self.request.affected_persist, {})
        self.assertItemsEqual(
            self.request.affected_flags, [self.flag1.name, self.flag2.name])


class AffectMiddlewareResponseTest(TestCase):
    def setUp(self):
        self.criteria = Criteria.objects.create(
            name='test_crit', max_cookie_age=0)
        self.request = RequestFactory().get('')
        self.request.affected_persist = {}
        self.response = HttpResponse('test response')
        self.mw = AffectMiddleware()
        self.mock = mox.Mox()

    def tearDown(self):
        self.mock.UnsetStubs()

    def test_persist_cookie(self):
        self.request.affected_persist[self.criteria] = True
        self.mock.StubOutWithMock(self.response, 'set_cookie')
        self.response.set_cookie(
            'dac_test_crit', value=True, max_age=None, secure=False)

        self.mock.ReplayAll()
        resp = self.mw.process_response(self.request, self.response)
        self.mock.VerifyAll()

        self.assertEqual(resp.content, 'test response')

    def test_persist_cookie_with_max_age(self):
        self.criteria.max_cookie_age = 1200
        self.request.affected_persist[self.criteria] = False
        self.mock.StubOutWithMock(self.response, 'set_cookie')
        self.response.set_cookie(
            'dac_test_crit', value=False, max_age=1200, secure=False)

        self.mock.ReplayAll()
        resp = self.mw.process_response(self.request, self.response)
        self.mock.VerifyAll()

        self.assertEqual(resp.content, 'test response')

    def test_testing_cookie(self):
        self.request.affected_tests = {self.criteria: True}
        self.mock.StubOutWithMock(self.response, 'set_cookie')
        self.response.set_cookie(
            'dact_test_crit', value=True, max_age=None, secure=False)

        self.mock.ReplayAll()
        resp = self.mw.process_response(self.request, self.response)
        self.mock.VerifyAll()

        self.assertEqual(resp.content, 'test response')

    def test_testing_cookie_with_max_age(self):
        self.criteria.max_cookie_age = 1200
        self.request.affected_tests = {self.criteria: False}
        self.mock.StubOutWithMock(self.response, 'set_cookie')
        self.response.set_cookie(
            'dact_test_crit', value=False, max_age=1200, secure=False)

        self.mock.ReplayAll()
        resp = self.mw.process_response(self.request, self.response)
        self.mock.VerifyAll()

        self.assertEqual(resp.content, 'test response')
