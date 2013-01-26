# -*- coding: utf-8 -*-

import sqlite3
from sys import exit
import os
import base64
import time
import datetime
import re

#This is a quick and dirty script written to accept databases
#created by edward.py and generate phpbb3 compliant SQL queries
#as well as images, which can be uploaded directly into the 
#/files folder of a phpbb3 installation. This script creates
#entries for topics, posts, and attachments. It doesn't not create 
#forums, which have to be created manually. Additionally, the id's
#of these forums must be connected to the forum id's found in
#databases created by edward.py. The same goes for users.
#By default this script generates attachment entries as having a
#thumbnail, this can be modified by changing the last digit in
#the "attachment" string below. This script does not however
#create thumbnails of the images, which have to be resized
#and renamed manually.


#POST TUPLE EXAMPLE REFERENCES BELOW:
# (forum id, forum name, topic id, topic name, post id, post author, date, post content,
#     image id, image name, image buffer object)



#These are the queries that will input the data correctly into a phpbb3 mysql database
return_post = "(%d, %d, %d, %d, 0, '', %d, 1, 0, 1, 1, 1, 1, '', '%s', '%s', '1', %d, '', '14djfgd3', 1, 0, '', 0, 0, 0, NULL, NULL, NULL)"
attachment = "(%d, %d, %d, 0, %d, 0, '%s', '%s', 0, '', '%s', '%s', %d, %d, 1)"
topic = "(%d, %d, 0, 1, 1, 0, '%s', %d, %d, 0, 0, 0, 0, 0, 0, %d, '%s', '', %d, %d, '%s', '', '%s', %d, 0, 0, 0, 0, '', 0, 0, 1, 0, 0, NULL)"


#This dict contains keys of names of users and values corresponding to their user_id 
#in the new forum
from secret_url import secret_url
autorzy = secret_url.autorzy

#This dict contains a mapping of forum id's between the new and old forums
forums = {1:9, 3:4, 4:5, 
            2: 3, 5:6, 
            6: 7, 7:8}
#post and topic offset. If you're inserting posts and topics in a forum which already 
#exists, it would be wise to use an offset, so that nothing is overwritten.
offset = 100
date = ''

def get_poster_id(name):
    """
    This function uses the autorzy dictionary in order to find the correct
    user name and user_id pairing.
    """
    return autorzy[name.encode('latin-1')]


def get_forum_id(id):
    """
    This functions uses the forums dictionary in order to correctly
    pair forums.
    """

    return forums[int(id)]
    #must return forum id corellated with forum name
    pass

def make_topic(first_post, last_post):
    """
    This function is responsible for creating the correct topic SQL
    query for phpbb3. It uses the global offset variable to create topics
    with the correct row offset. Further more, it uses the first and last
    posts of a topic to create the correct database entry.
    """
    global offset
    topic_id = first_post[2]+offset
    forum_id = get_forum_id(first_post[0])
    topic_name = first_post[3]
    topic_poster_id = get_poster_id(first_post[5])
    topic_time = get_post_time(first_post[6])
    first_post_id = first_post[4] + offset
    first_post_name = first_post[5]
    last_post_id = last_post[4] + offset
    last_poster_id = get_poster_id(last_post[5])
    last_poster_name = last_post[5]
    last_post_time = get_post_time(last_post[6])

    return topic % (topic_id, forum_id, topic_name, topic_poster_id, topic_time, first_post_id, 
                    first_post_name, last_post_id, last_poster_id, last_poster_name, topic_name, 
                    last_post_time)


def get_post_time(times):
    """
    This function accepts a string date and reworks it into unix time format.
    This if very forum specific, this forum uses a date in the format of:
    yyyy-mm-dd, hh:mm:ss. What is more, this forum also has entries in the form
    of: x hours ago, hh:mm and similar, which are edge cases that need to be
    included in here in the near future.
    """
    global date
    print date

##################################    #make special cases for minutes and hours




    if re.search(r'wczoraj', times) or re.search(r'godzin|minut', times):
        unix_time = time.mktime(datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:10])-1, 
                    int(times[-5:-3]), int(times[-2:]), 0).timetuple())
        
    else:
        unix_time = time.mktime(datetime.datetime(int(times[:4]), int(times[5:7]), int(times[8:10]),
            int(times[12:14]), int(times[15:17]), int(times[18:20])).timetuple())
        date = times

    #25200 is an arbitrary number of seconds that I found to match the correct
    #posting times.
    return int(unix_time)-25200


def make_post(post):
    """
    This function creates posts entries, including ones with posts. It accepts
    a single post tuple and determines whether it has images attached to it and
    whether this post already exists. If it already exists, it just creates 
    attachment entries. A clear note about the format of this tuple (important)
    can be found at the beginning of this file.
    """

    global offset
    global date

    if posts:
        if post[4]+offset < 1001:
            if posts and post[4]+offset == int(posts[-1][1:4]):
                print 'just image'
                    #duplicate post, meaning it's an attachment
                attachments.append(make_attach(post[4]+offset, post[2]+offset, get_poster_id(post[5]), 
                                        post[8], post[9], get_post_time(post[6])))
                return None
        if post[4]+offset > 1001 and post[4]+offset < 10000:
            print post[4]+offset
            print posts[-1][1:5]
            if posts and post[4]+offset == int(posts[-1][1:5]):
                print 'just image, 1000k + posts!'
                    #duplicate post, meaning it's an attachment
                attachments.append(make_attach(post[4]+offset, post[2]+offset, get_poster_id(post[5]), 
                                        post[8], post[9], get_post_time(post[6])))  
                return None
        if post[4] >= 10000:
            if posts and post[4]+offset == int(posts[-1][1:6]):
                print 'just image'
                    #duplicate post, meaning it's an attachment
                attachments.append(make_attach(post[4]+offset, post[2]+offset, get_poster_id(post[5]), 
                                        post[8], post[9], get_post_time(post[6])))  
                return None


        


    if post[9] is not None and post[10] is not None:
        print 'has images'
        #post with image
        attachments.append(make_attach(post[4]+offset, post[2]+offset, get_poster_id(post[5]), 
                            post[8], post[9], get_post_time(post[6])))

        return return_post % (post[4]+offset, post[2]+offset, get_forum_id(post[0]), get_poster_id(post[5]), 
                                get_post_time(post[6]), post[3], post[7], 1)
    else:
        print 'no images'
        #new post without image
        return return_post % (post[4]+offset, post[2]+offset, get_forum_id(post[0]), get_poster_id(post[5]), 
                                get_post_time(post[6]), post[3], post[7], 1)


    # return values


