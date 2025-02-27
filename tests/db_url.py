from peewee import *
from playhouse.db_url import connect
from playhouse.db_url import parse

from .base import BaseTestCase


class TestDBUrl(BaseTestCase):
    def test_db_url_parse(self):
        cfg = parse('mysql://usr:pwd@hst:123/db')
        self.assertEqual(cfg['user'], 'usr')
        self.assertEqual(cfg['passwd'], 'pwd')
        self.assertEqual(cfg['host'], 'hst')
        self.assertEqual(cfg['database'], 'db')
        self.assertEqual(cfg['port'], 123)
        cfg = parse('postgresql://usr:pwd@hst/db')
        self.assertEqual(cfg['password'], 'pwd')
        cfg = parse('mysql+pool://usr:pwd@hst:123/db'
                    '?max_connections=42&stale_timeout=8001.2&zai=&baz=3.4.5'
                    '&boolz=false')
        self.assertEqual(cfg['user'], 'usr')
        self.assertEqual(cfg['password'], 'pwd')
        self.assertEqual(cfg['host'], 'hst')
        self.assertEqual(cfg['database'], 'db')
        self.assertEqual(cfg['port'], 123)
        self.assertEqual(cfg['max_connections'], 42)
        self.assertEqual(cfg['stale_timeout'], 8001.2)
        self.assertEqual(cfg['zai'], '')
        self.assertEqual(cfg['baz'], '3.4.5')
        self.assertEqual(cfg['boolz'], False)

    def test_db_url_no_unquoting(self):
        # By default, neither user nor password is not unescaped.
        cfg = parse('mysql://usr%40example.com:pwd%23@hst:123/db')
        self.assertEqual(cfg['user'], 'usr%40example.com')
        self.assertEqual(cfg['passwd'], 'pwd%23')
        self.assertEqual(cfg['host'], 'hst')
        self.assertEqual(cfg['database'], 'db')
        self.assertEqual(cfg['port'], 123)

    def test_db_url_quoted_password(self):
        cfg = parse('mysql://usr:pwd%23%20@hst:123/db', unquote_password=True)
        self.assertEqual(cfg['user'], 'usr')
        self.assertEqual(cfg['passwd'], 'pwd# ')
        self.assertEqual(cfg['host'], 'hst')
        self.assertEqual(cfg['database'], 'db')
        self.assertEqual(cfg['port'], 123)

    def test_db_url_quoted_user(self):
        cfg = parse('mysql://usr%40example.com:p%40sswd@hst:123/db', unquote_user=True)
        self.assertEqual(cfg['user'], 'usr@example.com')
        self.assertEqual(cfg['passwd'], 'p%40sswd')
        self.assertEqual(cfg['host'], 'hst')
        self.assertEqual(cfg['database'], 'db')
        self.assertEqual(cfg['port'], 123)

    def test_db_url(self):
        db = connect('sqlite:///:memory:')
        self.assertTrue(isinstance(db, SqliteDatabase))
        self.assertEqual(db.database, ':memory:')

        db = connect('sqlite:///:memory:', pragmas=(
            ('journal_mode', 'MEMORY'),))
        self.assertTrue(('journal_mode', 'MEMORY') in db._pragmas)

        #db = connect('sqliteext:///foo/bar.db')
        #self.assertTrue(isinstance(db, SqliteExtDatabase))
        #self.assertEqual(db.database, 'foo/bar.db')

        db = connect('sqlite:////this/is/absolute.path')
        self.assertEqual(db.database, '/this/is/absolute.path')

        db = connect('sqlite://')
        self.assertTrue(isinstance(db, SqliteDatabase))
        self.assertEqual(db.database, ':memory:')

        db = connect('sqlite:///test.db?p1=1?a&p2=22&p3=xyz')
        self.assertTrue(isinstance(db, SqliteDatabase))
        self.assertEqual(db.database, 'test.db')
        self.assertEqual(db.connect_params, {
            'p1': '1?a', 'p2': 22, 'p3': 'xyz'})

    def test_bad_scheme(self):
        def _test_scheme():
            connect('missing:///')

        self.assertRaises(RuntimeError, _test_scheme)
