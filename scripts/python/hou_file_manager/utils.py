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

import shutil
import glob
from . import constants as const


def process_parm_files(parm, file_action, dest_dir):
    source_files = []

    raw_value = parm.rawValue()

    # Houdini doesn't support time-dependent UDIM texture files.
    # We will check if the file path contains <UDIM> first.
    if '<UDIM>' in raw_value:
        eval_value = parm.eval()
        print(eval_value)
        pattern = eval_value.replace('<UDIM>', '[1-9][0-9][0-9][0-9]')
        source_files = glob.glob(pattern)

    elif parm.isTimeDependent():
        pass

    else:
        # Then it is a single file. Eval it which will expand the path.
        source_files.append(parm.eval())

    print(source_files)

    # if nothing to process then return
    if not source_files:
        return False

    for s_file in source_files:
        if file_action == const.FILE_ACTION_COPY:
            print('Copying source file:\n'
                  '    {}\n'
                  '  to destination dir:\n'
                  '    {}'
                  .format(s_file, dest_dir))
            shutil.copy(s_file, dest_dir)
        elif file_action == const.FILE_ACTION_MOVE:
            print('Moving source file:\n'
                  '    {}\n'
                  '  to destination dir:\n'
                  '    {}'
                  .format(s_file, dest_dir))
            shutil.move(s_file, dest_dir)
        else:
            print('The file action is not supported: \n{}'
                  .format(file_action))

    return True


