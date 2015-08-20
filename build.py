import platform
import os

if platform.system() == 'Linux':
    os.system('python setup.py build_ext --inplace --force')

elif platform.system() == 'Windows':
    # use Microsoft visual C compiler
    #os.system('SET VS90COMNTOOLS=%VS120COMNTOOLS%')
    os.putenv('VS90COMNTOOLS',os.getenv('VS120COMNTOOLS'))
    os.system('python setup.py build_ext --inplace --force -c msvc')
