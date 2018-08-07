"""
This setup.py script and other related installation scripts are adapted from
https://github.com/choderalab/yank/blob/master/setup.py
"""
from __future__ import print_function
import distutils.extension
from setuptools import setup, Extension, find_packages
from os.path import relpath, join
import os, sys, ast, pip, subprocess

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = "Error reading README"

#from Cython.Build import cythonize
DOCLINES = __doc__.split("\n")

########################
VERSION = "0.2.2"  # Primary base version of the build
DEVBUILD = "1"  # Dev build status, Either None or Integer as string
ISRELEASED = False  # Are we releasing this as a full cut?
__version__ = VERSION
########################

CLASSIFIERS = """\
Development Status :: 1 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: The MIT License (MIT)
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Chemistry
Operating System :: Unix
"""

################################################################################
# Writing version control information to the module
################################################################################


def git_version():
    # Return the git revision as a string
    # copied from numpy setup.py
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'PYTHON'
        env['LANG'] = 'PYTHON'
        env['LC_ALL'] = 'PYTHON'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = 'Unknown'

    return GIT_REVISION


def write_version_py(filename='blues/version.py'):
    cnt = """
# This file is automatically generated by setup.py
short_version = '{base_version:s}'
build_number = '{build_number:s}'
version = '{version:s}'
full_version = '{full_version:s}'
git_revision = '{git_revision:s}'
release = {isrelease:s}
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    base_version = VERSION
    if DEVBUILD is not None and DEVBUILD != "None":
        local_version = base_version + ".dev" + DEVBUILD
    else:
        local_version = base_version
    full_version = local_version

    if os.path.exists('.git'):
        git_revision = git_version()
    else:
        git_revision = 'Unknown'

    if not ISRELEASED:
        full_version += '-' + git_revision[:7]

    a = open(filename, 'w')
    try:
        a.write(
            cnt.format(
                base_version=base_version,  # Base version e.g. X.Y.Z
                build_number=DEVBUILD,  # Package build number
                version=
                local_version,  # Flushed out version, usually just base, but can be X.Y.Z.devN
                full_version=
                full_version,  # Full version + git short hash, unless released
                git_revision=git_revision,  # Matched full github hash
                isrelease=str(ISRELEASED)))  # Released flag
    finally:
        a.close()


def write_meta_yaml(filename='devtools/conda-recipe/meta.yaml'):
    d = {}
    with open('blues/version.py') as f:
        data = f.read()
    lines = data.split('\n')

    keys = ['short_version', 'build_number']
    for line in lines:
        for k in keys:
            if k in line:
                (key, val) = line.split('=')
                d[key.strip()] = val.strip().strip("'")

    with open(filename, 'r') as meta:
        yaml_lines = meta.readlines()

    a = open(filename, 'w')
    try:
        for k, v in d.items():
            a.write("{{% set {} = '{}' %}}\n".format(k, v))
        #Replace top 2 header lines that contain the package version
        a.writelines(yaml_lines[2:])
    finally:
        a.close()


################################################################################
# USEFUL SUBROUTINES
################################################################################
#def read(fname):
#    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_package_data(data_root, package_root):
    files = []
    for root, dirnames, filenames in os.walk(data_root):
        for fn in filenames:
            files.append(relpath(join(root, fn), package_root))
    return files


def check_dependencies():
    from distutils.version import StrictVersion
    found_openmm = True
    found_openmmtools = True
    found_openmm_711_or_earlier = True
    found_numpy = True

    try:
        from simtk import openmm
        openmm_version = StrictVersion(openmm.Platform.getOpenMMVersion())
        if openmm_version < StrictVersion('7.1.1'):
            found_openmm_711_or_earlier = False
    except ImportError as err:
        found_openmm = False

    try:
        import numpy
    except:
        found_numpy = False

    try:
        import openmmtools
    except:
        found_openmmtools = False

    msg = None
    bar = ('-' * 70) + "\n" + ('-' * 70)
    if found_openmm:
        if not found_openmm_711_or_earlier:
            msg = [
                bar,
                '[Unmet Dependency] BLUES requires OpenMM version 7.1.1. You have version %s.'
                % openmm_version, bar
            ]
    else:
        msg = [
            bar,
            '[Unmet Dependency] BLUES requires the OpenMM python package. Please install with `conda install -c omnia openmm=7.1.1` ',
            bar
        ]

    if not found_numpy:
        msg = [
            bar,
            '[Unmet Dependency] BLUES requires the numpy python package. Refer to <http://www.scipy.org/scipylib/download.html> for numpy installation instructions.',
            bar
        ]

    if not found_openmmtools:
        msg = [
            bar,
            '[Unmet Dependency] BLUES requires the openmmtools python package. Please install with `conda install -c omnia openmmtools=0.14.0`',
            bar
        ]

    if msg is not None:
        import textwrap
        print()
        print(
            os.linesep.join([line for e in msg for line in textwrap.wrap(e)]),
            file=sys.stderr)
        #print('\n'.join(list(textwrap.wrap(e) for e in msg)))


################################################################################
# SETUP
################################################################################
write_version_py('blues/version.py')
write_meta_yaml('devtools/conda-recipe/meta.yaml')
setup(
    name='blues',
    author=
    "Samuel C. Gill, Nathan M. Lim, Kalistyn Burley, David L. Mobley, and others",
    author_email='dmobley@uci.edu',
    description=("NCMC moves in OpenMM to enhance ligand sampling"),
    long_description=long_description,
    version=__version__,
    license='MIT',
    url='https://github.com/MobleyLab/blues',
    platforms=['Linux-64', 'Mac OSX-64', 'Unix-64'],
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'blues': 'blues'},
    packages=['blues', "blues.tests", "blues.tests.data"] +
    ['blues.{}'.format(package) for package in find_packages('blues')],
    package_data={
        'blues':
        find_package_data('blues/tests/data', 'blues') + ['notebooks/*.ipynb']
        + ['images/*']
    },
    install_requires=[
        'numpy', 'cython', 'scipy', 'openmm', 'parmed', 'mdtraj', 'pandas',
        'netCDF4', 'pyyaml', 'pytest',
    ],
    extras_require={
        'docs': [
            'sphinx',  # autodoc was broken in 1.3.1
            'sphinxcontrib-napoleon',
            'sphinx_rtd_theme',
            'numpydoc',
        ],
        'tests': [
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],
    },
    zip_safe=False,
    include_package_data=True)
check_dependencies()
