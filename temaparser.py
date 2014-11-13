import os, re
from urllib import urlopen, urlretrieve
from urlparse import urljoin

# REMOTE SETTINGS
URL = "http://127.0.0.1:8000/" # absolute url of page with directory listing
REMOTE_DIR_FORMAT = None
# Uncomment next line to restrict directory names that are downloaded.
# REMOTE_DIR_FORMAT = re.compile(r'\d+\.\d+\.\w+\/?')

# LOCAL SETTINGS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE_DIR, "download.log") # history file path (relative to BASE_DIR)
DWN_PATH = os.path.join(BASE_DIR,"downloads") # downloaded files path
if not os.path.exists(DWN_PATH):
    os.makedirs(DWN_PATH)

def find_links(html_page):
    """
    Returns a list with string values of all "href=" attributes
    """
    link_re = re.compile(r'href=[\'"]?([^\'" >]+)')
    links = re.findall(link_re, html_page)
    return links

# Easy version (use if your site doesn't strip trailing slash from "href=")
def link_is_dir(link):
    return True if link.endswith('/') else False

# Hard version (with regex matching and empirical check for dir)
# def link_is_dir(link):
#     if REMOTE_DIR_FORMAT.match(link):
#         u = urlopen(urljoin(URL, link))
#         if u.headers.gettype() == "text/html":
#             return True
#     return False

def set_local_dirs():
    return {d+os.path.sep for d in os.listdir(DWN_PATH) if os.path.isdir(os.path.join(DWN_PATH, d))}

def list_remote_dirs():
    raw_html = urlopen(URL).read()
    dir_links = filter(link_is_dir, find_links(raw_html))
    return dir_links

def download_dir(dir_link, base_path, base_url):
    path = os.path.join(base_path, dir_link)
    url = urljoin(base_url, dir_link)
    with open(LOG, "a") as log:
        os.makedirs(path)
        dir_page = urlopen(url).read()
        links = find_links(dir_page)

        for link in links:
            if link_is_dir(link):
                download_dir(link, path, url)
            else:
                urlretrieve(url+link, path+link)
                print "downloaded file {0}".format(path+link)
                log.write("downloaded file {0}".format(path+link))


target_dirs = [x for x in list_remote_dirs() if x not in set_local_dirs()]

for dir_link in target_dirs:
    download_dir(dir_link, DWN_PATH, URL)
