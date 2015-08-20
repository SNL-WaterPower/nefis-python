del nefis.c
del nefis.pyd
rem del nefis.dll
del nefis.pdb
rem del nefis.lib
rem copy d:\svn-checkouts\ds\trunk\guis\utils_lgpl\nefis\lib\x64\Debug\dynamic\nefis.dll nefis.dll
rem copy d:\svn-checkouts\ds\trunk\guis\utils_lgpl\nefis\lib\x64\Debug\dynamic\nefis.pdb nefis.pdb
rem copy d:\svn-checkouts\ds\trunk\guis\utils_lgpl\nefis\lib\x64\Debug\dynamic\nefis_dll.lib nefis.lib

rem copy C:\Users\ccchart\Desktop\GitHub\Delft3D\src\utils_lgpl\nefis\lib\Release\dynamic\nefis.dll nefis.dll
rem copy C:\Users\ccchart\Desktop\GitHub\Delft3D\src\utils_lgpl\nefis\lib\Release\dynamic\nefis.pdb nefis.pdb
rem copy C:\Users\ccchart\Desktop\GitHub\Delft3D\src\utils_lgpl\nefis\lib\Release\dynamic\nefis_dll.lib nefis.lib

copy Z:\SVN\4970-win\src\utils_lgpl\nefis\lib\x64\Release\dynamic\nefis.dll nefis.dll
copy Z:\SVN\4970-win\src\utils_lgpl\nefis\lib\x64\Release\dynamic\nefis.pdb nefis.pdb
copy Z:\SVN\4970-win\src\utils_lgpl\nefis\lib\x64\Release\dynamic\nefis_dll.lib nefis.lib

python.exe setup.py build_ext --inplace
