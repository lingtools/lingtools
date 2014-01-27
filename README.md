lingtools
=========

Simple tools for studying language: data preprocessing, frequency
norms, n-gram models, working with lexicons, and more.

LingTools incorporates external modules for syllabification
(``lingtools.phon.syllabify``) and for reading from Praat TextGrids
``lingtools.phon.textgrid``). See
[syllabify](https://github.com/kylebgorman/syllabify/) and
[textgrid](https://github.com/kylebgorman/textgrid/) for more
information.

Corpora
=======

``lingtools.corpus`` contains Python modules for reading from popular lexical databases.
It currently supports using CELEX, CMUDict and SUBTLEX.

You can use it without installing just like any other Python package by
placing it on your PYTHONPATH or just running your scripts in the root
of LingTools.



Installation
============

*You do not need to install ``lingtools`` to use it. However, if you want to use its

If you want to install it, do the following:

1. Clone this git repository.
1. Run ``sudo python setup.py install`` in the root of the repository. 
   (You can skip the sudo if your Python site libraries live in a user-writable 
   location.)

You can now use ``lexinfo`` from any Python program on your system.
One of the annoying things about working with lexical databases is downloading
the right files. ``lexinfo`` can do this for you. For the readers that have
publicly available data (i.e., SUBTLEX, CMUDict) you can 
run the ``download`` method in the module to download the data
to the current working directory. You can see an example in the usage example
below, which uses the standard paths that the files will be downloaded to.


       >>> from lingtools.corpus import subtlexreader, cmudictreader
       >>> subtlexreader.download()
       Downloading http://expsy.ugent.be/subtlexus/SUBTLEXus74286wordstextversion.zip...
       Unzipping 'SUBTLEXus74286wordstextversion.zip'...
       >>> cmudictreader.download()
       Downloading https://cmusphinx.svn.sourceforge.net/svnroot/cmusphinx/trunk/cmudict/cmudict.0.7a...
       >>> prons = cmudictreader.CMUDict('cmudict.0.7a')
       >>> prons["constantine"]
       ['K', 'AA1', 'N', 'S', 'T', 'AH0', 'N', 'T', 'IY2', 'N']
       >>> freqs = subtlexreader.SubtlexDict('SUBTLEXus74286wordstextversion.txt')
       >>> freqs['the'].freq_count_low
       1339811


You can also use the ``download_corpora.py`` script to download all the publicly available data sets.
