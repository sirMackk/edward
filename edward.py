from lxml import html
import requests
import re

#Edward,
#Will scour a specific forum and extract posts along with date, author, content
#and images and input that information into a database. Very handy if there
#is no way to export the data any other way.


#It's aim is to scan a page of posts and scrape all the data.
#For the moment it's restricted to scraping a local file, because
#testing it out in the wild might ring some ddos alarms.

#Forum traversial not implemented yet, lots of debugging prompts.

class PostScanner(object):
#SCRAPING SCRIPT START
    global debug
    debug = False

    def check_date(self, s):
        """
        This function is meant to check whether a string has a specific date format.
        It is important, because dates are used as delimiters between posts, although
        this may be forum specific.
        """
        if re.search(r'\d{4}-\d{2}-\d{2}', s) or 'godziny temu' in s or 'minuty temu' in s:
            return True
        else:
            return False

    def check_img(self, s):
        """
        This function checks if a string is likely a name of an image.
        """
        if re.search(r'\.jpg|\.tiff|\.gif|\.bmp|\.png', s.lower()):
            return True
        else:
            return False

    def get_page_images(self, page):
        """
        This function is responsible for obtaining all images from a single page
        of posts, downloading them, and storing them in an iterable list od tuples.
        Each tuple consists of two elements - a string with the name of an image
        and a Requests.response object containing the image.
        """
        pics = page.xpath('//table[@class="attachment"]//a[@class="tooltip"]/img/attribute::alt')
        links = iter(page.xpath('//table[@class="attachment"]//a[@class="tooltip"]/attribute::href'))
        combined = []
        for i in pics:
            print 'i'
            img_tup = (i, requests.get(links.next()))
            combined.append(img_tup)

        return iter(combined)



    def make_post_list(self, posts, page):
        """
        This function takes in dirty data obtained from parsing an html file,
        and cleans it to get the date, post, and image names.
        """
        cont = []
        final = []
        i = 0
        di = {}

        images = []

        web_images = self.get_page_images(page)



        def end(di, cont, final, images):
            """
            This hack is supposed to 'cap' posts and thread.
            """
            di['post'] = ''.join(cont)
            cont[:] = []
            di['images'] = images[:]
            final.append(di)
            images[:] = []
            di = {}
            return di,cont, final, images

        limit = len(posts)
        while i < limit:
            is_date = self.check_date(posts[i])
            if is_date and not final and not di:            
                di['date'] = posts[i]

            elif self.check_img(posts[i]):
                # images.append(posts[i])
                images.append(web_images.next())

            elif not is_date:
                cont.append(posts[i])

            else: 

                di, cont, final, images = end(di, cont, final, images)
                di['date'] = posts[i]
            i += 1
        end(di, cont, final, images)
        print final
        return final


    def scan(self, page):
        """
        This is the main user-facing function to use. It takes 
        a web page source as a string input and then continues to parse it,
        extracting images and sorting the data.
        It's output is a list of dictionaries, where each dictionary contains
        represents a single post.
        """


        tree = html.fromstring(page)
        content = tree.xpath('//div[@class="tresc"]//text()')
        if debug:
            print len(content)
            print content
        filtered_list = []
        bad = ['Dodany: ', 'Cytuj+', '|', 'Link', u'Zg\u0142o\u015b', 'Cytuj']

        # for i in content:
        #     if not re.search(r'^\s[\r\n\t\t]', i) and i not in bad:
        #         filtered_list.append(i)
        filtered_list = [i for i in content if not re.search(r'^\s[\r\n\t\t]', i) and i not in bad]
        if debug:
            print 'filtered list:'
            print len(filtered_list)
            print filtered_list


        page_of_posts = self.make_post_list(filtered_list, tree)

        authors = tree.xpath('//div[@class="nickdiv"]/a/text()')
        authors = [i.strip() for i in authors]
        if debug:
            print len(authors)
            print 'authors: ', authors

        iter_authors = iter(authors)
        for i in page_of_posts:
            i['author'] = iter_authors.next()



        if debug:
            print 'page of posts:'
            print page_of_posts
            print len(page_of_posts)

        return page_of_posts

if __name__ == '__main__':
    #Temporary testing mechanism.


    usr_input = raw_input('Select the file to scrape: ')
    try:
        f = open(usr_input, 'rb')
    except IOError:
        print 'couldnt open file'
    else:
        print 'file open successfully'
        scraper = PostScanner()
        scraped = scraper.scan(f.read())
        for i in scraped:
            print i['author']
            print i['date']
            print i['post'].encode('utf-8')
            if 'images' in i:
                print i['images']

    finally:
        
        f.close()
        print 'file closed'

