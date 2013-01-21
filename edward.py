from lxml import html
import requests
import re
import sqlite3
from sys import exit

#Edward,
#Will scour a specific forum and extract posts along with date, author, content
#and images and input that information into a database. Very handy if there
#is no way to export the data any other way.


#It's aim is to scan a page of posts and scrape all the data.
#For the moment it's restricted to scraping a local file, because
#testing it out in the wild might ring some ddos alarms.

#Forum traversial not implemented yet, lots of debugging prompts.

class PostScanner(object):
    global debug

    def __init__(self, u):
        self.url = u

    def check_date(self, s):
        """
        This function is meant to check whether a string has a specific date format.
        It is important, because dates are used as delimiters between posts, although
        this may be forum specific.
        """
        if re.search(r'\d{4}-\d{2}-\d{2},', s) or re.search(r'godzin. temu|minut. temu', s) or re.search(r'wczoraj, \d{2}:\d{2}', s):
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
            print 'i',
            img_tup = (u'%s' % i, requests.get('%s%s' % (self.url, links.next())))
            combined.append(img_tup)

        return iter(combined)

    def make_post_list(self, posts, page):
        """
        This function takes in dirty data obtained from parsing an html file,
        and cleans it to get the date, post, and image names. Returns a 
        dictionary.
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

            #di is the dictionary
            #cont is short for content

            di['post'] = u''.join(cont)

            cont[:] = []
            di['images'] = images[:]
            final.append(di)
            images[:] = []
            di = {}
            return di,cont, final, images

        limit = len(posts)
        #rework this while loop for some minor content parsing
        while i < limit:
            is_date = self.check_date(posts[i])
            if is_date and not final and not di:            
                di['date'] = u'%s' % posts[i]
            elif self.check_img(posts[i]):
                images.append(web_images.next())
            elif not is_date:
                cont.append(posts[i])
            else: 
                di, cont, final, images = end(di, cont, final, images)
                di['date'] = u'%s' % posts[i]
            i += 1
        end(di, cont, final, images)
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

        filtered_list = []
        bad = ['Dodany: ', 'Cytuj+', '|', 'Link', u'Zg\u0142o\u015b', 'Cytuj']

        filtered_list = [i for i in content if not re.search(r'^\s[\r\n\t\t]', i) and i not in bad]

        page_of_posts = self.make_post_list(filtered_list, tree)

        authors = tree.xpath('//div[@class="nickdiv"]/a/text() | //div[@class="nickdiv"]/text()')
        authors = filter(None, [i.strip() for i in authors])
        print authors
        print page_of_posts
        print 'authors: ', len(authors)
        print 'posts: ', len(page_of_posts)
        iter_authors = iter(authors)
        try:
            for i in page_of_posts:
                i['author'] = unicode(iter_authors.next())
        except:
            conn.close()

        for p in page_of_posts:
            try:
                #This is the place where posts are inserted into the DB
                post_cur.execute('INSERT INTO POSTS (p_author, p_date, p_content, t_id) values (?, ?, ?, ?);', 
                                (p['author'], p['date'], p['post'], topic_cur.lastrowid))
                #And this is where images are inserted into the DB
                if p['images']:
                    for i in p['images']:
                        img_cur.execute('INSERT INTO IMGS (i_name, image, p_id) values (?, ?, ?);', 
                                    (i[0], sqlite3.Binary(i[1].content), post_cur.lastrowid))
            except sqlite3.Error, e:
                print e
                conn.close()
                exit(1)

        return page_of_posts

def get_topics(topic_tree):
    """
    This function is responsible for scraping a topics page. It returns a list
    of tuples in the format of (links, number of posts, titles).
    """
    topic_links = topic_tree.xpath('//tr[@class="transp"]/td[1]/a/attribute::href | //tr[@class=" z_tlem"]/td[1]/a/attribute::href')
    posts_per_topic = topic_tree.xpath('//tr[@class="transp"]/td[2]/text() | //tr[@class=" z_tlem"]/td[2]/text()')
    topic_titles = topic_tree.xpath('//tr[@class="transp"]/td[1]/a/text() | //tr[@class=" z_tlem"]/td[1]/a/text()')
    return zip(topic_links, posts_per_topic, topic_titles)

def post_scraper(url, t_info):   
    """
    This function obtains a list of tuples, each containing the link to a topic
    and a number of posts. It uses PostScanner.scan() to scan each page and,
    for now, stores it in a variable called scraped.
    """    
    for link, posts, title in t_info:
        try:
            #This inserts a topic's name into the database
            topic_cur.execute('INSERT INTO TOPICS (t_name, f_id) values (?, ?);', (title, forum_cur.lastrowid))
        except sqlite3.Error, e:
            print e
            conn.close()
            exit(1)

        if int(posts) % 10 == 0:
            post_limiter = (int(posts)/10)
        else:
            post_limiter = (int(posts)/10+2)

        for k in range(1, post_limiter):

            p_page = requests.get('%s%s/%d' % (url, link, k))
            scraped = scraper.scan(p_page.text)

            print scraped

    try:
    #experimental DB write here, tweak for performance
        conn.commit()
    except sqlite3.Error, e:
        print e
        conn.close()
        exit(1)


if __name__ == '__main__':


    from secret_url import secret_url
    url = secret_url.url

    page = requests.get(url)
    tree = html.fromstring(page.text)
    links = tree.xpath('//table[@id="serwis"]//div[@class="fl"]/a/attribute::href')
    headers = tree.xpath('//table[@id="serwis"]//div[@class="fl"]/a/text()')

    forums = zip(links, headers)

    scraper = PostScanner(url)
    db_name = raw_input('Input database name: ')

    try:
        conn = sqlite3.connect(db_name)
        forum_cur = conn.cursor()
        topic_cur = conn.cursor()
        post_cur = conn.cursor()
        img_cur = conn.cursor()
        forum_cur.execute('DROP TABLE IF EXISTS FORUMS;')
        forum_cur.execute('DROP TABLE IF EXISTS TOPICS;')
        forum_cur.execute('DROP TABLE IF EXISTS POSTS;')
        forum_cur.execute('DROP TABLE IF EXISTS IMGS;')
        forum_cur.execute('CREATE TABLE FORUMS (f_id integer primary key, f_name text);')
        forum_cur.execute('CREATE TABLE TOPICS (t_id integer primary key, t_name text, f_id references FORUMS);')
        forum_cur.execute('CREATE TABLE POSTS (p_id integer primary key, p_author text, p_date text, p_content text, t_id references TOPICS);')
        forum_cur.execute('CREATE TABLE IMGS (i_id integer primary key, i_name text, image blob, p_id references POSTS);')
    except sqlite3.Error, e:
        print e
        conn.close()
        exit(1)

    conn.commit()

    #set range for number of forums starting with zero and going up to 
    #number of forums + 1
    for i in xrange(0, 7):

        page = requests.get('%s%s' % (url, forums[i][0]))

        print 'next topic'
        #This an entry into the database with the title of a forum
        forum_cur.execute('INSERT INTO FORUMS (f_name) values (?);', (unicode(forums[i][1]),))


        topic_tree = html.fromstring(page.text)

        number_of_pages = topic_tree.xpath('//div[@class="paging"]/div[@class="wrap"]/em/text()')

        if number_of_pages:
            number_of_pages = int(number_of_pages[0][-3:-1])
            number_of_pages += 1
            for j in xrange(1, number_of_pages):

                topic_page = requests.get('%s%s/%d' % (url, forums[i][0], j))
                topics_per_page = html.fromstring(topic_page.text)
                topic_info = get_topics(topics_per_page)

                post_scraper(url, topic_info)


        else:
            topic_page = requests.get('%s%s' % (url, forums[i][0]))
            topics_per_page = html.fromstring(topic_page.text)
            topic_info = get_topics(topics_per_page)

            post_scraper(url, topic_info)

    print 'page scraped'
    print 'scraped %d posts' % post_cur.lastrowid
    print 'scraped %d topics' % topic_cur.lastrowid
    print 'scraped %d images' % img_cur.lastrowid
    print 'scraped %d forums' % forum_cur.lastrowid
    conn.close()