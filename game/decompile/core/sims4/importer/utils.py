# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\importer\utils.py
# Compiled at: 2020-05-07 17:39:36
# Size of source mod 2**32: 4377 bytes
import os, re, sys, zipfile, paths, sims4.log
logger = sims4.log.Logger('Importer')

def _partial_path_to_module_fqn(partial_path):
    if partial_path.endswith('__init__'):
        partial_path = partial_path[:-len('__init__')]
    fqn = partial_path.translate(str.maketrans('\\/', '..'))
    fqn = fqn.strip('.')
    return fqn


def import_modules():
    error_count = 0
    for script_root in paths.USER_SCRIPT_ROOTS:
        error_count += import_modules_by_path(script_root)

    return error_count


def module_names_gen(_path):
    py_re = re.compile('.+\\.py$')
    ext = '.zip'
    ext_index = _path.find(ext)
    if ext_index == -1:
        ext = '.ts4script'
        ext_index = _path.find(ext)
    elif ext_index != -1:
        compiled = True
        py_re = re.compile('.+\\.py[co]$')
        archive_name = _path[0:ext_index + len(ext)]
        local_path = _path[ext_index + len(ext) + 1:]
        archive = zipfile.ZipFile(archive_name)
        if local_path:
            files = [f for f in archive.namelist() if f.startswith(local_path + '/') if py_re.match(f)]
        else:
            files = [f for f in archive.namelist() if py_re.match(f)]
        for filename in files:
            if compiled:
                filename = filename[:-4]
            else:
                filename = filename[:-3]
            module_fqn = _partial_path_to_module_fqn(filename)
            yield (filename, module_fqn)

    else:
        compiled = False
        py_re = re.compile('.+\\.py$')
        prefix_list = sorted([os.path.commonprefix([os.path.abspath(m), _path]) for m in sys.path if _path.startswith(os.path.abspath(m))],
          key=len,
          reverse=True)
        if not prefix_list:
            logger.error('Path {0} must be under sys.path: {1}', _path, sys.path)
            return
        prefix = prefix_list[0]
        local_path = os.path.relpath(_path, prefix)
        files = []
        for dirpath, _, filenames in os.walk(_path):
            relative = os.path.join(local_path, os.path.relpath(dirpath, _path))
            relative = os.path.normpath(relative)
            for filename in filenames:
                if py_re.match(filename):
                    files.append((dirpath, relative, filename))

        for dirpath, relative, filename in files:
            if compiled:
                filename = filename[:-4]
            else:
                filename = filename[:-3]
            module_filename = os.path.join(dirpath, filename)
            module_name = os.path.join(relative, filename)
            module_fqn = _partial_path_to_module_fqn(module_name)
            yield (
             module_filename, module_fqn)


def import_modules_by_path(_path, use_print=False):
    import builtins
    ignored_modules = set()
    error_count = 0
    for module_name, module_fqn in module_names_gen(_path):
        try:
            builtins.__import__(module_fqn)
            ignored_modules.add(module_fqn)
        except Exception as exc:
            try:
                log_fn = print if use_print else logger.exception
                log_fn("  Failure: '{0}' ({1}) \n     {2}".format(module_name, module_fqn, exc))
                error_count += 1
            finally:
                exc = None
                del exc

    return error_count