# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\sysconfig.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 24893 bytes
import os, sys
from os.path import pardir, realpath
__all__ = [
 "'get_config_h_filename'", 
 "'get_config_var'", 
 "'get_config_vars'", 
 "'get_makefile_filename'", 
 "'get_path'", 
 "'get_path_names'", 
 "'get_paths'", 
 "'get_platform'", 
 "'get_python_version'", 
 "'get_scheme_names'", 
 "'parse_config_h'"]
_INSTALL_SCHEMES = {'posix_prefix':{
  'stdlib': "'{installed_base}/lib/python{py_version_short}'", 
  'platstdlib': "'{platbase}/lib/python{py_version_short}'", 
  'purelib': "'{base}/lib/python{py_version_short}/site-packages'", 
  'platlib': "'{platbase}/lib/python{py_version_short}/site-packages'", 
  'include': "'{installed_base}/include/python{py_version_short}{abiflags}'", 
  'platinclude': "'{installed_platbase}/include/python{py_version_short}{abiflags}'", 
  'scripts': "'{base}/bin'", 
  'data': "'{base}'"}, 
 'posix_home':{
  'stdlib': "'{installed_base}/lib/python'", 
  'platstdlib': "'{base}/lib/python'", 
  'purelib': "'{base}/lib/python'", 
  'platlib': "'{base}/lib/python'", 
  'include': "'{installed_base}/include/python'", 
  'platinclude': "'{installed_base}/include/python'", 
  'scripts': "'{base}/bin'", 
  'data': "'{base}'"}, 
 'nt':{
  'stdlib': "'{installed_base}/Lib'", 
  'platstdlib': "'{base}/Lib'", 
  'purelib': "'{base}/Lib/site-packages'", 
  'platlib': "'{base}/Lib/site-packages'", 
  'include': "'{installed_base}/Include'", 
  'platinclude': "'{installed_base}/Include'", 
  'scripts': "'{base}/Scripts'", 
  'data': "'{base}'"}, 
 'nt_user':{
  'stdlib': "'{userbase}/Python{py_version_nodot}'", 
  'platstdlib': "'{userbase}/Python{py_version_nodot}'", 
  'purelib': "'{userbase}/Python{py_version_nodot}/site-packages'", 
  'platlib': "'{userbase}/Python{py_version_nodot}/site-packages'", 
  'include': "'{userbase}/Python{py_version_nodot}/Include'", 
  'scripts': "'{userbase}/Python{py_version_nodot}/Scripts'", 
  'data': "'{userbase}'"}, 
 'posix_user':{
  'stdlib': "'{userbase}/lib/python{py_version_short}'", 
  'platstdlib': "'{userbase}/lib/python{py_version_short}'", 
  'purelib': "'{userbase}/lib/python{py_version_short}/site-packages'", 
  'platlib': "'{userbase}/lib/python{py_version_short}/site-packages'", 
  'include': "'{userbase}/include/python{py_version_short}'", 
  'scripts': "'{userbase}/bin'", 
  'data': "'{userbase}'"}, 
 'osx_framework_user':{
  'stdlib': "'{userbase}/lib/python'", 
  'platstdlib': "'{userbase}/lib/python'", 
  'purelib': "'{userbase}/lib/python/site-packages'", 
  'platlib': "'{userbase}/lib/python/site-packages'", 
  'include': "'{userbase}/include'", 
  'scripts': "'{userbase}/bin'", 
  'data': "'{userbase}'"}}
_SCHEME_KEYS = ('stdlib', 'platstdlib', 'purelib', 'platlib', 'include', 'scripts',
                'data')
_PY_VERSION = sys.version.split()[0]
_PY_VERSION_SHORT = '%d.%d' % sys.version_info[:2]
_PY_VERSION_SHORT_NO_DOT = '%d%d' % sys.version_info[:2]
_PREFIX = os.path.normpath(sys.prefix)
_BASE_PREFIX = os.path.normpath(sys.base_prefix)
_EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
_BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)
_CONFIG_VARS = None
_USER_BASE = None

def _safe_realpath(path):
    try:
        return realpath(path)
    except OSError:
        return path


if sys.executable:
    _PROJECT_BASE = os.path.dirname(_safe_realpath(sys.executable))
else:
    _PROJECT_BASE = _safe_realpath(os.getcwd())
if os.name == 'nt':
    if _PROJECT_BASE.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64')):
        _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir, pardir))
if '_PYTHON_PROJECT_BASE' in os.environ:
    _PROJECT_BASE = _safe_realpath(os.environ['_PYTHON_PROJECT_BASE'])

