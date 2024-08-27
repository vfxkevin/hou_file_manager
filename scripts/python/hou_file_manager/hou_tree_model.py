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

from PySide2.QtCore import QAbstractItemModel
from PySide2.QtCore import QModelIndex

from PySide2.QtCore import Qt

import hou

from . import constants as const
from .treemodel import (BaseTreeModel, TreeItem, TreeItemDataGenericList, BaseTreeItemData)


class TreeItemDataObject(BaseTreeItemData):
    def __init__(self, orig_data, property_get_attrs, property_set_attrs,
                 bg_color=None):
        super().__init__(orig_data)

        self._property_get_attrs = property_get_attrs
        self._property_set_attrs = property_set_attrs
        self._bg_color = bg_color

        if isinstance(orig_data, hou.OpNode):
            orig_data.addEventCallback((hou.nodeEventType.BeingDeleted, ),
                                       self.data_deleted)

    def len(self):
        return len(self._property_get_attrs)

    def get(self, column: int = 0):
        if column < 0 or column >= len(self._property_get_attrs):
            return None

        attr = self._property_get_attrs[column]
        if not hasattr(self._orig_data, attr):
            return None

        return getattr(self._orig_data, attr)()

    def set_data(self, column: int, value):
        if column < 0 or column >= len(self._property_set_attrs):
            return False

        attr = self._property_set_attrs[column]
        if not hasattr(self._orig_data, attr):
            return False

        getattr(self._orig_data, attr)(value)
        return True

    def get_bg_color(self):
        return self._bg_color

    def get_icon(self):
        if not isinstance(self._orig_data, hou.OpNode):
            return None

        icon_name = self._orig_data.type().icon()
        return hou.qt.createIcon(icon_name)

    def data_deleted(self, node, event_type, **kwargs):
        if self.tree_item:
            parent = self.tree_item.parent()
            parent.remove_child(self.tree_item)


class HouNodeTreeModel(BaseTreeModel):
    def __init__(self, path_list: list, parent=None):

        self._property_get_attrs = const.NODE_GET_ATTRS
        self._property_set_attrs = const.NODE_SET_ATTRS

        # Headers
        headers = const.NODE_TREE_HEADERS

        # root item
        hou_root_node = hou.node(const.PATH_DELIMITER)
        root_item = TreeItem(
            TreeItemDataObject(hou_root_node,
                               self._property_get_attrs,
                               self._property_set_attrs)
        )

        super().__init__(path_list, headers, root_item, parent)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        flags = QAbstractItemModel.flags(self, index)

        # Get tree item
        item = self.get_item(index)

        bg_color = item.get_raw_data().get_bg_color()
        if not bg_color:
            flags &= ~Qt.ItemIsSelectable

        return flags

    def set_up_model_data(self, data: list):
        """ Data is a string list of paths of Hou Nodes."""

        # Must sort the path list
        data.sort()

        for path in data:
            self.add_path_to_tree(path, self._root_item,'',
                                  self._property_get_attrs,
                                  self._property_set_attrs)

    def get_hou_object(self, index: QModelIndex):
        if not index.isValid():
            return None

            # Get tree item
        item = self.get_item(index)

        return item.tree_item_data().get_orig_data()

    def add_path_to_tree(self, path, target_tree_item, current_path,
                         property_get_attrs, property_set_attrs):
        parts = path.strip(const.PATH_DELIMITER).split(const.PATH_DELIMITER)

        current = parts[0]
        the_rest = parts[1:]

        child = target_tree_item.get_child_by_column_data(current)
        current_path = '{}{}{}'.format(current_path,
                                       const.PATH_DELIMITER,
                                       current)

        if not child:
            # get the hou node
            hou_node = hou.node(current_path)
            # create a tree item
            if not the_rest:
                bg_color = const.BG_RED
            else:
                bg_color = None
            child = TreeItem(
                TreeItemDataObject(hou_node,
                                   property_get_attrs,
                                   property_set_attrs,
                                   bg_color)
            )
            target_tree_item.append_child(child)

        if the_rest:
            # continue adding the rest
            self.add_path_to_tree(const.PATH_DELIMITER.join(the_rest),
                                  child,
                                  current_path,
                                  property_get_attrs,
                                  property_set_attrs)


class HouParmTreeModel(BaseTreeModel):
    def __init__(self, node_list: list, parent=None):

        self._property_get_attrs = const.PARM_GET_ATTRS
        self._property_set_attrs = const.PARM_SET_ATTRS

        headers = const.FILE_PARM_LIST_HEADERS

        root_item = TreeItem(TreeItemDataGenericList(['', '', '']))

        super().__init__(node_list, headers, root_item, parent)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlag

        flags = QAbstractItemModel.flags(self, index)
        col = index.column()
        if col == const.PARM_TREE_VIEW_EDITABLE_COLUMN:
            flags |= Qt.ItemIsEditable
        return flags

    def set_up_model_data(self, data: list):
        """Data is a string list of parm paths."""

        for parm_path in data:
            parm = hou.parm(parm_path)
            # add the node as a child to the root
            child = TreeItem(
                TreeItemDataObject(parm,
                                   self._property_get_attrs,
                                   self._property_set_attrs)
            )
            self._root_item.append_child(child)

            # then add file parameters as children to the node

    def get_hou_object(self,  index: QModelIndex):
        if not index.isValid():
            return None

            # Get tree item
        item = self.get_item(index)

        return item.tree_item_data().get_orig_data()



