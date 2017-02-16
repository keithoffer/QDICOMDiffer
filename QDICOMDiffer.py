#!/usr/bin/env python3
"""
    QDICOMDiffer - a small program to view and diff the metadata of DICOM images
    Copyright 2017 Keith Offer

    QDICOMDiffer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 3 as published by
    the Free Software Foundation.

    QDICOMDiffer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with QDICOMDiffer.  If not, see <http://www.gnu.org/licenses/>.
"""
# Imports include comments to indicate their respective licences
# pydicom is MIT licenced
import dicom
# PyQt is GPL v3 licenced
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPainter, QFontMetrics
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAbstractItemView, QProgressBar, QLabel, QTreeView, QScrollBar, \
    QPushButton
from PyQt5.QtCore import QSettings, Qt, QSortFilterProxyModel, QThread, pyqtSignal
# Python standard library is PSF licenced
import sys
import difflib
import re
import os
# Other files from this project
from ui.mainWindow import Ui_MainWindow

indirect_match_colour = QColor(179, 206, 236)
direct_match_colour = QColor(140, 183, 225)
GLOBAL_integer_key = 0  # key used to insure all nodes have unique id's
version = '1.0.1'

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.modelArray = [QStandardItemModel(), QStandardItemModel()]
        self.filterProxyArray = [RecursiveProxyModel(), RecursiveProxyModel()]
        self.treeViewArray = [self.ui.treeView, self.ui.treeView_2]
        self.pathLabelArray = [self.ui.labelPath, self.ui.labelPath_2]

        self.setWindowTitle('QDICOMDiffer ' + version)

        for i in range(2):
            self.modelArray[i].setHorizontalHeaderLabels(['Tag', 'Description', 'Value', 'Different', 'Index'])
            self.filterProxyArray[i].setSourceModel(self.modelArray[i])
            self.ui.lineEditTagFilter.textChanged.connect(self.filterProxyArray[i].set_tag_filter)
            self.ui.lineEditDescFilter.textChanged.connect(self.filterProxyArray[i].set_desc_filter)
            self.ui.lineEditValFilter.textChanged.connect(self.filterProxyArray[i].set_value_filter)
            self.treeViewArray[i].setModel(self.filterProxyArray[i])
            self.treeViewArray[i].setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.treeViewArray[i].setColumnHidden(3, True)
            self.treeViewArray[i].setColumnHidden(4, True)
            # the i=i here is needed to ensure i is within the local namespace, without it i evaluates to 1 both times
            self.ui.checkBoxShowOnlyDifferent.stateChanged.connect(
                lambda state, i=i: self.filterProxyArray[i].set_show_only_different(bool(
                    state)))
            self.treeViewArray[i].file_dropped.connect(lambda filepath, i=i: self.load_file(filepath, i))

        self.ui.splitter.setSizes([100, 0])

        self.ui.actionOpen.triggered.connect(self.open_files)
        self.ui.actionDiff.triggered.connect(self.do_diff)
        self.ui.actionHTML_diff.triggered.connect(self.open_html_diff_window)
        self.ui.actionAbout.triggered.connect(self.open_about_window)
        self.raw_diff_window = None
        self.html_diff_window = None
        self.ui.actionText_diff.triggered.connect(self.open_text_diff_window)
        self.ui.actionExpand_all.triggered.connect(self.expand_all)
        self.ui.actionCollapse_all.triggered.connect(self.collapse_all)
        self.dc_array = [None] * 2

        self.diff_result = None
        self.html_diff_result = None

        # Read the settings from the settings.ini file
        system_location = os.path.dirname(os.path.abspath(sys.argv[0]))
        QSettings.setPath(QSettings.IniFormat, QSettings.SystemScope, system_location)
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        if os.path.exists(system_location + "/settings.ini"):
            print("Loading from " + system_location + "/settings.ini")

        # If we were given command line arguments, try and load them
        arguments = sys.argv[1:]
        for number, line in enumerate(arguments):
            self.load_file(line, number)
            # Only ever handle two files
            if number == 1:
                self.ui.splitter.setSizes([50, 50])
                break

        self.show()

    def open_about_window(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("About")
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setText("QDICOMDiffer version " + version +
                       "<br> Written by Keith Offer" +
                       "<br> Relies heavily on the <a href='http://www.pydicom.org/'>pydicom</a> library")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.exec()

    def open_text_diff_window(self):
        if self.diff_result is not None:
            self.raw_diff_window = TextDiffWindow(self.diff_result)
        else:
            if self.dc_array[0] is not None and self.dc_array[0] is not None:
                self.ui.splitter.setSizes([50, 50])
                self.do_diff()
                # Note that the IDE complains that self.diff_result is still None here
                # It should have a value set by self.do_diff(), so this is not the case
                if self.diff_result is not None:
                    self.raw_diff_window = TextDiffWindow(self.diff_result)

    def open_html_diff_window(self):
        if self.html_diff_result is not None:
            self.html_diff_window = HTMLDiffWindow(self.html_diff_result)
        else:
            if self.dc_array[0] is not None and self.dc_array[0] is not None:
                self.ui.splitter.setSizes([50, 50])
                self.do_diff()
                # Note that the IDE complains that self.diff_result is still None here
                # It should have a value set by self.do_diff(), so this is not the case
                if self.diff_result is not None:
                    self.html_diff_window = HTMLDiffWindow(self.html_diff_result)

    def collapse_all(self):
        for i in range(2):
            self.treeViewArray[i].collapseAll()
            for n in range(3):
                self.treeViewArray[i].resizeColumnToContents(n)

    def expand_all(self):
        for i in range(2):
            self.treeViewArray[i].expandAll()
            for n in range(3):
                self.treeViewArray[i].resizeColumnToContents(n)
                self.treeViewArray[i].resizeColumnToContents(n)

    def set_value_filter(self, filter):
        for i in range(2):
            self.filterProxyArray[i].setFilterKeyColumn(2)
            self.filterProxyArray[i].setFilterFixedString(filter)

    def show_only_diff(self, new_state):
        state = (new_state == 2)
        for i in range(2):
            self.filterProxyArray[i].setFilterKeyColumn(3)
            if state:
                self.filterProxyArray[i].setFilterFixedString(str(int(state)))
            else:
                self.filterProxyArray[i].setFilterFixedString('')

    def open_files(self):
        filepaths = self.get_file_paths()

        if len(filepaths) > 2:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText('Ignoring all but the first two files')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec()

        if len(filepaths) != 0:
            folder = os.path.dirname(filepaths[0])
            if os.path.exists(folder):
                self.settings.setValue('Browse/LastOpenedLocation', folder)

        if len(filepaths) == 1:
            filepath = filepaths[0]
            if self.dc_array[0] is not None:
                # We are loading a file and there is already one loaded. Do we want to just view or diff?
                msgBox = QMessageBox()
                msgBox.setText(
                    "A file is already loaded. Do you want to diff with the currently loaded file or just load the new file?")
                load_button = QPushButton('Just load the new file')
                msgBox.addButton(load_button, QMessageBox.YesRole)
                diff_button = QPushButton('Diff with the currently loaded file')
                msgBox.addButton(diff_button, QMessageBox.NoRole)
                msgBox.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
                msgBox.exec()
                # Note if no button was pressed, no action is taken
                if msgBox.clickedButton() == load_button:
                    self.load_file(filepath, 0)
                elif msgBox.clickedButton() == diff_button:
                    self.load_file(filepath, 1)
                    self.ui.splitter.setSizes([50, 50])
                else:
                    pass
                return

        for file_number, filepath in enumerate(filepaths):
            self.load_file(filepath, file_number)
            if file_number == 1:
                # If more than two files selected, just break after handling the first two
                self.ui.splitter.setSizes([50, 50])
                break

    def get_file_paths(self):
        path_from_settings = self.settings.value('Browse/LastOpenedLocation')
        default_location = '.'
        if path_from_settings is not None:
            if os.path.exists(self.settings.value('Browse/LastOpenedLocation')):
                default_location = self.settings.value('Browse/LastOpenedLocation')
        """
        This looks a bit strange, but filenames are the first return value of this function
        so we need the [0] on the end to grab what we need
        """
        return QFileDialog.getOpenFileNames(self, 'Open DICOM file ...', default_location)[0]

    def load_file(self, filepath, file_number):
        try:
            dc = dicom.read_file(filepath)
            self.dc_array[file_number] = dc
            self.modelArray[file_number].removeRows(0, self.modelArray[
                file_number].rowCount())  # Remove any rows from old loaded files
            dict_to_tree(dc, parent=self.modelArray[file_number].invisibleRootItem())
            self.pathLabelArray[file_number].setText(filepath)
            for n in range(3):
                self.treeViewArray[file_number].resizeColumnToContents(n)
                if file_number == 1:
                    reset_tree_diff_state(self.modelArray[0].invisibleRootItem())
                else:
                    reset_tree_diff_state(self.modelArray[1].invisibleRootItem())
                self.diff_result = None
                self.html_diff_result = None
        except dicom.errors.InvalidDicomError:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Error")
            msgBox.setText('Failed to open ' + filepath + ' (is it a valid DICOM file?)')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec()

    def do_diff(self):
        self.diffProgressWindow = DiffProgressWindow(self.dc_array, self.modelArray, parent=self)
        if self.diffProgressWindow.exec():
            self.html_diff_result = self.diffProgressWindow.get_html_diff_result()
            self.diff_result = self.diffProgressWindow.get_diff_result()

# Class taken from stackoverflow user Eric Hulser, url: http://stackoverflow.com/a/11764662
class EnhancedQLabel(QLabel):
    def __init__(self, parent=None):
        super(EnhancedQLabel, self).__init__(parent)

    def setText(self, text):
        self.setToolTip(text)
        super(EnhancedQLabel, self).setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)

        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideMiddle, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)