def _is_python_source_dir(d):
    for fn in ('Setup.dist', 'Setup.local'):
        if os.path.isfile(os.path.join(d, 'Modules', fn)):
            return True

    return False


_sys_home = getattr(sys, '_home', None)
if _sys_home:
    if os.name == 'nt':
        if _sys_home.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64')):
            _sys_home = os.path.dirname(os.path.dirname(_sys_home))

def is_python_build(check_home=False):
    if check_home:
        if _sys_home:
            return _is_python_source_dir(_sys_home)
    return _is_python_source_dir(_PROJECT_BASE)


_PYTHON_BUILD = is_python_build(True)
if _PYTHON_BUILD:
    for scheme in ('posix_prefix', 'posix_home'):
        _INSTALL_SCHEMES[scheme]['include'] = '{srcdir}/Include'
        _INSTALL_SCHEMES[scheme]['platinclude'] = '{projectbase}/.'

def _subst_vars(s, local_vars):
    try:
        return (s.format)(**local_vars)
    except KeyError:
        try:
            return (s.format)(**os.environ)
        except KeyError as var:
            try:
                raise AttributeError('{%s}' % var) from None
            finally:
                var = None
                del var


def _extend_dict(target_dict, other_dict):
    target_keys = target_dict.keys()
    for key, value in other_dict.items():
        if key in target_keys:
            continue
        target_dict[key] = value


def _expand_vars(scheme, vars):
    res = {}
    if vars is None:
        vars = {}
    _extend_dict(vars, get_config_vars())
    for key, value in _INSTALL_SCHEMES[scheme].items():
        if os.name in ('posix', 'nt'):
            value = os.path.expanduser(value)
        res[key] = os.path.normpath(_subst_vars(value, vars))

    return res


def _get_default_scheme():
    if os.name == 'posix':
        return 'posix_prefix'
    return os.name


def _getuserbase():
    env_base = os.environ.get('PYTHONUSERBASE', None)
    if env_base:
        return env_base

    def joinuser(*args):
        return os.path.expanduser((os.path.join)(*args))

    if os.name == 'nt':
        base = os.environ.get('APPDATA') or '~'
        return joinuser(base, 'Python')
    if sys.platform == 'darwin':
        if sys._framework:
            return joinuser('~', 'Library', sys._framework, '%d.%d' % sys.version_info[:2])
    return joinuser('~', '.local')


def _parse_makefile(filename, vars=None):
    import re
    _variable_rx = re.compile('([a-zA-Z][a-zA-Z0-9_]+)\\s*=\\s*(.*)')
    _findvar1_rx = re.compile('\\$\\(([A-Za-z][A-Za-z0-9_]*)\\)')
    _findvar2_rx = re.compile('\\${([A-Za-z][A-Za-z0-9_]*)}')
    if vars is None:
        vars = {}
    done = {}
    notdone = {}
    with open(filename, errors='surrogateescape') as (f):
        lines = f.readlines()
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            continue
        m = _variable_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            v = v.strip()
            tmpv = v.replace('$$', '')
            if '$' in tmpv:
                notdone[n] = v
            else:
                try:
                    v = int(v)
                except ValueError:
                    done[n] = v.replace('$$', '$')
                else:
                    done[n] = v

    variables = list(notdone.keys())
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')
    while len(variables) > 0:
        for name in tuple(variables):
            value = notdone[name]
            m1 = _findvar1_rx.search(value)
            m2 = _findvar2_rx.search(value)
            if m1:
                if m2:
                    m = m1 if m1.start() < m2.start() else m2
                else:
                    m = m1 if m1 else m2
                if m is not None:
                    n = m.group(1)
                    found = True
                    if n in done:
                        item = str(done[n])
                    else:
                        if n in notdone:
                            found = False
                        else:
                            if n in os.environ:
                                item = os.environ[n]
                            else:
                                if n in renamed_variables:
                                    if name.startswith('PY_') and name[3:] in renamed_variables:
                                        item = ''
                                    else:
                                        if 'PY_' + n in notdone:
                                            found = False
                                        else:
                                            item = str(done['PY_' + n])
                                else:
                                    done[n] = item = ''
                    if found:
                        after = value[m.end():]
                        value = value[:m.start()] + item + after
                        if '$' in after:
                            notdone[name] = value
            else:
                try:
                    value = int(value)
                except ValueError:
                    done[name] = value.strip()
                else:
                    done[name] = value
                variables.remove(name)
            if name.startswith('PY_'):
                if name[3:] in renamed_variables:
                    name = name[3:]
                    if name not in done:
                        done[name] = value
                    else:
                        done[name] = value
                        variables.remove(name)

    for k, v in done.items():
        if isinstance(v, str):
            done[k] = v.strip()

    vars.update(done)
    return vars


