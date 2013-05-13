from django.contrib.auth.models import AnonymousUser, User, Group
from django.core.cache import cache
from django.test import TestCase
from django.test.client import RequestFactory
import mox

from affect import utils
from affect.models import Criteria, Flag
from affect.utils import (
    cache_criteria, detect_device, flag_is_affected, meets_criteria, random,
    set_persist_criteria, uncache_criteria, uncache_flag)


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


class DetectDeviceTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('')

    def test_iphone_mobile(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'UCWEB/8.8 (iPhone; CPU OS_6; en-US)AppleWebKit/534.1 U3/3.0.0 '
            'Mobile')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_ipad_mobile(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 '
            '(KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_ipod_mobile(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (iPod; U; CPU iPhone OS 3_1_1 like Mac OS X; en-us) '
            'AppleWebKit/528.18 (KHTML, like Gecko) Mobile/7C145')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_android_mobile(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (Linux; Android 4.2.2; Galaxy Nexus Build/JDQ39) '
            'AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.58 Mobile'
            ' Safari/537.31')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_android_tablet(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (Linux; Android 4.2.2; Nexus 7 Build/JDQ39) '
            'AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.58 '
            'Safari/537.31')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_no_user_agent(self):
        self.assertEqual(detect_device(self.request), Criteria.DESKTOP_DEVICE)

    def test_desktop(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 '
            'Firefox/20.0')
        self.assertEqual(detect_device(self.request), Criteria.DESKTOP_DEVICE)

    def test_webos_mobile(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (webOS/1.3; U; en-US) AppleWebKit/525.27.1 (KHTML, '
            'like Gecko) Version/1.0 Safari/525.27.1 Desktop/1.0')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_windows_phone(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/'
            '5.0; IEMobile/9.0)')
        self.assertEqual(detect_device(self.request), Criteria.MOBILE_DEVICE)

    def test_opera_mini(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Opera/10.61 (J2ME/MIDP; Opera Mini/5.1.21219/19.999; en-US; '
            'rv:1.9.3a5) WebKit/534.5 Presto/2.6.30')
        self.assertEqual(detect_device(self.request), Criteria.SIMPLE_DEVICE)

    def test_wap_device(self):
        self.request.META['HTTP_USER_AGENT'] = (
            'Nokia6630/1.0 (2.3.129) SymbianOS/8.0 Series60/2.6 '
            'Profile/MIDP-2.0 Configuration/CLDC-1.1')
        self.request.META['HTTP_ACCEPT'] = 'application/vnd.wap.xhtml+xml'
        self.assertEqual(detect_device(self.request), Criteria.SIMPLE_DEVICE)


class FlagAffectedTest(TestCase):
    def test_active(self):
        request = RequestFactory().get('')
        request.affected_flags = ['test_flag']
        self.assertIs(flag_is_affected(request, 'test_flag'), True)
        self.assertIs(flag_is_affected(request, 'other_flag'), False)

    def test_affected_flags_missing(self):
        request = RequestFactory().get('')
        self.assertIs(flag_is_affected(request, 'test_flag'), False)


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
        with self.settings(AFFECTED_NONENTRY_DOMAINS=['example.com']):
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

    def test_device_type_active(self):
        self.crit.device_type = Criteria.MOBILE_DEVICE
        self.crit.save()

        self.mock.StubOutWithMock(utils, 'detect_device')
        utils.detect_device(self.request).AndReturn(Criteria.MOBILE_DEVICE)

        self.mock.ReplayAll()
        self.assertIs(
            meets_criteria(self.request, 'test_crit'), True)
        self.mock.VerifyAll()


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


class UncacheFlagTest(TestCase):
    def test_uncache(self):
        criteria = Criteria.objects.create(name='test_crit')
        flag = Flag.objects.create(name='test_flag')
        conflict = Flag.objects.create(name='nega-test_flag')
        flag.conflicts.add(conflict)
        criteria.flags.add(flag, conflict)
        mock = mox.Mox()
        mock.StubOutWithMock(cache, 'set')
        cache.set('flag_conflicts:test_flag', None, 5)
        mock.StubOutWithMock(utils, 'uncache_criteria')
        utils.uncache_criteria(instance=criteria)

        mock.ReplayAll()
        uncache_flag(instance=flag)
        mock.VerifyAll()
        mock.UnsetStubs()
