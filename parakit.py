def input_exit():
    print()
    input("Press Enter to close the program. ")
    exit()

#Extreme sanity check
try:
    import venv
    import sys
    import os
    import platform
    import subprocess
except ImportError as e:
    print(f"Setup error: Error while importing standard libraries: {e}\nIf you see this message, please contact the developer!")
    input_exit()

_venv_path = 'venv'
_reqs_path = 'requirements.txt'
_worker_script_path = 'state_reader.py'
_vcheck_script_path = 'version_check.py'

#Create venv if not already created
if not os.path.isfile(os.path.join(_venv_path, 'pyvenv.cfg')):
    if os.path.exists(_venv_path):
        print(f"Setup error: The venv folder at '{_venv_path}' appears to be corrupted (missing config file).")
        print("Fix the issue or delete the folder and run this script again.")
        input_exit()

    venv.create(_venv_path, with_pip=True)
    print(f"Setup: venv created at '{_venv_path}'")
    print("\nIf this is your first time using ParaKit, welcome!")
    print("Please give us a moment to finish setting up.\nIt should take about a minute.\n")
    print("If it seems to do no progress at all for a while, try pressing Enter. Python's weird.")

if os.path.exists(os.path.join(_venv_path, 'Scripts')): #Windows
    _pip_exe = os.path.join(_venv_path, 'Scripts', 'pip')
    _python_exe = os.path.join(_venv_path, 'Scripts', 'python')
elif os.path.exists(os.path.join(_venv_path, 'bin')): #Unix
    _pip_exe = os.path.join(_venv_path, 'bin', 'pip')
    _python_exe = os.path.join(_venv_path, 'bin', 'python')
else:
    print("Setup error: Python created an unusual or broken virtual environment.")
    print("Try updating to the latest Python version.")
    input_exit()

#Install missing required packages in the venv
def get_installed_packages(venv_path):
    result = subprocess.run([_pip_exe, "freeze"], capture_output=True, text=True)
    return {line.split('==')[0] for line in result.stdout.splitlines()}

def get_required_packages(requirements_path):
    with open(requirements_path) as reqs:
        return {line.strip() for line in reqs if line and not line.startswith('#')}

if get_required_packages(_reqs_path) - get_installed_packages(_venv_path):
    print("Setup: Missing packages detected; running pip install.")
    try:
        subprocess.check_call([_pip_exe, "install", "-r", _reqs_path])
        print(f"Setup: All required modules installed to '{_venv_path}'")
    except subprocess.CalledProcessError as e:
        print(f"Setup error: Error occurred while installing requirements.txt modules: {e}")
        input_exit()
else:
    print(f"Setup: Requirements all good.")

#Run state-reader
subprocess.run([_python_exe, _worker_script_path])

#Inform users if running non-latest version
subprocess.run([_python_exe, _vcheck_script_path])

#Prevent instant exit
input_exit()