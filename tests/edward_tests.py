# -*- coding: utf-8 -*-
from nose.tools import *
import edward
import mock
from mock import patch

class edward_simple_tests(object):

    def setup(self):
        self.scanner = edward.PostScanner('http://example.com')

    def test_init(self):
        assert_equal(self.scanner.url, 'http://example.com')

    def test_check_date_good(self):
        dates = ['2010-01-20, 15:00:00', '1998-12-20, 9:38:23', '3 godziny temu', 'wczoraj, 12:00',
        '54 minuty temu', '14 minut temu', '23 sekundy temu', '15 sekund temu']
        for i in dates:
            assert_equal(self.scanner.check_date(i), True)

    def test_check_date_bad(self):
        dates = ['966-19-12, 14:00:20', '1998-5-24, 15:12:00', '2010-10-1, 12:00:00', '3 gopzin temu, 12:00',
        'parę godzin temu', 'widziałęm wczoraj', 'wiele godzin temu', 'duże godziny temu', 'wiele minut temu',
        'duże minuty temu']
        for i in dates:
            assert_equal(self.scanner.check_date(i), False)

    def test_check_img_good(self):
        imgs_strs = ['1225234.jpg', '192434.413941234.jpg', 'DSC00_1234.png', 'P140230.bmp']
        for i in imgs_strs:
            assert_equal(self.scanner.check_img(i), True)

    def test_check_img_bad(self):
        imgs_strs = ['format .jpg.', 'jako jpg', 'to są .gify']
        for i in imgs_strs:
            assert_equal(self.scanner.check_img(i), False)

class edward_get_page_images_tests(object):
    #Setup functions
    def page_mock_links_imgs(self, *args):
        img_list = ['DSCI1000.JPG', 'DSC98786.JPG', 'DSC0564132.JPG', 'DSC013654.JPG',
             'P1423954.JPG', 'DSCasda1324.JPG', u'sprzeda\xc5\xbc rzeczy 88.jpg', 
             u'sprzeda\xc5\xbc rzeczy.jpg', '654879.jpg']
        link_list = ['/pobierz-zalacznik/C66', '/pobierz-zalacznik/C6h', '/pobierz-zalacznik/C6i',
             '/pobierz-zalacznik/C6g', '/pobierz-zalacznik/C6f', '/pobierz-zalacznik/C6m',
              '/pobierz-zalacznik/C6W', '/pobierz-zalacznik/C6V', '/pobierz-zalacznik/C6U']

        if (args[0] == '//table[@class="attachment"]//a[@class="tooltip"]/img/attribute::alt'
        or args[0] == 'img_list'):
            return img_list
        elif (args[0] == '//table[@class="attachment"]//a[@class="tooltip"]/attribute::href'
            or args[0] == 'link_list'):
            return link_list
        else:
            raise ValueError('page_mock_links_imgs does not work with that argument')

    def dummy_requests(self, s):
        return s

    def setup(self):
        self.URL = 'http://example.com'
        self.scanner = edward.PostScanner(self.URL)
        self.mock_page = mock.Mock()
        self.mock_page.xpath.side_effect = self.page_mock_links_imgs
        #monkeypatching the requests.get call in edward with fake function defined above
        edward.requests.get = self.dummy_requests
    #End of setup functions

    #@patch('edward.requests.get', dummy_requests)
    def test_get_page_images_list_good(self):
        #Index 1 because the function returns two vars, 1 is a list of image names
        itered_links_and_pics = self.scanner.get_page_images(self.mock_page)[1]

        assert_equal(itered_links_and_pics, self.page_mock_links_imgs('img_list'))

    def test_get_page_images_iterator_good_count(self):
        #Index 0 because the function returns two vars, 0 is an iterator containing
        #tuple pairs of (image_name, relative_url)
        itered_links_and_pics = self.scanner.get_page_images(self.mock_page)[0]
        list_of_tuples = [i for i in itered_links_and_pics]
        assert_equal(len(list_of_tuples), 9)

    def test_get_page_images_iterator_good_order(self):
        itered_links_and_pics = self.scanner.get_page_images(self.mock_page)[0]
        list_of_tuples = [i for i in itered_links_and_pics]

        link_list = ['%s%s' % (self.URL, i) for i in self.page_mock_links_imgs('link_list')]
        img_list = self.page_mock_links_imgs('img_list')
        print img_list
        print list_of_tuples
        for i in xrange(len(list_of_tuples)):
            #check the tuple, index 0 being image file name, index 1 being the 
            #absolute url
            assert_equal(list_of_tuples[i][0], img_list[i])
            assert_equal(list_of_tuples[i][1], link_list[i])

class edward_get_topics_tests(object):

    def lxml_tree_mock(self, *args):
        t_links = ['/temat/468976/polecam-nowe-forum', '/temat/465987/witam-nowych', 
        '/temat/136645/put-no-monument', '/temat/107867/for-me-i-didnt', '/temat/5641326/it-in-life-and-i-dont',
         '/temat/136549/need-it-in', '/temat/546974/death', '/temat/651657/if-i-no-longer-serve', '/temat/654977/you-just-kiss-my',
          '/temat/5465798/my-ashes-goodbye']
        t_posts = ['23', '11', '95', '75', '23', '22', '4', '24', '22', '60']
        t_titles = [u'by the time you read this', u'i will already be dead', 
        'by the time you read this', 'i will already', u'be gone \xc4\x99 pick up the pieces \u2019', 'pieces', 'and throw them away',
         'do not reply to this', u'but realise what you have done\xc3\xb3w!', u'by the time you read this\xc3\xb3b ze \xc5\x9al']

        if args[0] == '//tr[@class="transp"]/td[1]/a/attribute::href | //tr[@class=" z_tlem"]/td[1]/a/attribute::href':
            return t_links
        elif args[0] == '//tr[@class="transp"]/td[2]/text() | //tr[@class=" z_tlem"]/td[2]/text()':
            return t_posts
        elif args[0] == '//tr[@class="transp"]/td[1]/a/text() | //tr[@class=" z_tlem"]/td[1]/a/text()':
            return t_titles
        else:
            raise ValueError('lxml_tree_mock does not work with that argument.')

    def setup(self):
        self.mock_topic_tree = mock.Mock()
        self.mock_topic_tree.xpath.side_effect = self.lxml_tree_mock

    def test_get_topics_tests_good(self):
        zipped = [('/temat/468976/polecam-nowe-forum', '23', u'by the time you read this'),
         ('/temat/465987/witam-nowych', '11', u'i will already be dead'),
          ('/temat/136645/put-no-monument', '95', 'by the time you read this'), ('/temat/107867/for-me-i-didnt', '75', 'i will already'),
           ('/temat/5641326/it-in-life-and-i-dont', '23', u'be gone \xc4\x99 pick up the pieces \u2019'),
            ('/temat/136549/need-it-in', '22', 'pieces'), ('/temat/546974/death', '4', 'and throw them away'),
             ('/temat/651657/if-i-no-longer-serve', '24', 'do not reply to this'),
              ('/temat/654977/you-just-kiss-my', '22', u'but realise what you have done\xc3\xb3w!'),
               ('/temat/5465798/my-ashes-goodbye', '60', u'by the time you read this\xc3\xb3b ze \xc5\x9al')]

        result = edward.get_topics(self.mock_topic_tree)
        assert_equal(result, zipped)

    #TODO: Finish off get_topics tests and think about make_post_list_tests


    def test_make_post_list(self):
        pass

    def test_scan(self):
        pass

    def test_post_scraper(self):
        pass