def get_makefile_filename():
    if _PYTHON_BUILD:
        return os.path.join(_sys_home or _PROJECT_BASE, 'Makefile')
    elif hasattr(sys, 'abiflags'):
        config_dir_name = 'config-%s%s' % (_PY_VERSION_SHORT, sys.abiflags)
    else:
        config_dir_name = 'config'
    if hasattr(sys.implementation, '_multiarch'):
        config_dir_name += '-%s' % sys.implementation._multiarch
    return os.path.join(get_path('stdlib'), config_dir_name, 'Makefile')


def _get_sysconfigdata_name():
    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', '_sysconfigdata_{abi}_{platform}_{multiarch}'.format(abi=(sys.abiflags),
      platform=(sys.platform),
      multiarch=(getattr(sys.implementation, '_multiarch', ''))))


def _generate_posix_vars():
    import pprint
    vars = {}
    makefile = get_makefile_filename()
    try:
        _parse_makefile(makefile, vars)
    except OSError as e:
        try:
            msg = 'invalid Python installation: unable to open %s' % makefile
            if hasattr(e, 'strerror'):
                msg = msg + ' (%s)' % e.strerror
            raise OSError(msg)
        finally:
            e = None
            del e

    config_h = get_config_h_filename()
    try:
        with open(config_h) as (f):
            parse_config_h(f, vars)
    except OSError as e:
        try:
            msg = 'invalid Python installation: unable to open %s' % config_h
            if hasattr(e, 'strerror'):
                msg = msg + ' (%s)' % e.strerror
            raise OSError(msg)
        finally:
            e = None
            del e

    if _PYTHON_BUILD:
        vars['BLDSHARED'] = vars['LDSHARED']
    name = _get_sysconfigdata_name()
    if 'darwin' in sys.platform:
        import types
        module = types.ModuleType(name)
        module.build_time_vars = vars
        sys.modules[name] = module
    pybuilddir = 'build/lib.%s-%s' % (get_platform(), _PY_VERSION_SHORT)
    if hasattr(sys, 'gettotalrefcount'):
        pybuilddir += '-pydebug'
    os.makedirs(pybuilddir, exist_ok=True)
    destfile = os.path.join(pybuilddir, name + '.py')
    with open(destfile, 'w', encoding='utf8') as (f):
        f.write('# system configuration generated and used by the sysconfig module\n')
        f.write('build_time_vars = ')
        pprint.pprint(vars, stream=f)
    with open('pybuilddir.txt', 'w', encoding='ascii') as (f):
        f.write(pybuilddir)


def _init_posix(vars):
    name = _get_sysconfigdata_name()
    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)
    build_time_vars = _temp.build_time_vars
    vars.update(build_time_vars)


def _init_non_posix(vars):
    vars['LIBDEST'] = get_path('stdlib')
    vars['BINLIBDEST'] = get_path('platstdlib')
    vars['INCLUDEPY'] = get_path('include')
    vars['EXT_SUFFIX'] = '.pyd'
    vars['EXE'] = '.exe'
    vars['VERSION'] = _PY_VERSION_SHORT_NO_DOT
    vars['BINDIR'] = os.path.dirname(_safe_realpath(sys.executable))


def parse_config_h(fp, vars=None):
    if vars is None:
        vars = {}
    import re
    define_rx = re.compile('#define ([A-Z][A-Za-z0-9_]+) (.*)\n')
    undef_rx = re.compile('/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n')
    while 1:
        line = fp.readline()
        if not line:
            break
        m = define_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            try:
                v = int(v)
            except ValueError:
                pass

            vars[n] = v
        else:
            m = undef_rx.match(line)
            if m:
                vars[m.group(1)] = 0

    return vars


def get_config_h_filename():
    if _PYTHON_BUILD:
        if os.name == 'nt':
            inc_dir = os.path.join(_sys_home or _PROJECT_BASE, 'PC')
        else:
            inc_dir = _sys_home or _PROJECT_BASE
    else:
        inc_dir = get_path('platinclude')
    return os.path.join(inc_dir, 'pyconfig.h')


def get_scheme_names():
    return tuple(sorted(_INSTALL_SCHEMES))


def get_path_names():
    return _SCHEME_KEYS


def get_paths(scheme=_get_default_scheme(), vars=None, expand=True):
    if expand:
        return _expand_vars(scheme, vars)
    return _INSTALL_SCHEMES[scheme]


