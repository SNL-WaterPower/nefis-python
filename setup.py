from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from distutils.core import setup
from distutils.extension import Extension
import numpy as np
try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

cmdclass = { }
ext_modules = [ ]

import platform

if platform.system() == 'Linux':
    nefis_libs_loc = "/home/ccchart/wrkdir/SVN/4970/src/utils_lgpl/nefis/packages/nefis/src_so/.libs"

    if use_cython:
        ext_modules += [
            Extension(  "nefis",
                        [ "nefis.pyx" ],
                        #libraries=["nefis"],
                        libraries=["NefisSO"],
                        library_dirs = [nefis_libs_loc],
                        runtime_library_dirs = [nefis_libs_loc],
                        include_dirs=[np.get_include()]
                        ),
        ]
        cmdclass.update({ 'build_ext': build_ext })
    else:
        print("Import failed (statement): 'from Cython.Distutils import build_ext'")

elif platform.system() == 'Windows':
    #nefis_libs_loc = r"""C:\Users\ccchart\Desktop\GitHub\Delft3D\src\utils_lgpl\nefis\lib\Release\dynamic"""
    #nefis_libs_loc = r"""C:\Users\ccchart\Desktop\GitHub\Delft3D\src\utils_lgpl\nefis\lib\Release\static"""
    nefis_libs_loc = r"""Z:\SVN\4970-win\src\utils_lgpl\nefis\lib\x64\Release\dynamic"""

    if use_cython:
        ext_modules += [
            Extension(  "nefis",
                        [ "nefis.pyx" ],
                        libraries=["nefis_dll"],
                        library_dirs = [nefis_libs_loc],
                        #runtime_library_dirs = [nefis_libs_loc],
                        include_dirs=[np.get_include()]
                        ),
        ]
        cmdclass.update({ 'build_ext': build_ext })
    else:
        print("Import failed (statement): 'from Cython.Distutils import build_ext'")

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nefis',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.2.0',

    description='NEFIS library',
    long_description=long_description,

    # The project's main homepage.
    #url='https://github.com/openearth/nefis-python',
    url='http://oss.deltares.nl/web/delft3d',

    # Author details
    author='Jan Mooiman',
    author_email='jan.mooiman@deltares.nl',

    # Choose your license
    license='LGPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Microsoft :: Windows',
    ],

    # What does your project relate to?
    keywords='nefis file_format',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['contrib', 'docs']),
    packages=find_packages('.'),
    #packages=find_packages('data'),
    package_data = {'data': ['*.dat'] },
    #data_files=[('data', ['trim-f34.dat', 'data/trim-f34.def'])],

    cmdclass = cmdclass,
    ext_modules=ext_modules,
    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['numpy'],

    include_dirs = [np.get_include()],


    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'nefisdump=nefis:dump',
        ],
    },
)