class DiffProgressWindow(QtWidgets.QDialog):
    def __init__(self, dc_array, model_array, parent=None):
        super(DiffProgressWindow, self).__init__(parent)
        self.progressBar = QProgressBar()
        self.label = QLabel("Diffing ...")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label, alignment=Qt.AlignVCenter)
        self.layout.addWidget(self.progressBar, alignment=Qt.AlignVCenter)
        self.setLayout(self.layout)
        self.setWindowTitle('Diff progress')

        self.diff_result = None
        self.html_diff_result = None

        self.show()

        self.workerThread = DiffWorkerThread(dc_array, model_array)
        self.workerThread.lines_to_process.connect(lambda num_of_lines: self.progressBar.setMaximum(num_of_lines))
        self.workerThread.current_line.connect(lambda line: self.progressBar.setValue(line))
        self.workerThread.start()
        self.workerThread.finished.connect(self.handle_finished)

    def handle_finished(self, html_diff_result, diff_result):
        self.html_diff_result = html_diff_result
        self.diff_result = diff_result
        self.accept()

    def get_html_diff_result(self):
        return self.html_diff_result

    def get_diff_result(self):
        return self.diff_result


class DiffWorkerThread(QThread):
    """
    Worker thread that does the diffing and highlighting of nodes
    """

    def __init__(self, dc_array, modelArray):
        super(DiffWorkerThread, self).__init__()
        self.dc_array = dc_array
        self.modelArray = modelArray
        self.lines_processed = 0

    def run(self):
        # To diff the two dictionaries with difflib, they need to be a list of lines terminated with \n
        # Code taken from the DicomDiff example from pydicom, which can be found at the following url
        # https://github.com/darcymason/pydicom/blob/master/pydicom/examples/DicomDiff.py
        rep = []
        for dataset in self.dc_array:
            lines = str(dataset).split("\n")
            lines = [line + "\n" for line in lines]  # add the newline to end
            rep.append(lines)

        htmldiff = difflib.HtmlDiff()
        self.html_diff_result = htmldiff.make_file(rep[0], rep[1])

        diff = difflib.Differ()
        # We do this diff because this looks nicer, and use this copy to display to the user as the 'raw diff'
        self.diff_result = list(diff.compare(rep[0], rep[1]))

        columns_to_save = [0, 1, 2]
        index_col = 4

        # Note that here a variabled ending in _2 refers to the file / pane on the right
        string_representation_unkeyed = []
        tree_to_string_list(self.modelArray[0].invisibleRootItem(), string_representation_unkeyed, columns_to_save)
        list_of_keys = []
        tree_to_string_list(self.modelArray[0].invisibleRootItem(), list_of_keys, [index_col])

        string_representation_2_unkeyed = []
        tree_to_string_list(self.modelArray[1].invisibleRootItem(), string_representation_2_unkeyed, columns_to_save)
        list_of_keys_2 = []
        tree_to_string_list(self.modelArray[1].invisibleRootItem(), list_of_keys_2, [index_col])

        # If we don't convert to a list here, we can only iterate over the result once as it returns generators
        unkeyed_diff_list = list(diff.compare(string_representation_unkeyed, string_representation_2_unkeyed))

        list_old_stuff = []
        list_old_stuff_2 = []
        for line in unkeyed_diff_list:
            if not line.startswith('?') and not line.startswith('+'):
                list_old_stuff.append(line)
            if not line.startswith('?') and not line.startswith('-'):
                list_old_stuff_2.append(line)

        diff_list_with_keys = []
        for i in range(len(list_old_stuff)):
            if i % 3 == 0:
                diff_list_with_keys.append(list_of_keys[int(i / 3)])
            diff_list_with_keys.append(list_old_stuff[i])

        diff_list_with_keys_2 = []
        for i in range(len(list_old_stuff_2)):
            if i % 3 == 0:
                diff_list_with_keys_2.append(list_of_keys_2[int(i / 3)])
            diff_list_with_keys_2.append(list_old_stuff_2[i])

        num_lines = len(diff_list_with_keys) + len(diff_list_with_keys_2)
        self.lines_to_process.emit(num_lines)
        self.highlight_nodes(diff_list_with_keys, self.modelArray[0], '-')
        self.highlight_nodes(diff_list_with_keys_2, self.modelArray[1], '+')
        self.finished.emit(self.html_diff_result, self.diff_result)

    # TODO: This was designed before I learnt about QModelIndex. It might be faster if redesigned to use that
    def highlight_nodes(self, diff_list, model, plus_or_minus):
        find_identifier_regex = r':\s(.*$)'  # Extracts the identifier from the index line in match group 0
        identifier = 'NOT_SET'
        for line_number, line in enumerate(diff_list):
            self.lines_processed += 1
            self.current_line.emit(self.lines_processed)
            # Save the last seen index, so when we need to go find a node, we know it's index
            if '# INDEX' in line:
                identifier = re.findall(find_identifier_regex, line)[0]
            # Handle lines that were different between the two files
            elif line.startswith(plus_or_minus):
                # Use the index we saved to find the node in the tree
                node = search_nodes_recursively(model.invisibleRootItem(),
                                                '# INDEX: ' + str(identifier), 4)
                if node is not None:
                    # Mark the row as an exact match
                    node_children = get_children(node, model)
                    node_children[3].setText('1')

                    # Mark all parent rows as an indirect match
                    list_of_parents = []
                    get_all_parents(node, list_of_parents)
                    for parent in list_of_parents:
                        node_children = get_children(parent, model)
                        if node_children[3].text() != 1:
                            node_children[3].setText('2')

    lines_to_process = pyqtSignal(int, name='lines_to_process')
    current_line = pyqtSignal(int, name='current_line')
    finished = pyqtSignal(object, object, name='finished')


