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
import sys
import shutil
import glob
import re
import importlib
import hou
from . import constants as const

class MissingUDIMToken(Exception):
    pass

class FPaddingReSplitError(Exception):
    pass

class SpecialSymbolFound(Exception):
    pass

def files_exist(parm):
    """Checks if the files specified in the parm exist. For sequence
    files, it will return True if any files specified exist."""
    raw_path = parm.rawValue()

    # Backtick or () are not supported.
    if ('`' in raw_path or '(' in raw_path or ')' in raw_path):
        raise SpecialSymbolFound(f'Sepcial symbols, such as `, (, or ), '
                                 f'found in: {raw_path}')

    expanded_dirname = os.path.dirname(parm.eval())

    # Return false when the dirname doesn't exist.
    if not os.path.exists(expanded_dirname):
        return False

    raw_basename = os.path.basename(raw_path)

    pattern = None
    if const.UDIM_TOKEN in raw_basename:
        pattern = re.escape(raw_basename)
        if const.UDIM_TOKEN not in pattern:
            raise MissingUDIMToken(f'<UDIM> token gone missing in: {pattern}')
        pattern = pattern.replace(const.UDIM_TOKEN, const.REGEX_FOUR_DIGITS)
    elif parm.isTimeDependent():
        parts = re.split(const.REGEX_F_PADDING, raw_basename)
        if len(parts) != 4:
            raise FPaddingReSplitError(f'Can not use F padding to split the '
                                       f'basename: {raw_basename}')
        digits = parts[1] or parts[2]
        pattern = re.escape(parts[0]) + r'(\d{' + digits + r'})' + re.escape(parts[3])
    else:
        pattern = re.escape(raw_basename)

    compiled = re.compile(pattern)
    for filename in os.listdir(expanded_dirname):
        match = compiled.fullmatch(filename)
        if match:
            return True

    return False


def process_parm_files(parm, file_action, new_raw_path, dryrun=True):
    src_dest_file_pairs = []

    original_raw_path = parm.rawValue()
    original_expanded_path = parm.eval()
    original_raw_basename = os.path.basename(original_raw_path)
    original_expanded_dirname = os.path.dirname(original_expanded_path)
    new_expanded_path = hou.text.expandString(new_raw_path)
    new_raw_basename = os.path.basename(new_raw_path)
    new_expanded_dirname = os.path.dirname(new_expanded_path)

    dryrun_str = "[DRYRUN] " if dryrun else ""

    if not original_raw_path:
        return False

    is_sequence_style = False
    pattern_re = None

    # Houdini doesn't support time-dependent UDIM texture files.
    # We will check if the file path contains <UDIM> first.
    if const.UDIM_TOKEN in original_raw_path:
        pattern_re = re.compile(const.UDIM_TOKEN)
        is_sequence_style = True
    elif parm.isTimeDependent():
        # Backtick or () are not supported.
        if ('`' in original_raw_basename or '(' in original_raw_basename
                or ')' in original_raw_basename):
            print('Ignored, because backticks and () are not supported at '
                  'the moment.')
            return False

        # Checking for $F4 or ${F4} like substrings.
        pattern_re = re.compile(const.REGEX_F_PADDING)
        result = pattern_re.search(original_raw_basename)
        if not result:
            print('Ignored, because even it is time dependent but not $F '
                  'or ${F} like string can not be found.')
            return False
        is_sequence_style = True

    # Based on if it is sequence style
    if is_sequence_style:
        # Get the full basename regex pattern
        orig_raw_basename_parts = pattern_re.split(original_raw_basename)
        orig_expanded_full_basename_pattern_re = re.compile(
            '^' + re.escape(orig_raw_basename_parts[0]) +
            '([0-9]+)' + re.escape(orig_raw_basename_parts[1]) + '$'
        )

        # Split the new basename using the pattern
        new_raw_basename_parts = pattern_re.split(new_raw_basename)

        for f in os.listdir(original_expanded_dirname):
            match = orig_expanded_full_basename_pattern_re.match(f)
            if not match:
                continue

            # get the frame number from f
            seq_number = match.groups()[0]

            # construct new filename
            new_f = (new_raw_basename_parts[0] + seq_number +
                     new_raw_basename_parts[1])

            src = os.path.join(original_expanded_dirname, f)
            dest = os.path.join(new_expanded_dirname, new_f)

            src_dest_file_pairs.append((src, dest))
    else:
        # Then it is a single file. Eval it which will expand the path.
        src_dest_file_pairs.append((original_expanded_path, new_expanded_path))

    # if nothing to process then return
    if not src_dest_file_pairs:
        print('No files to apply the file actions. Exiting.')
        return False

    # for s_file in source_files:
    for src_file, dest_file in src_dest_file_pairs:
        if not os.path.isfile(src_file):
            print('The source file does not exist: \n  {}'.format(src_file))
            continue

        # Check if target file already exists.
        if os.path.isfile(dest_file):
            print('The file with same name as source file already '
                  'exists in destination directory:\n'
                  '  {}\n'
                  'Exiting.'
                  .format(dest_file))
            continue

        # Then take file action.
        if file_action == const.FILE_ACTION_COPY:
            print(f'{dryrun_str}Copying source file:\n'
                  f'{dryrun_str}    {src_file}\n'
                  f'{dryrun_str}  to destination file:\n'
                  f'{dryrun_str}    {dest_file}')
            if not dryrun:
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy(src_file, dest_file)
        elif file_action == const.FILE_ACTION_MOVE:
            print(f'{dryrun_str}Moving source file:\n'
                  f'{dryrun_str}    {src_file}\n'
                  f'{dryrun_str}  to destination file:\n'
                  f'{dryrun_str}    {dest_file}')
            if not dryrun:
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.move(src_file, dest_file)
        else:
            print('The file action is not supported: \n'
                  '  {}\n'
                  'Exiting.'
                  .format(file_action))

    print('All files have been processed. Done.')
    return True


def deep_reload_package(package_name):
    modules_to_reload = [
        name for name in sys.modules
        if name == package_name or name.startswith(package_name + ".")
    ]
    modules_to_reload.sort(key=len, reverse=True)

    for module_name in modules_to_reload:
        try:
            importlib.reload(sys.modules[module_name])
        except Exception as e:
            print(f"Skipped reloading {module_name}: {e}")

    print(f"Successfully deep-reloaded all submodules for: {package_name}")

