from nose.tools import *
from lxml import etree
from nitro_py.nitro_py import results_total, pages_total, pid, fmt_mixins, fmt_kwargs

class TestParseResponse:
    def setup(self):
        self.page = open('tests/resources.xml', 'rt')
        self.page_infoset = etree.parse(self.page)
        self.clip = open('tests/clip.xml', 'rt')
        self.clip_infoset = etree.parse(self.clip)

    def test_results_total(self):
        assert_equal(results_total(self.page_infoset), 119668)

    def test_pages_total(self):
        assert_equal(pages_total(self.page_infoset, 100), 1197)

    def test_resources(self):
        # Testing this requires storing a lot of files on disk
        pass

    def test_pid(self):
        assert_equal(pid(self.clip_infoset), 'p02v33hl')

    def teardown(self):
        self.page.close()
        self.clip.close()

class TestGetResponse:
    def setup(self):
        self.mixins = ['ancestor_titles', 'contributions']
        self.kwargs = {'entity_type':'clip', 'availability':'available'}

    def test_fmt_mixins(self):
        assert_equal(fmt_mixins(self.mixins), '&mixin=ancestor_titles&mixin=contributions')

    def test_fmt_kwargs(self):
        assert_equal(fmt_kwargs(self.kwargs), '&availability=available&entity_type=clip')

    def teardown(self):
        pass