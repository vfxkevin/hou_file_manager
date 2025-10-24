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
import subprocess
from functools import partial

from .py_ui import QtWidgets, QtCore

import hou
import nodesearch

from . import constants as const
from . import matchers
from . import utils
from .hou_tree_model import HouParmTreeModel, HouNodeTreeModel


class NodeParmFilterList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        self._filter_rows = []

    def add_filter_row(self, filter_type):
        pass

    def remove_filter_row(self, filter_row_obj):
        pass

    def matches_all(self):
        return None

    def matchers(self):
        matchers = []
        for filter in self._filter_rows:
            matcher = filter.matcher()
            if not matcher:
                raise Exception('Filter ({}) does not have a matcher.'
                                .format(filter))
            matchers.append(matcher)

        return matchers


class FilePathManagerBrowser(QtWidgets.QFrame):
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
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addLayout(top_section_layout, stretch=0)
        root_layout.addLayout(centre_section_layout, stretch=1)

        # set the root layout
        self.setLayout(root_layout)

    def set_up_node_tree_model(self, path_list):

        self._node_tree_model = HouNodeTreeModel(path_list)
        self.ui_node_tree_view.setModel(self._node_tree_model)
        self.ui_node_tree_view.selectionModel().selectionChanged.connect(
            self.on_node_tree_view_selection_changed)

        # Configure tree view
        self.ui_node_tree_view.expandAll()
        self.ui_node_tree_view.resizeColumnToContents(0)

    def set_up_parm_tree_model(self, parm_list):

        # Update the parm tree view
        self._parm_tree_model = HouParmTreeModel(parm_list)
        self.ui_parm_tree_view.setModel(self._parm_tree_model)
        self._parm_tree_model.dataChanged.connect(
            self.on_parm_tree_data_changed)

    def node_tree_view_config_post_model_setup(self):

        # Configure tree view
        self.ui_parm_tree_view.resizeColumnToContents(0)
        self.ui_parm_tree_view.setColumnWidth(1, 50)
        header = self.ui_parm_tree_view.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionsMovable(False)

        # Add file chooser button to all column 1 items.
        parm_root_index = self.ui_parm_tree_view.rootIndex()
        parm_row_count = self._parm_tree_model.rowCount(parm_root_index)
        for row in range(parm_row_count):
            # multiple buttons
            buttons_widget = QtWidgets.QWidget()
            buttons_layout = QtWidgets.QHBoxLayout()
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            file_chooser_button = hou.qt.FileChooserButton()
            # get orig data
            index = self._parm_tree_model.index(row, 0)
            parm = (self._parm_tree_model.get_item(index)
                    .get_raw_data().get_orig_data())
            if matchers.parm_is_file_type(parm, 'image'):
                file_chooser_button.setFileChooserFilter(hou.fileType.Image)
                file_chooser_button.setFileChooserIsImageChooser(True)
            elif matchers.parm_is_file_type(parm, 'geometry'):
                file_chooser_button.setFileChooserFilter(hou.fileType.Geometry)
            preview_button = QtWidgets.QPushButton('P')
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
        self.ui_refresh_button = QtWidgets.QPushButton('Refresh')
        self.ui_refresh_button.clicked.connect(self.on_refresh)

        # choose root node section
        root_path_layout = QtWidgets.QHBoxLayout()
        root_path_label = QtWidgets.QLabel('Search In Path:')
        self.ui_root_path_text = hou.qt.SearchLineEdit()
        self.ui_root_path_text.editingFinished.connect(self.on_refresh)
        choose_root_button = hou.qt.NodeChooserButton()
        choose_root_button.nodeSelected.connect(self.on_root_node_selected)
        root_path_layout.addWidget(root_path_label)
        root_path_layout.addWidget(self.ui_root_path_text)
        root_path_layout.addWidget(choose_root_button)

        # filter layout
        filter_grp_box = QtWidgets.QGroupBox('Filters')
        filter_layout = QtWidgets.QVBoxLayout()

        # node filter layout
        node_filter_layout = QtWidgets.QHBoxLayout()
        node_filter_layout.setSpacing(20)

        # Node name filter
        node_name_filter_layout = QtWidgets.QHBoxLayout()
        node_name_filter_layout.setSpacing(5)
        node_name_label = QtWidgets.QLabel('Node Name:')
        self.ui_node_name_filter_text = QtWidgets.QLineEdit('*')
        self.ui_node_name_filter_text.editingFinished.connect(self.on_refresh)
        node_name_filter_layout.addWidget(node_name_label)
        node_name_filter_layout.addWidget(self.ui_node_name_filter_text)

        # Node type filter
        node_type_filter_layout = QtWidgets.QHBoxLayout()
        node_type_filter_layout.setSpacing(5)
        node_type_label = QtWidgets.QLabel('Node Type:')
        self.ui_node_type_category_combo = hou.qt.ComboBox()

        cate = list(hou.nodeTypeCategories().items())
        for c in (hou.managerNodeTypeCategory(), hou.rootNodeTypeCategory()):
            cate.remove((c.name(), c))
        cate.insert(0, ("*", None))
        cate.sort()
        for c in cate:
            self.ui_node_type_category_combo.addItem(c[0], c[1])
        self.ui_node_type_category_combo.setMinimumWidth(80)
        self.ui_node_type_category_combo.currentTextChanged.connect(
            self.on_node_type_category_changed)

        self.ui_node_type_combo = hou.qt.ComboBox()
        self.ui_node_type_combo.setEditable(True)
        self.ui_node_type_combo.addItem('*')
        self.ui_node_type_combo.setMinimumWidth(200)
        self.ui_node_type_combo.currentTextChanged.connect(self.on_refresh)
        node_type_filter_layout.addWidget(node_type_label)
        node_type_filter_layout.addWidget(self.ui_node_type_category_combo)
        node_type_filter_layout.addWidget(self.ui_node_type_combo, stretch=1)

        # add to node filter layout
        node_filter_layout.addLayout(node_name_filter_layout, stretch=1)
        node_filter_layout.addLayout(node_type_filter_layout, stretch=1)

        # parm filter layout
        parm_filter_layout = QtWidgets.QHBoxLayout()
        parm_filter_layout.setSpacing(20)

        # Parm name filter
        parm_name_filter_layout = QtWidgets.QHBoxLayout()
        parm_name_filter_layout.setSpacing(5)
        parm_name_label = QtWidgets.QLabel('Parm Name:')
        self.ui_parm_name_filter_text = QtWidgets.QLineEdit('*')
        self.ui_parm_name_filter_text.editingFinished.connect(self.on_refresh)
        parm_name_filter_layout.addWidget(parm_name_label)
        parm_name_filter_layout.addWidget(self.ui_parm_name_filter_text)

        # Parm File type filter
        parm_file_type_filter_layout = QtWidgets.QHBoxLayout()
        parm_file_type_filter_layout.setSpacing(5)
        file_type_label = QtWidgets.QLabel('Parm File Type:')
        parm_file_type_filter_layout.addWidget(file_type_label)
        self.ui_file_type_combo = hou.qt.ComboBox()
        self.ui_file_type_combo.addItem('Image')
        self.ui_file_type_combo.addItem('Geometry')
        self.ui_file_type_combo.currentTextChanged.connect(self.on_refresh)
        parm_file_type_filter_layout.addWidget(self.ui_file_type_combo)
        parm_file_type_filter_layout.addStretch()

        # add to parm filter layout
        parm_filter_layout.addLayout(parm_name_filter_layout, stretch=1)
        parm_filter_layout.addLayout(parm_file_type_filter_layout, stretch=1)

        # add to filter layout
        filter_layout.addLayout(node_filter_layout)
        filter_layout.addLayout(parm_filter_layout)

        # set layout
        filter_grp_box.setLayout(filter_layout)

        # top section layout
        top_section_layout = QtWidgets.QVBoxLayout()
        top_section_layout.addWidget(self.ui_refresh_button)
        top_section_layout.addLayout(root_path_layout)
        top_section_layout.addWidget(filter_grp_box)

        return top_section_layout

    def build_node_view_widget(self):
        # Top widget and layout
        node_view_top_widget = QtWidgets.QWidget()
        node_view_layout = QtWidgets.QHBoxLayout()

        # The tree view
        self.ui_node_tree_view = QtWidgets.QTreeView()
        self.ui_node_tree_view.setAlternatingRowColors(True)
        self.ui_node_tree_view.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
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
        parm_view_top_widget = QtWidgets.QWidget()
        parm_view_layout = QtWidgets.QHBoxLayout()

        # The tree view
        self.ui_parm_tree_view = QtWidgets.QTreeView()
        self.ui_parm_tree_view.setAlternatingRowColors(True)
        self.ui_parm_tree_view.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
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
        tools_n_log_top_widget = QtWidgets.QTabWidget()

        # create the scroll area
        tools_scroll_area = QtWidgets.QScrollArea()
        tools_scroll_area.setWidgetResizable(True)

        # Create widget and layout
        tools_widget = QtWidgets.QWidget()
        tools_layout = QtWidgets.QVBoxLayout()

        # create a GroupBox for batch process files
        self.ui_batch_process_grp_box = QtWidgets.QGroupBox('Batch Processing')
        batch_process_grp_box_layout = QtWidgets.QVBoxLayout()

        # radio group
        selection_hlayout = QtWidgets.QHBoxLayout()
        repath_label = QtWidgets.QLabel("Repath :")
        selection_option_button_grp = QtWidgets.QButtonGroup()
        self.ui_selected_parms_option = QtWidgets.QRadioButton('Selected parm(s)')
        self.ui_selected_parms_option.setChecked(True)
        self.ui_all_parms_option = QtWidgets.QRadioButton('All listed parm(s)')
        selection_option_button_grp.addButton(self.ui_selected_parms_option)
        selection_option_button_grp.addButton(self.ui_all_parms_option)
        selection_hlayout.addWidget(repath_label)
        selection_hlayout.addWidget(self.ui_selected_parms_option)
        selection_hlayout.addWidget(self.ui_all_parms_option)
        selection_hlayout.setStretch(0, 1)
        selection_hlayout.setStretch(1, 1)
        selection_hlayout.setStretch(2, 1)

        string_replace_grp_box = QtWidgets.QGroupBox('String Replace')
        string_replace_grp_box_layout = QtWidgets.QVBoxLayout()

        pattern_label = QtWidgets.QLabel("Pattern string:")
        pattern_hlayout = QtWidgets.QHBoxLayout()
        self.ui_pattern_str = QtWidgets.QLineEdit('')
        pattern_path_browse = hou.qt.FileChooserButton()
        pattern_path_browse.setFileChooserFilter(hou.fileType.Directory)
        pattern_path_browse.setFileChooserTitle('Choose source directory')
        pattern_path_browse.fileSelected.connect(self.on_pattern_path_browse)
        pattern_hlayout.addWidget(self.ui_pattern_str)
        pattern_hlayout.addWidget(pattern_path_browse)

        replacement_label = QtWidgets.QLabel('Replacement string:')
        replacement_hlayout = QtWidgets.QHBoxLayout()
        self.ui_replacement_str = QtWidgets.QLineEdit('$HIP/tex/')
        replacement_path_browse = hou.qt.FileChooserButton()
        replacement_path_browse.setFileChooserFilter(hou.fileType.Directory)
        replacement_path_browse.setFileChooserTitle(
            'Choose destination directory')
        replacement_path_browse.fileSelected.connect(
            self.on_replacement_path_browse)
        replacement_hlayout.addWidget(self.ui_replacement_str)
        replacement_hlayout.addWidget(replacement_path_browse)

        syntax_layout = QtWidgets.QHBoxLayout()
        syntax_label = QtWidgets.QLabel('Function to use :')
        self.ui_syntax_combo_box = hou.qt.ComboBox()
        for func_tuple in const.STR_REPLACE_FUNCS:
            self.ui_syntax_combo_box.addItem(func_tuple[0])
        # syntax_count_label = QLabel('Count :')
        # self.ui_syntax_count = QLineEdit('-1')
        # vali = QIntValidator()
        # vali.setBottom(-1)
        # self.ui_syntax_count.setValidator(vali)
        # self.ui_syntax_count.setToolTip(
        #     'Default -1 to replace/substitute all occurrences.\n'
        #     'Use 0 for not doing anything.\n'
        #     'Value greater than 0 to replace/substitute corresponding '
        #     'number of occurrences.'
        # )
        syntax_layout.addWidget(syntax_label)
        syntax_layout.addWidget(self.ui_syntax_combo_box)
        # syntax_layout.addWidget(syntax_count_label)
        # syntax_layout.addWidget(self.ui_syntax_count)
        syntax_layout.setStretch(1, 1)

        string_replace_grp_box_layout.addWidget(pattern_label)
        string_replace_grp_box_layout.addLayout(pattern_hlayout)
        string_replace_grp_box_layout.addWidget(replacement_label)
        string_replace_grp_box_layout.addLayout(replacement_hlayout)
        string_replace_grp_box_layout.addLayout(syntax_layout)
        string_replace_grp_box.setLayout(string_replace_grp_box_layout)

        file_action_hlayout = QtWidgets.QHBoxLayout()
        file_action_label = QtWidgets.QLabel('File action :')

        self.ui_batch_process_action_combo = hou.qt.ComboBox()
        for file_action in const.FILE_ACTIONS:
            self.ui_batch_process_action_combo.addItem(file_action)
        file_action_hlayout.addWidget(file_action_label)
        file_action_hlayout.addWidget(self.ui_batch_process_action_combo)
        file_action_hlayout.setStretch(1, 1)

        buttons_hlayout = QtWidgets.QHBoxLayout()
        preview_it = QtWidgets.QPushButton('Dryrun')

        preview_it.setFixedHeight(40)
        preview_it.clicked.connect(self.on_action_dryrun)
        run_it = QtWidgets.QPushButton('Run')
        run_it.setFixedHeight(40)
        run_it.clicked.connect(self.on_action_run)
        buttons_hlayout.addWidget(preview_it)
        buttons_hlayout.addWidget(run_it)
        buttons_hlayout.setStretch(0, 3)
        buttons_hlayout.setStretch(1, 7)

        note_label = QtWidgets.QLabel(
            'NOTE: \n'
            ' 1. The repath string replace will be applied to the RAW value '
            'of the Parameter, not the expanded value.\n'
            ' 2. File action can apply to sequence files with <UDIM> or $F '
            '(or ${F}) in the filenames.\n'
            ' 3. The intermediate-level directories will be created when '
            'copying/moving the files to a non-existent directory.\n'
            ' 4. Dryrun button is to only display the changes will be made '
            'to the parameters, but not copy/move files or set parameter '
            'values.'
        )
        note_label.setWordWrap(True)

        batch_process_grp_box_layout.addLayout(selection_hlayout)
        batch_process_grp_box_layout.addWidget(string_replace_grp_box)
        batch_process_grp_box_layout.addLayout(file_action_hlayout)
        batch_process_grp_box_layout.addStretch()
        batch_process_grp_box_layout.addLayout(buttons_hlayout)
        batch_process_grp_box_layout.addWidget(note_label)
        self.ui_batch_process_grp_box.setLayout(
            batch_process_grp_box_layout
        )

        # Add the GroupBox to the layout
        tools_layout.addWidget(self.ui_batch_process_grp_box)

        # Set the layout and widget
        tools_widget.setLayout(tools_layout)

        # add to scroll area
        tools_scroll_area.setWidget(tools_widget)

        # create log widget
        log_scroll_area = QtWidgets.QScrollArea()

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
        centre_section_layout = QtWidgets.QHBoxLayout()
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(node_view_top_widget)
        splitter.addWidget(parm_view_top_widget)
        splitter.addWidget(tools_n_log_top_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)
        centre_section_layout.addWidget(splitter)

        return centre_section_layout

    def on_reset(self):
        self.ui_root_path_text.setText('')
        self.on_refresh()

    def on_refresh(self):
        """ The main callback for refreshing the UIs."""

        # Get the root node
        root_path = self.ui_root_path_text.text()
        if not root_path:
            self.set_up_node_tree_model([])
            self.set_up_parm_tree_model([])
            return

        root_node = hou.node(root_path)
        if not root_node:
            self.set_up_node_tree_model([])
            self.set_up_parm_tree_model([])
            return

        # Get the filters
        filter_matchers = []
        node_name_filter_txt = self.ui_node_name_filter_text.text()
        if not node_name_filter_txt:
            node_name_filter_txt = '*'
        filter_matchers.append(nodesearch.Name(node_name_filter_txt))

        node_type_filter_txt = self.ui_node_type_combo.lineEdit().text()
        filter_matchers.append(nodesearch.NodeType(node_type_filter_txt))

        parm_name_filter_txt = self.ui_parm_name_filter_text.text()
        if not parm_name_filter_txt:
            parm_name_filter_txt = '*'
        parm_file_type_filter_txt = self.ui_file_type_combo.currentText()
        filter_matchers.append(matchers.ParmNameAndFileType(
            parm_name_filter_txt, parm_file_type_filter_txt))

        final_matcher_grp = nodesearch.Group(filter_matchers, intersect=True)

        nodes = list(final_matcher_grp.nodes(root_node, ignore_case=True,
                                             recursive=True,
                                             recurse_in_locked_nodes=False))

        # Get node path list
        path_list = [n.path() for n in nodes]

        # Set up the two models.
        self.set_up_node_tree_model(path_list)
        self.set_up_parm_tree_model([])

    def on_root_node_selected(self, op_node):
        self.ui_root_path_text.setText(op_node.path())
        self.on_refresh()

    def on_node_tree_view_double_clicked(self, model_index: QtCore.QModelIndex):

        node = self._node_tree_model.get_hou_object(model_index)
        if not node:
            return

        node.setCurrent(True, clear_all_selected=True)

    def on_node_tree_view_selection_changed(self, selected, deselected):
        # get parm name pattern
        parm_name_pattern = self.ui_parm_name_filter_text.text()
        if not parm_name_pattern:
            parm_name_pattern = '*'

        # get parm file type
        parm_file_type = self.ui_file_type_combo.currentText().lower()

        # Get the selected nodes from node tree view
        # Use selectedRows(0) because we just need one id per row.
        id_list = self.ui_node_tree_view.selectionModel().selectedRows(0)

        # Find all the filtered parms
        parm_list = []
        for index in id_list:

            node = (self._node_tree_model.get_item(index)
                    .get_raw_data().get_orig_data())

            for parm in node.globParms(parm_name_pattern, ignore_case=True):

                # Re-use the function from matchers
                if matchers.parm_is_file_type(parm, parm_file_type,
                                              match_invisible=False):
                    parm_list.append(parm.path())

        self.set_up_parm_tree_model(parm_list)
        self.node_tree_view_config_post_model_setup()

    def update_parm_model(self, row_id, path):
        if not path:
            return

        index = self._parm_tree_model.index(row_id, 2)
        self._parm_tree_model.setData(index, path, QtCore.Qt.EditRole)

    def on_parm_tree_data_changed(self, top_left: QtCore.QModelIndex,
                                  bottom_right: QtCore.QModelIndex, roles):
        parm = (self._parm_tree_model.get_item(top_left)
                .get_raw_data().get_orig_data())

    def on_action_dryrun(self):
        results = self.run_it(dryrun=True)
        if not results:
            return

        dialog = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()

        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)
        table.setRowCount(len(results))
        table.setHorizontalHeaderLabels(['Original Raw Path', 'New Raw Path'])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        for index, pair in enumerate(results):
            table.setItem(index, 0, QtWidgets.QTableWidgetItem(pair[0]))
            table.setItem(index, 1, QtWidgets.QTableWidgetItem(pair[1]))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.setGeometry(400, 200, 800,500)
        dialog.setModal(True)
        dialog.exec_()

    def on_action_run(self):
        results = self.run_it(dryrun=False)

    def run_it(self, dryrun=True):

        # Just return if no tree model
        if not self._parm_tree_model:
            return

        # Each item of the list is a tuple of
        # (id_of_column_0, id_of_column_2)
        id_list = []
        if self.ui_selected_parms_option.isChecked():
            col_0_list = self.ui_parm_tree_view.selectionModel().selectedRows(0)
            col_2_list = self.ui_parm_tree_view.selectionModel().selectedRows(2)
            id_list = list(zip(col_0_list, col_2_list))
            if not id_list:
                return

        elif self.ui_all_parms_option.isChecked():
            root_index = self.ui_parm_tree_view.rootIndex()
            root_item = self._parm_tree_model.get_item(root_index)
            row_num = len(root_item.children())
            for row_id in range(row_num):
                id_list.append((self._parm_tree_model.index(row_id, 0),
                                self._parm_tree_model.index(row_id, 2)))

        # replace function
        syntax_combo_index = self.ui_syntax_combo_box.currentIndex()
        if syntax_combo_index >= len(const.STR_REPLACE_FUNCS):
            hou.ui.displayMessage('The str replace function is not supported!\n'
                                  'Supported are : {}'
                                  .format(const.STR_REPLACE_FUNCS))
            return
        replace_func = const.STR_REPLACE_FUNCS[syntax_combo_index][1]

        # pattern string
        pattern_string = self.ui_pattern_str.text()
        if not pattern_string:
            hou.ui.displayMessage('Pattern string is empty. Exiting.')
            return
        
        # replacement string
        replacement_string = self.ui_replacement_str.text()
        if not replacement_string:
            hou.ui.displayMessage('Replacement string is empty. Exiting.')
            return

        # Action
        file_action = self.ui_batch_process_action_combo.currentText()
        if file_action not in const.FILE_ACTIONS:
            hou.ui.displayMessage('The action is not supported!\n'
                                  'Supported actions are : {}'
                                  .format(const.FILE_ACTIONS))
            return



        # count
        # count = int(self.ui_syntax_count.text())

        # results with original and new raw path pairs
        results = []

        # Process
        for id_pair in id_list:

            # get parm from id
            parm = (self._parm_tree_model.get_item(id_pair[0])
                    .get_raw_data().get_orig_data())

            if not parm.rawValue():
                continue

            # replace string
            original_raw_path = parm.rawValue()
            new_raw_path = replace_func(pattern_string, replacement_string,
                                        original_raw_path)

            # process parameter files
            if file_action == const.FILE_ACTION_NONE:
                success = True
            else:
                success = utils.process_parm_files(parm, file_action,
                                                   new_raw_path,
                                                   dryrun=dryrun)

            if success:
                # add to results
                results.append((original_raw_path, new_raw_path))
                if not dryrun:
                    # Then set model data, the views will update automatically.
                    self._parm_tree_model.setData(id_pair[1], new_raw_path,
                                                  QtCore.Qt.EditRole)

        return results

    def on_preview_file(self, row_id):

        index = self._parm_tree_model.index(row_id, 2)
        parm = (self._parm_tree_model.get_item(index).get_raw_data()
                .get_orig_data())
        file_path = parm.eval()
        raw_value = parm.rawValue()
        if not file_path:
            return

        if not os.path.isfile(file_path):
            hou.ui.displayMessage('The file does not exist:\n'
                                  '  {}\n'
                                  '(Raw value: {})'
                                  .format(file_path, raw_value))
            return

        subprocess.Popen(['mplay', '-minimal', file_path])

    def on_node_type_category_changed(self):
        self.ui_node_type_combo.clear()
        self.ui_node_type_combo.addItem('*')

        cur_cate = self.ui_node_type_category_combo.itemData(
            self.ui_node_type_category_combo.currentIndex())

        if not cur_cate:
            return

        items = nodesearch.node_types(cur_cate)
        self.ui_node_type_combo.addItems(items)

    def on_pattern_path_browse(self, dir_path):
        self.ui_pattern_str.setText(dir_path)

    def on_replacement_path_browse(self, dir_path):
        self.ui_replacement_str.setText(dir_path)

