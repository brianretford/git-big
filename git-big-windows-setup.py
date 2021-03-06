import os
import subprocess
import sys
    
import win32com.shell.shell as shell
import win32api, win32con

def spawn_as_administrator():
    """ Spawn ourself with administrator rights and wait for new process to exit
        Make the new process use the same console as the old one.
          Raise Exception() if we could not get a handle for the new re-run the process
          Raise pywintypes.error() if we could not re-spawn
        Return the exit code of the new process,
          or return None if already running the second admin process. """
    #pylint: disable=no-name-in-module,import-error
    import win32event, win32process
    if '--admin' in sys.argv:
        return None
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:] + ['--admin'])
    SEE_MASK_NOCLOSE_PROCESS = 0x00000040
    process = shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params, fMask=SEE_MASK_NOCLOSE_PROCESS)
    hProcess = process['hProcess']
    if not hProcess:
        raise Exception("Could not get admin privileges")
    # It is necessary to wait for the elevated process or else
    #  stdin lines are shared between 2 processes: they get one line each
    INFINITE = -1
    win32event.WaitForSingleObject(hProcess, INFINITE)
    exitcode = win32process.GetExitCodeProcess(hProcess)
    win32api.CloseHandle(hProcess)
    return exitcode

def main():
    rkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock", 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(rkey, "AllowDevelopmentWithoutDevLicense", 0, win32con.REG_DWORD, 1)
    cmds = [['git', 'config', '--system', 'core.symlinks', 'true'],
            ['git', 'config', '--global', 'core.symlinks', 'true'],
            ['git', 'config', 'core.symlinks', 'true'],]
    for cmd in cmds:
      subprocess.check_call(cmd, shell=True)
    

if __name__ == '__main__':
    print("Enabling developer mode")
    print("Enabling git core.symlinks system wide")
    ret = spawn_as_administrator()
    if ret is None:
      main()
    elif ret != 0:
      print("Error configuring system.")
