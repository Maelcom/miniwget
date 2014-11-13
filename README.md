temaparser
==========
#### Parse a webpage for links to folders, download new folders recursively, skip existing top-level folders.
As it turned out, all this can be solved (and in a much more robust way) with:

##### *wget --mirror -nH --no-parent -R index.html*

Nevertheless, let this remain a tribute to the gods of Pythonism.
