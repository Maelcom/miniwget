import os, re
from urllib import urlopen, urlretrieve
from urlparse import urljoin, urlparse
import logging

# REMOTE SETTINGS
URL = "http://127.0.0.1:8000/" # absolute url of page with directory listing
REMOTE_DIR_FORMAT = None
# Uncomment next line to restrict directory names that are downloaded.
# REMOTE_DIR_FORMAT = re.compile(r'\d+\.\d+\.\w+\/?')

# LOCAL SETTINGS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DWN_PATH = os.path.join(BASE_DIR,"downloads") # downloaded files path
if not os.path.exists(DWN_PATH):
    os.makedirs(DWN_PATH)

logging.basicConfig( filename=os.path.join(BASE_DIR, "download.log"),
                     filemode='w',
                     level=logging.DEBUG,
                     format= '%(asctime)s - %(levelname)s - %(message)s')

def find_links(html_page):
    """
    Returns a list with string values of all "href=" attributes.
    Excludes parent links like '../'
    """
    link_re = re.compile(r'<a.*href=["\']?((?!\.)[^\'" >]+)')
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
    return {d for d in os.listdir(DWN_PATH) if os.path.isdir(os.path.join(DWN_PATH, d))}

def list_remote_dirs():
    raw_html = urlopen(URL).read()
    dir_urls = filter(link_is_dir, find_links(raw_html))
    dir_names = map(url2dir, dir_urls)
    return zip(dir_urls, dir_names)

def url2dir(dir_url):
    return urlparse(dir_url).path.rstrip('/').split('/')[-1]

def download_dir(dir_url, base_path, base_url):
    dir_name = url2dir(dir_url)
    path = os.path.join(base_path, dir_name)
    url = urljoin(base_url, dir_url)

    logging.info("="*80)
    logging.info("Found new dir on server!")
    logging.info("url: {0}".format(url))
    logging.info("dir_name: {0}".format(dir_name))
    logging.info("path to save: {0}".format(path))

    dir_page = urlopen(url).read()
    links = find_links(dir_page)

    logging.info("total {0} links found".format(len(links)))
    logging.info("="*80)

    try:
        os.makedirs(path)
    except Exception as e:
        logging.error("Couldn't create download folder. Error message: {0}".format(e))

    for link in links:
        if link_is_dir(link):
            download_dir(link, path, url)
        else:
            try:
                file_name = url2dir(link)
                logging.info("trying to download\n{0}\ninto\n{1}\n".format(urljoin(url,link), os.path.join(path,file_name)))
                urlretrieve(urljoin(url, link), os.path.join(path, file_name))
                logging.info("SUCCESS - downloaded file\n{0}\n".format(link))
            except Exception as e:
                logging.error("Couldn't download file\n{0}\nError message: {1}\n".format(link, e))


if __name__ == "__main__":
    loc = set_local_dirs()
    rem = list_remote_dirs()
    target_dirs = [x[0] for x in rem if x[1] not in loc]

    print loc
    print rem
    print target_dirs

    for dir_url in target_dirs:
        download_dir(dir_url, DWN_PATH, URL)
