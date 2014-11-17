import os, argparse, re
from urllib import urlopen, urlretrieve
from urlparse import urljoin, urlparse
import logging
import fnmatch
import sys

"""
SETUP
"""
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Retrieve files/folders from URL.',
    epilog='Example: \n \
    $ %s -d -r http://127.0.0.1/repo/v2.10/ ~/mydir --mask="*.zip"\n\n \
    This will download .zip files found by given URL into \n \
    "~/mydir/v2.10" (with recursive subdirs).' % __file__)
parser.add_argument("url", help="Absolute url of page with directory listing.")
parser.add_argument("destination", nargs="?", help="Destination for downloaded files.")
parser.add_argument("-m", "--mask", type=str, help="Download only files matching this mask.")
parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files/folders.")
parser.add_argument("-r", "--recursive", action="store_true", help="Download with subfolders.")
parser.add_argument("-d", "--direct", action="store_true",
                    help="Directly download given URL as a folder. \
                    Otherwise URL is treated as a listing of folders which are \
                    are downloaded only if they don't exist locally.")

args = parser.parse_args()

RECURSIVE = args.recursive
FORCE = args.force
DIRECT = args.direct
MASK = args.mask
URL = args.url
DEST = args.destination

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if DEST:
    DWN_PATH = os.path.join(os.getcwd(), DEST)
    if not os.path.exists(DWN_PATH):
        raise Exception("Invalid destination specified: "+DWN_PATH)
else:
    DWN_PATH = os.path.join(BASE_DIR,"downloads")
"""
SETUP END
"""

"""
LOCAL SETTINGS
"""
# Uncomment next line to restrict directory names that are downloaded.
# REMOTE_DIR_FORMAT = re.compile(r'\d+\.\d+\.\w+\/?')

LOG_FILE = os.path.join(BASE_DIR, "download.log")
IGNORE_FILE = os.path.join(BASE_DIR, ".ignorelist")

ignore_list = []
if os.path.isfile(IGNORE_FILE):
    with open(IGNORE_FILE, 'r') as f:
        ignore_list = [x.strip().strip('\\/') for x in f]

if not os.path.exists(DWN_PATH):
    os.makedirs(DWN_PATH)
logging.basicConfig( filename=LOG_FILE,
                     filemode='w',
                     level=logging.DEBUG,
                     format= '%(asctime)s - %(levelname)s - %(message)s')
"""
LOCAL SETTINGS END
"""


def find_links(html_page):
    """
    Returns a list with string values of all "href=" attributes.
    Excludes parent links like '../'
    """
    link_re = re.compile(r'<a.*href=["\']?((?!\.)[^\'" >]+)')
    links = re.findall(link_re, html_page)
    return links

def link_is_dir(link):
    """
    Easy version (use if your site doesn't strip trailing slash from "href=")
    """
    return True if link.endswith('/') else False

# def link_is_dir(link):
#     """
#     Hard version (with regex matching and empirical check for dir)
#     """
#     if REMOTE_DIR_FORMAT.match(link):
#         u = urlopen(urljoin(URL, link))
#         if u.headers.gettype() == "text/html":
#             return True
#     return False

def set_local_dirs(path=DWN_PATH):
    return {d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))}

def list_remote_dirs(url=URL):
    raw_html = urlopen(url).read()
    dir_urls = filter(link_is_dir, find_links(raw_html))
    dir_names = map(url2dir, dir_urls)
    return zip(dir_urls, dir_names)

def url2dir(dir_url):
    return urlparse(dir_url).path.rstrip('/').split('/')[-1]

def _progressbar_hook(file_name):
    def inner_hook(blocks, block_size, file_size, bar_length=25):
        got_size = min(blocks * block_size, file_size)
        percent = float(got_size) / file_size if file_size>0 else 1.0
        dots = int(percent * bar_length)
        bar = '[' + '.'*dots + ' '*(bar_length-dots) + ']'

        output = "{0:3}% {1} {2} / {3} kB \r".format(int(percent*100), bar, got_size, file_size)
        if not blocks:
            sys.stdout.write('downloading {0}\n'.format(file_name))

        sys.stdout.write(output)
        sys.stdout.flush()
    return inner_hook

def get_files(file_links, path, url):
    for file_link in file_links:
        file_url = urljoin(url, file_link)
        file_name = url2dir(file_link)
        file_path = os.path.join(path, file_name)

        if FORCE or not os.path.isfile(file_path):
            logging.info("trying to download\n{0}\ninto\n{1}\n".format(file_url, file_path))
            try:
                urlretrieve(file_url, file_path, _progressbar_hook(file_name))
                sys.stdout.write('\n')
                logging.info("SUCCESS - downloaded file\n{0}\n".format(file_link))
            except Exception as e:
                logging.error("Couldn't download file\n{0}\nError message: {1}\n".format(file_link, e))
        else:
            logging.warning("file already exists - skipping:\n{0}\n".format(file_name))

def download_dir(dir_url, path=DWN_PATH, base_url=URL):
    # Ensure dir_url is absolute (could be relative up to this point)
    url = urljoin(base_url, dir_url)

    dir_name = url2dir(url)
    if dir_name:
        if dir_name not in ignore_list:
            path = os.path.join(path, dir_name)
        else:
            return

    sys.stdout.write("\nProcessing folder {0}\n".format(dir_url))

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            logging.error("Couldn't create download folder. Error message: {0}".format(e))
    elif not FORCE and dir_name:
        logging.warning("target dir already exists - skipping:\n{0}\n".format(path))
        return

    logging.info("="*80)
    logging.info("Found new dir on server!")
    logging.info("url: {0}".format(url))
    logging.info("dir_name: {0}".format(dir_name))
    logging.info("path to save: {0}".format(path))

    dir_page = urlopen(url).read()
    links = find_links(dir_page)
    # Split links to dir_links and file_links
    # NOTE: these links can be relative -> make absolute before passing them on.
    file_links, dir_links = [], []
    for link in links:
        if link_is_dir(link):
            dir_links.append(link)
        elif not MASK or fnmatch.fnmatch(url2dir(link), MASK):
            file_links.append(link)


    logging.info("total {0} links found: {1} files and {2} directories".format(len(links), len(file_links), len(dir_links)))
    logging.info("="*80)

    # Get files
    get_files(file_links, path, url)

    # Get folders
    if RECURSIVE:
        for dir_link in dir_links:
            download_dir(dir_link, path, url)

def main():
    if DIRECT:
        target_dirs=[URL]
    else:
        loc = set_local_dirs()
        rem = list_remote_dirs(URL)
        target_dirs = [x[0] for x in rem if x[1] not in loc]

        if ignore_list:
            sys.stdout.write("Will skip folders listed in {0}\n".format(IGNORE_FILE))

    for dir_url in target_dirs:
        download_dir(dir_url)

if __name__ == "__main__":
    main()