class TextDiffWindow(QtWidgets.QWidget):
    def __init__(self, diff):
        super(TextDiffWindow, self).__init__()
        self.textEdit = QtWidgets.QTextEdit()
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.textEdit)
        self.textEdit.setReadOnly(True)
        self.setWindowTitle('Text diff')

        for line in diff:
            if line.startswith('+'):
                self.textEdit.setTextColor(Qt.darkGreen)
            elif line.startswith('-'):
                self.textEdit.setTextColor(Qt.red)
            elif line.startswith('?'):
                self.textEdit.setTextColor(Qt.darkYellow)
            else:
                self.textEdit.setTextColor(Qt.black)
            self.textEdit.append(line)

        self.setLayout(self.layout)
        self.resize(600, 700)

        self.show()
        self.textEdit.verticalScrollBar().triggerAction(QScrollBar.SliderToMinimum)


class HTMLDiffWindow(QtWidgets.QWidget):
    def __init__(self, diff):
        super(HTMLDiffWindow, self).__init__()

        self.textEdit = QtWidgets.QTextEdit()
        self.horLayout = QtWidgets.QVBoxLayout()
        self.horLayout.addWidget(self.textEdit)
        self.textEdit.setReadOnly(True)
        self.textEdit.setHtml(diff)
        self.setLayout(self.horLayout)
        self.setWindowTitle('HTML diff')

        self.show()
        self.raise_()  # sometimes the window doesn't appear on top for some reason
        self.resize(600, 700)


