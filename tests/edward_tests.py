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
        elif args[0] == '//table[@class="attachment"]//a[@class="tooltip"]/attribute::href':
            return link_list

    def dummy_requests(self, s):
        return s

    def setup(self):
        self.scanner = edward.PostScanner('http://example.com')
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

    def test_get_page_images_iterator_good(self):
        #Index 0 because the function returns two vars, 0 is an iterator containing
        #tuple pairs of (image_name, relative_url)

        #TODO: verify if names in tuple are in correct order as original lists
        itered_links_and_pics = self.scanner.get_page_images(self.mock_page)[0]
        list_of_tuples = [i for i in itered_links_and_pics]
        assert_equal(len(list_of_tuples), 9)

        
       
    def test_make_post_list(self):
        pass

    def test_scan(self):
        pass

    def test_get_topics(self):
        pass

    def test_post_scraper(self):
        pass

