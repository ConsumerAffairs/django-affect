from django.test import TestCase
import mox

from affect.models import Criteria, Flag, datetime


class CriteriaModelTest(TestCase):
    def test_unicode(self):
        crit = Criteria.objects.create(name='test_crit')
        self.assertEqual(unicode(crit), 'test_crit')

    def test_save_updates_modified(self):
        crit = Criteria.objects.create(name='test_crit')
        mock = mox.Mox()
        mock.StubOutWithMock(datetime, 'now')
        datetime.now().AndReturn(datetime.datetime(2012, 1, 1))

        mock.ReplayAll()
        crit.save()
        mock.VerifyAll()
        mock.UnsetStubs()

        crit = Criteria.objects.get(id=crit.id)
        self.assertEqual(crit.modified, datetime.datetime(2012, 1, 1))


class FlagModelTest(TestCase):
    def test_unicode(self):
        flag = Flag.objects.create(name='test_flag')
        self.assertEqual(unicode(flag), 'test_flag')

    def test_save_updates_modified(self):
        flag = Flag.objects.create(name='test_flag')
        mock = mox.Mox()
        mock.StubOutWithMock(datetime, 'now')
        datetime.now().AndReturn(datetime.datetime(2012, 1, 1))

        mock.ReplayAll()
        flag.save()
        mock.VerifyAll()
        mock.UnsetStubs()

        flag = Flag.objects.get(id=flag.id)
        self.assertEqual(flag.modified, datetime.datetime(2012, 1, 1))