class DroppableTreeView(QTreeView):
    """
    A subclass of QTreeView that emits the file location of files dropped on it
    """

    def __init__(self, *args):
        super(DroppableTreeView, self).__init__(*args)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            self.file_dropped.emit(event.mimeData().urls()[0].toLocalFile())
        else:
            event.ignore()

    def drawRow(self, painter, options, index):
        if index.sibling(index.row(), 3).data() == '1':
            painter.fillRect(options.rect, direct_match_colour)
        if index.sibling(index.row(), 3).data() == '2':
            painter.fillRect(options.rect, indirect_match_colour)
        super(DroppableTreeView, self).drawRow(painter, options, index)

    file_dropped = pyqtSignal(str, name='file_dropped')


class RecursiveProxyModel(QSortFilterProxyModel):
    """
    A subclass of QSortFilterProxyModel that does recursive and multi column filtering
    """

    def __init__(self):
        super(RecursiveProxyModel, self).__init__()
        self._show_only_different = False
        self._value_filter = ''
        self._tag_filter = ''
        self._desc_filter = ''

    def set_value_filter(self, new_filter):
        self._value_filter = new_filter
        self.invalidateFilter()

    def set_desc_filter(self, new_filter):
        self._desc_filter = new_filter
        self.invalidateFilter()

    def set_tag_filter(self, new_filter):
        self._tag_filter = new_filter
        self.invalidateFilter()

    def set_show_only_different(self, new_bool):
        self._show_only_different = new_bool
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if self.row_matches_filters(source_row, source_parent):
            # TODO: Change matched row to make it show up differently. Perhaps underline / italics?
            return True

        # We also want a node to be visible if it has any children that match (otherwise you won't be able to see those
        # matches
        return self.has_matching_children(source_row, source_parent)

    def row_matches_filters(self, row_num, parent):
        model = self.sourceModel()
        parent_obj = model.itemFromIndex(parent)
        if parent_obj is not None:
            tag = parent_obj.child(row_num, 0).text()
            desc = parent_obj.child(row_num, 1).text()
            value = parent_obj.child(row_num, 2).text()
            different = parent_obj.child(row_num, 3).text()
        else:
            tag = model.item(row_num, 0).text()
            desc = model.item(row_num, 1).text()
            value = model.item(row_num, 2).text()
            different = model.item(row_num, 3).text()

        accepted = self._tag_filter in tag and self._desc_filter in desc and self._value_filter in value
        if self._show_only_different:
            accepted = accepted and ( different == '1' or different == '2')

        return accepted

    def has_matching_children(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, parent=source_parent)
        number_of_children = model.rowCount(index)
        for i in range(number_of_children):
            if self.filterAcceptsRow(i, index):
                return True
        return False


