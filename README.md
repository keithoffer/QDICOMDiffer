QDICOMDiffer 1.1.1
==================

A small cross-platform program to show DICOM metadata in a tree view, aswell as visually diff the metadata of two different DICOM files. I've only tested under Linux and Windows, but macOS should work aswell. If you don't want to run the python script itself, Windows [binary releases](https://github.com/keithoffer/QDICOMDiffer/releases) are available through github.

![Screenshot comparing two of the internationalized character set test DICOM images](Screenshots/main_screenshot.gif?raw=true)

Screenshot comparing two of the [internationalized character set test DICOM images](http://www.dclunie.com/images/charset/ ). 

Prerequisites
-------------
- python 3 (3.5 and 3.6 tested)

Python modules

- PyQt5 (5.7 tested)
- pydicom (0.9.9 and 1.0.0a1 tested)

Both are available through pip, however the version of pydicom on pypi is [rather out of date](https://github.com/darcymason/pydicom/issues/240), so moving to the unreleased 1.0.0 branch solves atleast one crash on a file I found in the wild. You can install the 1.0.0 branch of pydicom from github: 
```
pip install https://github.com/darcymason/pydicom/archive/master.zip 
```
Usage
-----
You can load images into the program in a couple of ways:

1. Through the File -> Open menu, where you can select one or two files to load in. If a file is already loaded and you select another, you'll be asked if you want it in the main or diff pane.
2. Drag and drop files onto the tree view in the application. The diff pane is hidden by default, but can be exanded by dragging it in from the right hand side.
3. As arguments to the program on invocation, e.g. ./QDICOMDiffer.py /path/to/file /path/to/file2

Note that if you try and load more than two files at once, any files beyond the first two are ignored.

Once two files are loaded, `File -> Diff` will begin the diffing process.

License
-------

QDICOMDiffer is copyrighted free software made available under the terms of the GPLv3

Copyright: (C) 2017 by Keith Offer. All Rights Reserved.
