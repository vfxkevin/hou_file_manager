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
from nodesearch.matchers import Matcher


class FileParm(Matcher):
    """
    Matches by the file_type if the parmTemplate string_type of any parm
    is hou.stringParmType.FileReference.
    """

    def __init__(self, parm_name, file_type, match_invisible=False):

        self.parm_name = parm_name
        self.file_type = file_type.lower()
        self.match_invisible = match_invisible

    def __repr__(self):
        return "<{} {} {}>".format(type(self).__name__,
                                   self.parm_name,
                                   self.file_type)

    def matches(self, node, ignore_case=False):
        if self.parm_name is None or self.parm_name == '':
            return False

        for parm in node.globParms(self.parm_name, ignore_case=ignore_case,
                                   search_label=True, single_pattern=True):

            # No need to match when the parm is invisible and we don't want to
            # match invisible parms.
            if not self.match_invisible and not parm.isVisible():
                continue

            # Get parmTemplate of the parm.
            pt = parm.parmTemplate()

            if not isinstance(pt, hou.StringParmTemplate):
                continue

            if not pt.stringType() == hou.stringParmType.FileReference:
                continue

            # It will return True once any parm meets the condition.
            # No need to continue checking all the rest of the parms.
            if pt.fileType().name().lower() == self.file_type:
                return True

        return False