def dict_to_tree(dc, parent=None):
    """
    Fills a Qt tree data structure with a pydicom dictionary. I was unsure exactly what layout to use, so I mainly copied
    the structure used by the the pydicom tree example using wxwidgets, avaiable here:
    https://github.com/darcymason/pydicom/blob/dev/pydicom/examples/dicomtree.py
    """
    # This regex is used to match a memory offset used in the description of pydicom sequences
    sequence_regex = r',\sat\s[0-9A-F]{7}'  # comma, whitespace, the word 'at', whitespace, followed by seven hex digits
    for data_element in dc:
        tag = str(data_element.tag)
        desc = data_element.description()
        value = str(data_element).replace(desc, '').replace(tag, '').strip()
        """
        This is a weird one. By default, pydicom includes a memory offset which we need to remove because it is
        non deterministic. Any non-deterministic stuff in the description will make diffing two files impossible.
        More info here https://github.com/darcymason/pydicom/issues/107
        """
        value = re.sub(sequence_regex, '', value)
        new_child = QStandardItem(tag)

        parent.appendRow([new_child, QStandardItem(desc),
                          QStandardItem(value),
                          QStandardItem('0'),
                          QStandardItem("# INDEX: " + str(get_unique_value()))])
        if data_element.VR == "SQ":
            if len(data_element.value) != 0:
                for i, dataset in enumerate(data_element.value):
                    sq_item_description = data_element.name.replace(" Sequence", "")  # XXX not i18n
                    item_text = "{0:s} {1:d}".format(sq_item_description, i + 1)
                    child = QStandardItem()
                    new_child.appendRow(
                        [child, QStandardItem(sq_item_description), QStandardItem(item_text), QStandardItem('0'),
                         QStandardItem("# INDEX: " + str(get_unique_value()))])
                    dict_to_tree(dataset, parent=child)
            else:
                pass