def make_attach(post_id, topic_id, poster_id, img_id, img_name, time):
    """
    This function create attachment entries with randomly generated,
    22 character long names without extensions. It also checks their
    size and ensures that the SQL entry will have a proper mime-type
    and file-type.
    """
    global i_id 
    i_id += 1


    i_cur.execute('SELECT * from IMGS where i_id = %s' % str(img_id))
    image = i_cur.fetchone()

    image_name = base64.urlsafe_b64encode(os.urandom(22))
    try:
        f = open(image_name, 'wb')
        f.write(image[2])
        f.close()
    except IOError, e:
        print e
        exit(1)

    file_size = os.stat(image_name).st_size
    mime_type = 'image/%s' % img_name.split('.')[-1]
    file_type = img_name.split('.')[1]


    return attachment % (i_id, post_id, topic_id, poster_id, image_name, img_name, 
                    file_type.lower(), mime_type.lower(), file_size, time)



try:
    #This is the attachment offset. It must be larger than any already exists
    #attachment ID present in the DB.
    i_id = 50
    #main1a.db is the database I'm using, has to be changed.
    conn = sqlite3.connect('main1a.db')
    cur = conn.cursor()
    i_cur = conn.cursor()
    cur.execute('SELECT ROWID from TOPICS ORDER BY ROWID DESC LIMIT 1;')
    max_topic_range = cur.fetchone()[0]
    posts = []
    attachments = []
    topics = []

    for i in xrange(1, max_topic_range+1):
        print 'topic #: ', i
        cur.execute('select * from forums_topics where t_id = %d;' % i)
        topic_posts = cur.fetchall()
        for j in topic_posts:
            candidate = make_post(j)
            if candidate is not None:
                posts.append(candidate)

 
        topics.append(make_topic(topic_posts[0], topic_posts[-1]))



except sqlite3.Error, e:
    print e
    exit(1)

finally:
    conn.close()

#These are the actual sql queries. They will precede the data, so that phpMyAdmin knows where to insert the data.
post_insert = """
INSERT INTO phpbb_posts (post_id, topic_id, forum_id, poster_id, icon_id, poster_ip, post_time, post_approved, post_reported, enable_bbcode, enable_smilies, enable_magic_url, enable_sig, post_username, post_subject, post_text, post_checksum, post_attachment, bbcode_bitfield, bbcode_uid, post_postcount, post_edit_time, post_edit_reason, post_edit_user, post_edit_count, post_edit_locked, post_wpu_xpost_parent, post_wpu_xpost_meta1, post_wpu_xpost_meta2) VALUES 
"""

topic_insert = """
INSERT INTO phpbb_topics (topic_id, forum_id, icon_id, topic_attachment, topic_approved, topic_reported, topic_title, topic_poster, topic_time, topic_time_limit, topic_views, topic_replies, topic_replies_real, topic_status, topic_type, topic_first_post_id, topic_first_poster_name, topic_first_poster_colour, topic_last_post_id, topic_last_poster_id, topic_last_poster_name, topic_last_poster_colour, topic_last_post_subject, topic_last_post_time, topic_last_view_time, topic_moved_id, topic_bumped, topic_bumper, poll_title, poll_start, poll_length, poll_max_options, poll_last_vote, poll_vote_change, topic_wpu_xpost) VALUES 
"""
attachment_insert = """
INSERT INTO phpbb_attachments (attach_id, post_msg_id, topic_id, in_message, poster_id, is_orphan, physical_filename, real_filename, download_count, attach_comment, extension, mimetype, filesize, filetime, thumbnail) VALUES 
"""
def encoding_help(s):
    """
    This function is responsible for encoding the strings from the database
    with the right encoding before they get written to a text file. This
    is also very forum specific, as the forums seemed to have used a dominant
    latin-1 charset, but additionally it used 2 characters from unicode. 
    Special treatment was needed in order to filter these two unicode characters
    and replace with with ascii ones, which mingle easily with latin-1.
    """
    if u'\u201d' in s or u'\u2019' in s:
        string = s.replace(u'\u201d', '"')
        if u'\u2019' in string:
            string = string.replace(u'\u2019', '"')

        return string.encode('latin-1')

    else:

        return s.encode('latin-1')



try:
    f = open('sql_queries.sql', 'wb')
    f.write(topic_insert)
    for i in topics[:-1]:
        f.write('%s, ' % encoding_help(i))
    f.write('%s; ' % encoding_help(topics[-1]))

    f.write(post_insert)
    for i in posts[:-1]:
        f.write('%s, ' % encoding_help(i))
    f.write('%s; ' % encoding_help(posts[-1]))

    f.write(attachment_insert)
    for i in attachments[:-1]:
        f.write('%s, ' % encoding_help(i))
    f.write('%s; ' % encoding_help(attachments[-1]))

except IOError, e:
    print e
    exit(1)
finally:
    f.close()