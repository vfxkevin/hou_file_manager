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

FILE_TYPE_DICT = {'image': hou.fileType.Image,
                  'geometry': hou.fileType.Geometry}


def parm_is_file_type(parm, file_type, match_invisible=False):
        # No need to match when the parm is invisible and we don't want to
        # match invisible parms.
        if not match_invisible and not parm.isVisible():
            return False

        # Get parmTemplate of the parm.
        pt = parm.parmTemplate()

        if not isinstance(pt, hou.StringParmTemplate):
            return False

        if not pt.stringType() == hou.stringParmType.FileReference:
            return False

        # It will return True once any parm meets the condition.
        # No need to continue checking all the rest of the parms.
        if pt.fileType().name().lower() == file_type:
            return True


class ParmNameAndFileType(Matcher):
    """
    Matches nodes if any of the node's parameters match the name pattern
    and file_type.
    """

    def __init__(self, name_pattern, file_type, match_invisible=False):

        self.name_pattern = name_pattern
        # file_type is string and converted to lower case.
        self.file_type = file_type.lower()
        self.match_invisible = match_invisible

    def __repr__(self):

        return ("<{} {} match_invisible={}>"
                .format(type(self).__name__, self.file_type,
                        self.match_invisible))

    def matches(self, node, ignore_case=False):

        if self.file_type not in FILE_TYPE_DICT.keys():
            raise Exception('The file type is not supported: {}'
                            .format(self.file_type))

        for parm in node.globParms(self.name_pattern, ignore_case=ignore_case,
                                   search_label=True, single_pattern=False):
            if parm_is_file_type(parm, self.file_type, self.match_invisible):
                return True

        return False

