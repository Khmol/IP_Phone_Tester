# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt5. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# Run the build process by running the command
#
# C:\Python34\python.exe setup.py build
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys, os.path
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': 'atexit'
    }
}

executables = [
    Executable( os.path.abspath('Tester_AKB.py'), base = base, icon = '75.ico')
]

setup(name='Discharge_Tester',
      version='1.0',
      description='Discharge_Tester',
      options=options,
      executables=executables
      )
