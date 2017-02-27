QDICOMDiffer 1.1.0
==================

A small cross-platform program to show DICOM metadata in a tree view, aswell as visually diff the metadata of two different DICOM files. I've only tested under Linux and Windows, but macOS should work aswell. If you don't want to run the python script itself, Windows [binary releases](https://github.com/keithoffer/QDICOMDiffer/releases) are available through github.

![Screenshot comparing two of the internationalized character set test DICOM images](Screenshots/main_screenshot.png?raw=true)

Screenshot comparing two of the [internationalized character set test DICOM images](http://www.dclunie.com/images/charset/ ). 

Prerequisites
-------------
- python 3 (3.5 and 3.6 tested)

Python modules

- PyQt5 (5.7 tested)
- pydicom (0.9.9 tested)

Both are available through pip. 

Usage
-----
You can load images into the program in a couple of ways:

1) Through the File -> Open menu, where you can select one or two files to load in. If a file is already loaded and you select another, you'll be asked if you want it in the main or diff pane.
2) Drag and drop files onto the tree view in the application. The diff pane is hidden by default, but can be exanded by dragging it in from the right hand side.
3) As arguments to the program on invocation, e.g. ./QDICOMDiffer.py /path/to/file /path/to/file2

Note that if you try and load more than two files at once, any files beyond the first two are ignored.

License
-------

QDICOMDiffer is copyrighted free software made available under the terms of the GPLv3

Copyright: (C) 2017 by Keith Offer. All Rights Reserved.