def get_path(name, scheme=_get_default_scheme(), vars=None, expand=True):
    return get_paths(scheme, vars, expand)[name]


def get_config_vars(*args):
    global _CONFIG_VARS
    if _CONFIG_VARS is None:
        _CONFIG_VARS = {}
        _CONFIG_VARS['prefix'] = _PREFIX
        _CONFIG_VARS['exec_prefix'] = _EXEC_PREFIX
        _CONFIG_VARS['py_version'] = _PY_VERSION
        _CONFIG_VARS['py_version_short'] = _PY_VERSION_SHORT
        _CONFIG_VARS['py_version_nodot'] = _PY_VERSION_SHORT_NO_DOT
        _CONFIG_VARS['installed_base'] = _BASE_PREFIX
        _CONFIG_VARS['base'] = _PREFIX
        _CONFIG_VARS['installed_platbase'] = _BASE_EXEC_PREFIX
        _CONFIG_VARS['platbase'] = _EXEC_PREFIX
        _CONFIG_VARS['projectbase'] = _PROJECT_BASE
        try:
            _CONFIG_VARS['abiflags'] = sys.abiflags
        except AttributeError:
            _CONFIG_VARS['abiflags'] = ''

        if os.name == 'nt':
            _init_non_posix(_CONFIG_VARS)
        if os.name == 'posix':
            _init_posix(_CONFIG_VARS)
        SO = _CONFIG_VARS.get('EXT_SUFFIX')
        if SO is not None:
            _CONFIG_VARS['SO'] = SO
        _CONFIG_VARS['userbase'] = _getuserbase()
        srcdir = _CONFIG_VARS.get('srcdir', _PROJECT_BASE)
        if os.name == 'posix':
            if _PYTHON_BUILD:
                base = os.path.dirname(get_makefile_filename())
                srcdir = os.path.join(base, srcdir)
    else:
        srcdir = os.path.dirname(get_makefile_filename())
    _CONFIG_VARS['srcdir'] = _safe_realpath(srcdir)
    if sys.platform == 'darwin':
        import _osx_support
        _osx_support.customize_config_vars(_CONFIG_VARS)
    if args:
        vals = []
        for name in args:
            vals.append(_CONFIG_VARS.get(name))

        return vals
    return _CONFIG_VARS


def get_config_var(name):
    if name == 'SO':
        import warnings
        warnings.warn('SO is deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    return get_config_vars().get(name)


def get_platform():
    if os.name == 'nt':
        if 'amd64' in sys.version.lower():
            return 'win-amd64'
        else:
            return sys.platform
            return os.name != 'posix' or hasattr(os, 'uname') or sys.platform
        if '_PYTHON_HOST_PLATFORM' in os.environ:
            return os.environ['_PYTHON_HOST_PLATFORM']
        osname, host, release, version, machine = os.uname()
        osname = osname.lower().replace('/', '')
        machine = machine.replace(' ', '_')
        machine = machine.replace('/', '-')
        if osname[:5] == 'linux':
            return '%s-%s' % (osname, machine)
        if osname[:5] == 'sunos':
            if release[0] >= '5':
                osname = 'solaris'
                release = '%d.%s' % (int(release[0]) - 3, release[2:])
                bitness = {2147483647:'32bit', 
                 9223372036854775807:'64bit'}
                machine += '.%s' % bitness[sys.maxsize]
    elif osname[:3] == 'aix':
        return '%s-%s.%s' % (osname, version, release)
        if osname[:6] == 'cygwin':
            osname = 'cygwin'
            import re
            rel_re = re.compile('[\\d.]+')
            m = rel_re.match(release)
            if m:
                release = m.group()
    elif osname[:6] == 'darwin':
        import _osx_support
        osname, release, machine = _osx_support.get_platform_osx(get_config_vars(), osname, release, machine)
    return '%s-%s-%s' % (osname, release, machine)


def get_python_version():
    return _PY_VERSION_SHORT


def _print_dict(title, data):
    for index, (key, value) in enumerate(sorted(data.items())):
        if index == 0:
            print('%s: ' % title)
        print('\t%s = "%s"' % (key, value))


def _main():
    if '--generate-posix-vars' in sys.argv:
        _generate_posix_vars()
        return
    print('Platform: "%s"' % get_platform())
    print('Python version: "%s"' % get_python_version())
    print('Current installation scheme: "%s"' % _get_default_scheme())
    print()
    _print_dict('Paths', get_paths())
    print()
    _print_dict('Variables', get_config_vars())


if __name__ == '__main__':
    _main()