temaparser
==========
#### Parse a webpage for links to files/folders, download them recursively.
As it turned out, all this can be solved (and in a much more robust way) with:

##### *wget --mirror -nH --no-parent -R index.html*

Nevertheless, let this remain a tribute to the gods of Pythonism.

Usage
----------
    usage: temaparser.py [-h] [-f] [-r] [-d] [url]
    
    positional arguments:
        url              Absolute url of page with directory listing.
    
    optional arguments:
      -f, --force      Overwrite existing files/folders.
      -r, --recursive  Download with subfolders.
      -d, --direct     Directly download given URL as a folder. 
                       Otherwise URL is treated as a listing of folders which are 
                       downloaded only if they don't exist locally.
