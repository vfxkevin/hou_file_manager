# MIT License
#
# Copyright: (C) 2024 Kevin Ma Yi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import subprocess
from functools import partial

from PySide2.QtWidgets import QWidget, QFrame, QGroupBox
from PySide2.QtWidgets import (QAbstractItemView, QListView, QTreeView,
                               QHeaderView)
from PySide2.QtWidgets import (QPushButton, QLineEdit, QLabel,
                               QRadioButton)
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QScrollArea
from PySide2.QtWidgets import QTabWidget, QSplitter, QButtonGroup
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt

import hou
import resourceui

from . import constants as const
from .matchers import FileParm
from .hou_tree_model import HouParmTreeModel, HouNodeTreeModel


class FilePathManagerBrowser(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Models for the two views
        self._node_tree_model = None
        self._parm_tree_model = None

        # --------------- top section ---------------
        top_section_layout = self.build_top_section()

        # --------------- centre section ---------------
        centre_section_layout = self.build_center_section()

        # --------------- root layout ---------------
        root_layout = QVBoxLayout()
        root_layout.addLayout(top_section_layout)
        root_layout.addLayout(centre_section_layout)

        # set the root layout
        self.setLayout(root_layout)

    def set_up_node_tree_model(self, root_node):

        m = FileParm(parm_name='*',
                     file_type='image')
        path_list = [n.path() for n in
                     m.nodes(root_node, recursive=True)]

        self._node_tree_model = HouNodeTreeModel(path_list)
        self.ui_node_tree_view.setModel(self._node_tree_model)
        self.ui_node_tree_view.selectionModel().selectionChanged.connect(
            self.on_node_tree_view_selection_changed)

        # Configure tree view
        self.ui_node_tree_view.expandAll()
        self.ui_node_tree_view.resizeColumnToContents(0)

    def set_up_parm_tree_model(self):
        # Get the selected nodes from node tree view
        # Use selectedRows(0) because we just need one id per row.
        id_list = self.ui_node_tree_view.selectionModel().selectedRows(0)

        # Find all the filtered parms
        parm_list = []
        for index in id_list:
            node = (self._node_tree_model.get_item(index)
                    .get_raw_data().get_orig_data())
            for parm in node.globParms('*'):
                if not parm.isVisible():
                    continue

                pt = parm.parmTemplate()

                if not isinstance(pt, hou.StringParmTemplate):
                    continue

                if not pt.stringType() == hou.stringParmType.FileReference:
                    continue

                if pt.fileType().name().lower() == 'image':
                    parm_list.append(parm.path())

        # Update the parm tree view
        self._parm_tree_model = HouParmTreeModel(parm_list)
        self.ui_parm_tree_view.setModel(self._parm_tree_model)
        self._parm_tree_model.dataChanged.connect(
            self.on_parm_tree_data_changed)

        # Configure tree view
        self.ui_parm_tree_view.resizeColumnToContents(0)
        self.ui_parm_tree_view.setColumnWidth(1, 50)
        header = self.ui_parm_tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionsMovable(False)

        # Add file chooser button to all column 1 items.
        parm_root_index = self.ui_parm_tree_view.rootIndex()
        parm_row_count = self._parm_tree_model.rowCount(parm_root_index)
        for row in range(parm_row_count):
            # multiple buttons
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout()
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            file_chooser_button = hou.qt.FileChooserButton()
            preview_button = QPushButton('P')
            buttons_layout.addWidget(file_chooser_button)
            buttons_layout.addWidget(preview_button)
            buttons_widget.setLayout(buttons_layout)

            # add the widget to the item
            self.ui_parm_tree_view.setIndexWidget(
                self._parm_tree_model.index(row,1), buttons_widget)

            # add callbacks
            file_cb = partial(self.update_parm_model, row)
            file_chooser_button.fileSelected.connect(file_cb)

            preview_cb = partial(self.on_preview_file, row)
            preview_button.clicked.connect(preview_cb)

    def build_top_section(self):

        # create widgets
        self.ui_refresh_button = QPushButton('Refresh')
        self.ui_refresh_button.clicked.connect(self.on_refresh_tree_widget)

        # choose root node section
        root_path_layout = QHBoxLayout()
        root_path_label = QLabel('Search In Path:')
        self.ui_root_path_text = hou.qt.SearchLineEdit()
        self.ui_root_path_text.editingFinished.connect(self.on_refresh_tree_widget)
        choose_root_button = hou.qt.NodeChooserButton()
        choose_root_button.nodeSelected.connect(self.on_root_node_selected)
        root_path_layout.addWidget(root_path_label)
        root_path_layout.addWidget(self.ui_root_path_text)
        root_path_layout.addWidget(choose_root_button)

        # top section layout
        top_section_layout = QVBoxLayout()
        top_section_layout.addWidget(self.ui_refresh_button)
        top_section_layout.addLayout(root_path_layout)

        return top_section_layout

    def build_node_view_widget(self):
        # Top widget and layout
        node_view_top_widget = QWidget()
        node_view_layout = QHBoxLayout()

        # The tree view
        self.ui_node_tree_view = QTreeView()
        self.ui_node_tree_view.setAlternatingRowColors(True)
        self.ui_node_tree_view.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.ui_node_tree_view.setToolTip(
            'Node View:\n'
            '* Select nodes to show parameters details:\n'
            '   - This will NOT affect node selection in Houdini!\n'
            '   - Only highlighted nodes can be selected!\n'
            '   - Single-click the highlighted item to select single item.\n'
            '   - Click and drag to select multiple items.\n'
            '   - Use Ctrl + click to toggle selection of the items.\n'
            '   - Use Shift + click the start and end items for a range.\n'
            '* Double-click on an item to select it, set it to current \n'
            '  and show it in the Network View.\n'
            '   - This WILL affect node selection in Houdini!')
        self.ui_node_tree_view.doubleClicked.connect(
            self.on_node_tree_view_double_clicked)

        # Add tree view
        node_view_layout.addWidget(self.ui_node_tree_view)
        node_view_top_widget.setLayout(node_view_layout)

        return node_view_top_widget

    def build_parm_view_widget(self):
        # Top widget and layout
        parm_view_top_widget = QWidget()
        parm_view_layout = QHBoxLayout()

        # The tree view
        self.ui_parm_tree_view = QTreeView()
        self.ui_parm_tree_view.setAlternatingRowColors(True)
        self.ui_parm_tree_view.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.ui_parm_tree_view.setToolTip(
            'Parameter View:\n'
            '* To select parameter(s) for "Batch Processing" (right panel):\n'
            '   - Single-click the highlighted item to select single item.\n'
            '   - Click and drag to select multiple items.\n'
            '   - Use Ctrl + click to toggle selection of the items.\n'
            '   - Use Shift + click the start and end items for a range.\n'
            '* Use the file chooser buttons in the "Tools" column \n'
            '  to browse and choose files.\n'
            '* Double-click on an item of the "Raw Value" column to \n'
            '  edit them directly in place.')

        # Add to layout
        parm_view_layout.addWidget(self.ui_parm_tree_view)
        parm_view_top_widget.setLayout(parm_view_layout)

        return parm_view_top_widget

    def build_tools_n_log_widget(self):
        # create tab widget
        tools_n_log_top_widget = QTabWidget()

        # create the scroll area
        tools_scroll_area = QScrollArea()
        tools_scroll_area.setWidgetResizable(True)

        # Create widget and layout
        tools_widget = QWidget()
        tools_layout = QVBoxLayout()

        # create a GroupBox for multiple selections
        self.ui_grp_box_multi = QGroupBox(
            'Batch process:')
        parm_layout_grp_box_mlt = QVBoxLayout()
        self.ui_copy_or_move_combo = hou.qt.ComboBox()
        self.ui_copy_or_move_combo.addItem('Copy')
        self.ui_copy_or_move_combo.addItem('Move')
        selection_option_button_grp = QButtonGroup()
        self.ui_selected_parms_option = QRadioButton(
            'file(s) of selected parm(s)')
        self.ui_selected_parms_option.setChecked(True)
        self.ui_all_parms_option = QRadioButton('file(s) of all listed parm(s)')
        selection_option_button_grp.addButton(self.ui_selected_parms_option)
        selection_option_button_grp.addButton(self.ui_all_parms_option)
        label = QLabel(' and set Parm path(s) to:')
        hlayout = QHBoxLayout()
        self.ui_file_dest_dir = QLineEdit('$HIP/tex/')
        hlayout.addWidget(self.ui_file_dest_dir)
        dest_dir_browse = hou.qt.FileChooserButton()
        dest_dir_browse.setFileChooserFilter(hou.fileType.Directory)
        dest_dir_browse.setFileChooserTitle('Choose destination directory')
        hlayout.addWidget(dest_dir_browse)
        run_it = QPushButton('Run')
        run_it.clicked.connect(self.on_action_run_it)
        note_label = QLabel(
            'NOTE: Currently sequence files or UDIM files not supported.')
        parm_layout_grp_box_mlt.addWidget(self.ui_copy_or_move_combo)
        parm_layout_grp_box_mlt.addWidget(self.ui_selected_parms_option)
        parm_layout_grp_box_mlt.addWidget(self.ui_all_parms_option)
        parm_layout_grp_box_mlt.addWidget(label)
        parm_layout_grp_box_mlt.addLayout(hlayout)
        parm_layout_grp_box_mlt.addWidget(run_it)
        parm_layout_grp_box_mlt.addWidget(note_label)
        self.ui_grp_box_multi.setLayout(parm_layout_grp_box_mlt)

        # Add the GroupBox to the layout
        tools_layout.addWidget(self.ui_grp_box_multi)
        tools_layout.addStretch()

        # Set the layout and widget
        tools_widget.setLayout(tools_layout)

        # add to scroll area
        tools_scroll_area.setWidget(tools_widget)

        # create log widget
        log_scroll_area = QScrollArea()

        # add widgets to tab widget
        tools_n_log_top_widget.addTab(tools_scroll_area, "Tools")
        tools_n_log_top_widget.addTab(log_scroll_area, 'Logs')

        return tools_n_log_top_widget

    def build_center_section(self):

        # ==== centre section top widgets ====
        node_view_top_widget = self.build_node_view_widget()

        parm_view_top_widget = self.build_parm_view_widget()

        tools_n_log_top_widget = self.build_tools_n_log_widget()

        # ==== centre section layout ====
        centre_section_layout = QHBoxLayout()
        splitter = QSplitter()
        splitter.addWidget(node_view_top_widget)
        splitter.addWidget(parm_view_top_widget)
        splitter.addWidget(tools_n_log_top_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)
        centre_section_layout.addWidget(splitter)

        return centre_section_layout

    def on_root_node_selected(self, op_node):
        self.ui_root_path_text.setText(op_node.path())
        self.on_refresh_tree_widget()

    def on_node_tree_view_double_clicked(self, model_index: QModelIndex):

        node = self._node_tree_model.get_hou_object(model_index)
        if not node:
            return

        node.setCurrent(True, clear_all_selected=True)

    def on_node_tree_view_selection_changed(self, selected, deselected):
        self.set_up_parm_tree_model()

    def update_parm_model(self, row_id, path):
        if not path:
            return

        index = self._parm_tree_model.index(row_id, 2)
        self._parm_tree_model.setData(index, path, Qt.EditRole)

    def on_parm_tree_data_changed(self, top_left: QModelIndex,
                                  bottom_right: QModelIndex, roles):
        parm = (self._parm_tree_model.get_item(top_left)
                .get_raw_data().get_orig_data())

    def on_action_run_it(self):

        # Each item of the list is a tuple of
        # (id_of_column_0, id_of_column_2)

        id_list = None
        if self.ui_selected_parms_option.isChecked():
            col_0_list = self.ui_parm_tree_view.selectionModel().selectedRows(0)
            col_2_list = self.ui_parm_tree_view.selectionModel().selectedRows(2)
            id_list = list(zip(col_0_list, col_2_list))
            if not id_list:
                return

        elif self.ui_all_parms_option.isChecked():
            pass

        # Dest dir
        dest_dir = self.ui_file_dest_dir.text()
        expanded_dest_dir = hou.text.expandString(dest_dir)
        if not os.path.isdir(expanded_dest_dir):
            hou.ui.displayMessage('The expended dest dir does not exist: \n'
                                  '  --- Raw Path --- \n'
                                  '    {}\n'
                                  '  --- Expanded Path --- \n'
                                  '    {}\n'
                                  .format(dest_dir, expanded_dest_dir))
            return

        # Action
        file_action = self.ui_copy_or_move_combo.currentText().lower()
        if file_action not in const.FILE_ACTIONS:
            hou.ui.displayMessage('The action is not supported!\n'
                                  'Supported actions are : {}'
                                  .format(const.FILE_ACTIONS))
            return

        # Process
        # for parm in parm_list:
        for id_pair in id_list:

            # get parm from id
            parm = (self._parm_tree_model.get_item(id_pair[0])
                    .get_raw_data().get_orig_data())

            # Get source file first
            s_file = parm.eval()

            # Check the existence of the source file.
            if not s_file or not os.path.isfile(s_file):
                print('The source file does not exist:\n{}'.format(s_file))
                continue

            # Copy or move the file first.
            if file_action == const.FILE_ACTION_COPY:
                print('Copying source file:\n'
                      '    {}\n'
                      '  to destination dir:\n'
                      '    {}'
                      .format(s_file, expanded_dest_dir))
                shutil.copy(s_file, expanded_dest_dir)
            elif file_action == const.FILE_ACTION_MOVE:
                print('Moving source file:\n'
                      '    {}\n'
                      '  to destination dir:\n'
                      '    {}'
                      .format(s_file, expanded_dest_dir))
                shutil.move(s_file, expanded_dest_dir)
            else:
                print('The file action is not supported: \n{}'
                      .format(file_action))

            # New file path (it is not expanded), so MUST use the non-expanded
            # dest_dir !
            basename = os.path.basename(s_file)
            new_file_path = os.path.join(dest_dir, basename)

            # Check if new file exists before updating the parameter
            if not os.path.isfile(hou.text.expandString(new_file_path)):
                print('The new file does not exist: \n{}'.format(new_file_path))
                continue

            # Then set model data, the views will update automatically.
            self._parm_tree_model.setData(id_pair[1], new_file_path,
                                          Qt.EditRole)

    def on_preview_file(self, row_id):

        index = self._parm_tree_model.index(row_id, 2)
        print(row_id)
        parm = self._parm_tree_model.get_item(index).get_raw_data().get_orig_data()
        file_path = parm.eval()
        raw_value = parm.rawValue()
        print(file_path)
        if not file_path:
            return

        if not os.path.isfile(file_path):
            hou.ui.displayMessage('The file does not exist:\n'
                                  '  {}\n'
                                  '(Raw value: {})'.format(file_path, raw_value))
            return

        subprocess.Popen(['mplay', file_path])

    def on_refresh_tree_widget(self):
        root_path = self.ui_root_path_text.text()
        if not root_path:
            return

        root_node = hou.node(root_path)
        if not root_node:
            return

        self.set_up_node_tree_model(root_node)
        self.set_up_parm_tree_model()

