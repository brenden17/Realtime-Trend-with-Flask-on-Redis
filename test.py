import unittest

from resource import *


class ResourceTestCase(unittest.TestCase):
    def _setUp(self):
        self.NR = NewspaperRosource('abc', 'http://www.abc.com.au')

    def _test_fetch_article_url(self):
        self.NR.fetch_article_url()

    def _test_get_line(self):
        for l in self.NR.get_line():
            print l

    def _test_NewspaperRosource(self):
        nr = NewspaperRosource('abc', 'http://www.abc.com.au')
        for l in nr:
            print l

    def _test_NewspaperRosource_saved(self):
        nr = NewspaperRosource('abc', 'http://www.abc.com.au', save=True)
        # for l in nr:
        #     print l

    def test_NewspaperRosource_saved_no_fetch(self):
        nr = NewspaperRosource('abc', 'http://www.abc.com.au', fetch=True, save=True)
       

    def _test_model(self):
        create_model()

if __name__ == '__main__':
    unittest.main()