def get_children(node, model):
    children = []
    if node is not None:
        parent = node.parent()
        row = node.row()
        if parent is not None:
            for column in range(5):
                children.append(parent.child(row, column))
        else:
            for column in range(5):
                children.append(model.item(row, column))

    return children


def reset_tree_diff_state(node):
    """
    Resets the diff state on all children of a node, to any depth
    """
    if node is not None:
        row_count = node.rowCount()
        for row in range(row_count):
            node.child(row, 3).setText('0')
            reset_tree_diff_state(node.child(row,0))

def search_nodes_recursively(node, token, column):
    """
    Searches a node and all of it's children for a value of 'token' on column 'column'
    """
    match = None
    if node is not None:
        row_count = node.rowCount()
        for row in range(row_count):
            if node.child(row, column).text() == token:
                match = node.child(row, column)
                return match
            else:
                match = search_nodes_recursively(node.child(row, 0), token, column)
                if match is not None:
                    return match
    return match


def get_all_parents(node, list_of_nodes):
    parent = node.parent()
    if parent is not None:
        list_of_nodes.append(parent)
        get_all_parents(parent, list_of_nodes)
    else:
        return


def get_unique_value():
    global GLOBAL_integer_key
    # Just a simple integer unique key
    value = GLOBAL_integer_key
    GLOBAL_integer_key += 1
    return value


def tree_to_string_list(node, string_representation, columns_to_save, ):
    for i in range(node.rowCount()):
        for j in columns_to_save:
            string_representation.append(node.child(i, j).text())
        tree_to_string_list(node.child(i), string_representation, columns_to_save)


if __name__ == '__main__':
    if sys.platform.startswith('linux'):
        if os.geteuid() == 0:
            print("This program should not be run as root, exiting ...")
            sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    GUI = MainWindow()
    sys.exit(app.exec())
