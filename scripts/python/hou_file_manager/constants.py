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

import hou
import re

PATH_DELIMITER = '/'

# Headers
DEFAULT_TREE_HEADERS = ['Name', 'Value']
NODE_TREE_HEADERS = ['Node View']
FILE_PARM_LIST_HEADERS = ['Parameter View', 'Tools',
                          'Raw Value (Double click to edit)']

PARM_TREE_VIEW_EDITABLE_COLUMN = 2

# Getter attr
PARM_GET_ATTRS = ['name', '', 'rawValue']
NODE_GET_ATTRS = ['name']

# Setter attr
PARM_SET_ATTRS = ['', '', 'set']
NODE_SET_ATTRS = ['']

# File actions
FILE_ACTION_NONE = 'None -> ONLY update parameter, NOT making changes to files'
FILE_ACTION_COPY = 'Copy -> Update parameter AND copy files to new paths'
FILE_ACTION_MOVE = 'Move -> Update parameter AND move files to new paths'
FILE_ACTIONS = [FILE_ACTION_NONE, FILE_ACTION_COPY, FILE_ACTION_MOVE]

# String replace functions
PYTHON_STR_REPLACE = 'Python: str.replace()'
STR_REPLACE = (PYTHON_STR_REPLACE,
               lambda pattern, repl, string:
               string.replace(pattern, repl)
               )
PYTHON_RE_SUBSTITUTE = 'Python: re.sub()'
REGEX_SUBSTITUTE = (PYTHON_RE_SUBSTITUTE,
                    lambda pattern, repl, string:
                    re.sub(pattern, repl, string)
                    )
STR_REPLACE_FUNCS = [STR_REPLACE, REGEX_SUBSTITUTE]

# Colors
BG_RED = (100, 0, 0)
BG_GREEN = (0, 100, 0)

# icons
ICON_SIZE = hou.ui.scaledSize(16)
ADD_ICON = hou.qt.createIcon("BUTTONS_list_add", ICON_SIZE, ICON_SIZE)

SESSION_VAR = 'GLOBAL_BROWSER_UI_HOU_FILE_MANAGER'


