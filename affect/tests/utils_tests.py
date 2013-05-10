from django.contrib.auth.models import AnonymousUser, User, Group
from django.core.cache import cache
from django.test import TestCase
from django.test.client import RequestFactory
import mox

from affect import utils
from affect.models import Criteria, Flag
from affect.utils import (cache_criteria, meets_criteria, random,
                          set_persist_criteria, uncache_criteria)


class CacheCriteriaTest(TestCase):
    def setUp(self):
        self.crit = Criteria.objects.create(name='test_crit')
        self.crit.flags.add(Flag.objects.create(name='test_flag'))
        self.crit.users.add(User.objects.create(username='test_user'))
        self.crit.groups.add(Group.objects.create(name='test_group'))
        self.mock = mox.Mox()
        self.mock.StubOutWithMock(cache, 'add')

    def tearDown(self):
        self.mock.UnsetStubs()

    def test_cache(self):
        cache.add('criteria:test_crit', self.crit)
        cache.add('criteria:test_crit:flags',
                  mox.SameElementsAs(self.crit.flags.all()))
        cache.add('criteria:test_crit:users',
                  mox.SameElementsAs(self.crit.users.all()))
        cache.add('criteria:test_crit:groups',
                  mox.SameElementsAs(self.crit.groups.all()))

        self.mock.ReplayAll()
        cache_criteria(instance=self.crit)
        self.mock.VerifyAll()

    def test_cache_w_other_action(self):
        self.mock.ReplayAll()
        cache_criteria(instance=self.crit, action='pre_add')
        self.mock.VerifyAll()


class MeetsCriteriaTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('')
        self.request.user = AnonymousUser()
        self.crit = Criteria.objects.create(name='test_crit')
        self.mock = mox.Mox()

    def tearDown(self):
        self.mock.UnsetStubs()

    def test_meets_nothing(self):
        self.mock.StubOutWithMock(cache, 'get')
        cache.get('criteria:test_crit')
        cache.get('criteria:test_crit:users')
        cache.get('criteria:test_crit:groups')
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # criteria
        utils.cache_criteria(instance=self.crit)  # users
        utils.cache_criteria(instance=self.crit)  # groups

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)
        self.mock.VerifyAll()

    def test_criteria_cached(self):
        self.mock.StubOutWithMock(cache, 'get')
        cache.get('criteria:test_crit').AndReturn(self.crit)
        cache.get('criteria:test_crit:users')
        cache.get('criteria:test_crit:groups')
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # users
        utils.cache_criteria(instance=self.crit)  # groups

        self.mock.ReplayAll()
        meets_criteria(self.request, 'test_crit')
        self.mock.VerifyAll()

    def test_criteria_doesnt_exist(self):
        self.assertIs(
            meets_criteria(self.request, 'fake_crit'), False)

    def test_on_for_everyone(self):
        self.crit.everyone = True
        self.crit.save()

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_off_for_everyone(self):
        self.crit.everyone = False
        self.crit.save()

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)

    def test_testing_force_on(self):
        self.crit.testing = True
        self.crit.save()
        self.request = RequestFactory().get('', {'dact_test_crit': 1})

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.assertIs(self.request.affected_tests['test_crit'], True)

    def test_testing_force_off(self):
        self.crit.testing = True
        self.crit.save()
        self.request = RequestFactory().get('', {'dact_test_crit': 0})

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)
        self.assertIs(self.request.affected_tests['test_crit'], False)

    def test_testing_cookie_on(self):
        self.crit.testing = True
        self.crit.save()
        self.request.COOKIES['dact_test_crit'] = 'True'

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_testing_cookie_off(self):
        self.crit.testing = True
        self.crit.save()
        self.request.COOKIES['dact_test_crit'] = 'False'

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)

    def test_authenticated_user(self):
        self.crit.authenticated = True
        self.crit.save()
        self.request.user = User.objects.create(username='test_user')

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_nonauthenticated_user(self):
        self.crit.authenticated = True
        self.crit.save()

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)

    def test_staff_user(self):
        self.crit.staff = True
        self.crit.save()
        self.request.user = User.objects.create(
            username='test_user', is_staff=True)

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_superuser(self):
        self.crit.superuser = True
        self.crit.save()
        self.request.user = User.objects.create(
            username='test_user', is_superuser=True)

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_user_in_users(self):
        self.request.user = User.objects.create(
            username='test_user')
        self.crit.users.add(self.request.user)
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # criteria
        utils.cache_criteria(instance=self.crit)  # users

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_user_in_cached_users(self):
        self.request.user = User.objects.create(
            username='test_user')
        self.crit.users.add(self.request.user)
        self.mock.StubOutWithMock(cache, 'get')
        cache.get('criteria:test_crit')
        cache.get('criteria:test_crit:users').AndReturn([self.request.user])
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # criteria

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_user_in_groups(self):
        self.request.user = User.objects.create(
            username='test_user')
        group = Group.objects.create(name='test_group')
        self.request.user.groups.add(group)
        self.crit.groups.add(group)
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # criteria
        utils.cache_criteria(instance=self.crit)  # users
        utils.cache_criteria(instance=self.crit)  # group

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_user_in_cached_groups(self):
        self.request.user = User.objects.create(
            username='test_user')
        group = Group.objects.create(name='test_group')
        self.request.user.groups.add(group)
        self.crit.groups.add(group)
        self.mock.StubOutWithMock(cache, 'get')
        cache.get('criteria:test_crit')
        cache.get('criteria:test_crit:users')
        cache.get('criteria:test_crit:groups').AndReturn([group])
        self.mock.StubOutWithMock(utils, 'cache_criteria')
        utils.cache_criteria(instance=self.crit)  # criteria
        utils.cache_criteria(instance=self.crit)  # users

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_percent_on(self):
        self.crit.percent = 50
        self.crit.save()
        self.mock.StubOutWithMock(random, 'uniform')
        random.uniform(0, 100).AndReturn(20)
        self.mock.StubOutWithMock(utils, 'set_persist_criteria')
        utils.set_persist_criteria(self.request, 'test_crit', True)

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_percent_off(self):
        self.crit.percent = 50
        self.crit.save()
        self.mock.StubOutWithMock(random, 'uniform')
        random.uniform(0, 100).AndReturn(99)
        self.mock.StubOutWithMock(utils, 'set_persist_criteria')
        utils.set_persist_criteria(self.request, 'test_crit', False)

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)
        self.mock.VerifyAll()

    def test_percent_cookie_on(self):
        self.crit.percent = 50
        self.crit.save()
        self.request.COOKIES['dac_test_crit'] = 'True'
        self.mock.StubOutWithMock(random, 'uniform')
        self.mock.StubOutWithMock(utils, 'set_persist_criteria')
        utils.set_persist_criteria(self.request, 'test_crit', True)

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()

    def test_percent_cookie_off(self):
        self.crit.percent = 50
        self.crit.save()
        self.request.COOKIES['dac_test_crit'] = 'False'
        self.mock.StubOutWithMock(random, 'uniform')
        self.mock.StubOutWithMock(utils, 'set_persist_criteria')
        utils.set_persist_criteria(self.request, 'test_crit', False)

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), False)
        self.mock.VerifyAll()

    def test_entry_url(self):
        self.crit.entry_url = '/test.html'
        self.crit.save()
        self.request.path = '/test.html'
        self.request.META['HTTP_REFERER'] = 'http://example.com/blah'
        self.request.META['HTTP_HOST'] = 'testserver.com'

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_entry_url_nonentry_domain(self):
        with self.settings(AFFECTED_NONENETRY_DOMAINS=['example.com']):
            self.crit.entry_url = '/test.html'
            self.crit.save()
            self.request.path = '/test.html'
            self.request.META['HTTP_REFERER'] = 'http://example.com/blah'
            self.request.META['HTTP_HOST'] = 'testserver.com'

            self.assertIs(
                meets_criteria(self.request, 'test_crit'), False)

    def test_referrer(self):
        self.crit.referrer = 'example.com,www.example.com'
        self.crit.save()
        self.request.META['HTTP_REFERER'] = 'http://example.com/blah'

        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)

    def test_query_args_exact_match(self):
        self.crit.query_args = {'foo': 'bar'}
        self.crit.save()
        request = RequestFactory().get('', {'foo': 'bar'})
        request.user = AnonymousUser()

        self.assertIs(
            meets_criteria(request, 'test_crit'), True)

    def test_query_args_exact_no_match(self):
        self.crit.query_args = {'foo': 'bar'}
        self.crit.save()
        request = RequestFactory().get('', {'foo': 'baz'})
        request.user = AnonymousUser()

        self.assertIs(
            meets_criteria(request, 'test_crit'), False)

    def test_query_args_any_for_key(self):
        self.crit.query_args = {'foo': '*'}
        self.crit.save()
        request = RequestFactory().get('', {'foo': 'bar'})
        request.user = AnonymousUser()

        self.assertIs(
            meets_criteria(request, 'test_crit'), True)

    def test_query_args_in_list(self):
        self.crit.query_args = {'foo': ['bar', 'baz']}
        self.crit.save()
        request = RequestFactory().get('', {'foo': 'bar'})
        request.user = AnonymousUser()

        self.assertIs(
            meets_criteria(request, 'test_crit'), True)

    def test_query_args_not_in_list(self):
        self.crit.query_args = {'foo': ['bar', 'baz']}
        self.crit.save()
        request = RequestFactory().get('', {'foo': 'boz'})
        request.user = AnonymousUser()

        self.assertIs(
            meets_criteria(request, 'test_crit'), False)


class SetPersistCriteriaTest(TestCase):
    def test_persist(self):
        request = RequestFactory().get('')
        set_persist_criteria(request, 'test_crit', False)
        self.assertDictEqual(request.affect_persist, {'test_crit': False})

    def test_persist_w_existing_persists(self):
        request = RequestFactory().get('')
        request.affect_persist = {'other_crit': True}
        set_persist_criteria(request, 'test_crit', False)
        self.assertDictEqual(
            request.affect_persist, {'other_crit': True, 'test_crit': False})


class UncacheCriteriaTest(TestCase):
    def test_uncache(self):
        criteria = Criteria.objects.create(name='test_crit')
        mock = mox.Mox()
        mock.StubOutWithMock(cache, 'set_many')
        cache.set_many({
            'criteria:test_crit:users': None,
            'criteria:test_crit:flags': None,
            'criteria:all': None,
            'criteria:test_crit': None,
            'criteria:test_crit:groups': None}, 5)

        mock.ReplayAll()
        uncache_criteria(instance=criteria)
        mock.VerifyAll()
        mock.UnsetStubs()
