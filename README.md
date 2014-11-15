temaparser
==========
#### Parse a webpage for links to files/folders, download them recursively.
As it turned out, all this can be solved (and in a much more robust way) with:

##### *wget --mirror -nH --no-parent -R index.html*

Nevertheless, let this remain a tribute to the gods of Pythonism.

Usage
----------
    usage: temaparser.py [-h] [-m MASK] [-f] [-r] [-d] url [destination]

    positional arguments:
      url                   Absolute url of page with directory listing.
      destination           Destination for downloaded files.

    optional arguments:
      -h, --help            show this help message and exit
      -m MASK, --mask MASK  Download only files matching this mask.
      -f, --force           Overwrite existing files/folders.
      -r, --recursive       Download with subfolders.
      -d, --direct          Directly download given URL as a folder. Otherwise URL
                            is treated as a listing of folders which are are
                            downloaded only if they don't exist locally.

Examples
----------
    $ temaparser.py http://127.0.0.1/repo/
Downloads all new (non-existant locally) folders from given URL into "./downloads/".

    $ temaparser.py -d -r http://127.0.0.1/repo/v2.10/ ~/mydir --mask="*.zip"
Downloads .zip files from given URL into "~/mydir/v2.10" (including recursive subdirs).

