temaparser
==========
#### Parse a webpage for links to files, download new files, skip old ones (stored in a history file).
As it turned out, all this can be solved (and in a much more robust way) with:

##### *wget --mirror -nH --no-parent -R index.html*

Nevertheless, let this remain a tribute to the gods of Pythonism.
