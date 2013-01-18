## Edward

### What is all this about?

Edward is a script meant to save the content of an online forum, which otherwise does not allow any way to export the data. It is specifically tailored to a conrete forum, however by changing a few xpath queries I am sure it is possible to expand its functionality to other platforms due to their common characteristics.

Edward is meant to use lxml and Requests to traverse a forum and gather information such as authors, post content, dates, pictures and store them in an SQLite database. Later, Edward will also facilitate the extraction of this data using Requests to POST it onto a new forum. 

At the current stage Edward is mostly a skeleton with the ability to scrape the authors, dates, content, and attachments from a single page of posts. I'm currently working on hooking it up to a general forum traversial and database input mechanism, after which I'll code the reverse functions.

### License

Copyright (C) 2013  sirMackk

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.