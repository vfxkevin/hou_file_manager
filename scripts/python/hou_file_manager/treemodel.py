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
from PySide2.QtGui import QBrush, QColor

from . import constants as const


class BaseTreeItemData:
    def __init__(self, orig_data, icon=None, bg_color=None):
        self._orig_data = orig_data
        self._icon = icon
        self._bg_color = bg_color

    def len(self):
        raise NotImplementedError

    def get(self, column: int = 0):
        raise NotImplementedError

    def set_data(self, column: int, value):
        raise NotImplementedError

    def get_orig_data(self):
        return self._orig_data

    def get_icon(self):
        return self._icon

    def set_icon(self, icon):
        self._icon = icon

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, bg_color):
        self._bg_color = bg_color


class TreeItemDataGenericList(BaseTreeItemData):
    def __init__(self, orig_data: list):
        super().__init__(orig_data)

    def len(self):
        return len(self._orig_data)

    def get(self, column: int = 0):
        return self._orig_data[column]

    def set_data(self, column: int, value):
        if column < 0 or column >= len(self._orig_data):
            return False

        self._orig_data[column] = value
        return True

    def get_icon(self):
        return None


class TreeItem:
    def __init__(self, data: BaseTreeItemData, parent: 'TreeItem' = None):
        self._data = data
        self._parent = parent
        self._children = []

    def append_child(self, item: 'TreeItem'):
        self._children.append(item)
        item.set_parent(self)

    def get_child(self, index: int):
        if index < 0 or index >= len(self._children):
            return None
        return self._children[index]

    def get_child_by_column_data(self, data: str, column: int = 0):
        if not data:
            return None

        for child in self._children:
            child_data = child.data(column)

            if not child_data:
                continue

            if data == child_data:
                return child

    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def set_parent(self, parent: 'TreeItem'):
        self._parent = parent

    def get_row_id(self):
        if self._parent:
            return self._parent.children().index(self)

        return 0

    def data(self, column: int = 0):
        if column < 0 or column >= self._data.len():
            return None

        return self._data.get(column)

    def set_data(self, column: int, value):
        if column < 0 or column >= self._data.len():
            return False

        return self._data.set_data(column, value)

    def tree_item_data(self):
        return self._data

    def column_count(self):
        return self._data.len()

    def get_raw_data(self):
        """ To return the instance of a subclass of BaseTreeItemData."""
        return self._data


class BaseTreeModel(QAbstractItemModel):
    def __init__(self, input_data: list, headers: list, root_item: TreeItem,
                 parent=None):
        super().__init__(parent)

        # Initialize headers and root_item
        self._headers = headers
        self._root_item = root_item

        # finally set up data for the model
        self.set_up_model_data(input_data)

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]

        return None

    def index(self, row: int, column: int,
              parent: QModelIndex = QModelIndex()) -> QModelIndex:

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        result_id = QModelIndex()

        parent_item = self.get_item(parent)
        if not parent_item:
            return result_id

        child = parent_item.get_child(row)
        if child:
            result_id = self.createIndex(row, column, child)

        return result_id

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:

        if not index.isValid():
            return QModelIndex()

        input_item = self.get_item(index)
        if input_item:
            parent_item = input_item.parent()
        else:
            parent_item = None

        if not parent_item or parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.get_row_id(), 0, parent_item)

    def rowCount(self, parent: QModelIndex) -> int:

        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item = self.get_item(parent)
        if not parent_item:
            return 0

        children = parent_item.children()
        return len(children)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self._root_item.column_count()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.DisplayRole):
        if not index.isValid():
            return None

        # Get tree item
        item = self.get_item(index)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.data(index.column())

        elif role == Qt.DecorationRole:
            return item.get_raw_data().get_icon()

        elif role == Qt.BackgroundRole:
            # get the original data which is the Hou Node.
            bg_color = item.get_raw_data().get_bg_color()
            if bg_color:
                brush = QBrush(QColor(*bg_color))
                return brush

        return None

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.EditRole:
            return False

        item = self.get_item(index)
        print(item)
        print('---')
        print(index.column())
        result = item.set_data(index.column(), value)
        print(result)

        if result:
            print('emit')
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        return result

    def set_up_model_data(self, data: list):
        raise NotImplementedError


