import time
import xbmc
import xbmcaddon
import subprocess
import os
import shutil
import stat

__addon__ = xbmcaddon.Addon(id='service.apcupsd')
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('path'))
__userdir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
APCUPSD_BIN_PATH = os.path.join(__addondir__, 'resources/lib/apcupsd/sbin/apcupsd')
APCUPSD_CONF_PATH = os.path.join(__userdir__, 'apcupsd.conf')
LOCKFILE_PATH = '/run/apcupsd'
APCUPSD_EXAMPLE_CONF_PATH = os.path.join(__addondir__, 'resources/lib/apcupsd/etc/apcupsd/apcupsd.conf')
EXE_FILES = ['/etc/apcupsd/apccontrol',
             '/etc/apcupsd/changeme',
             '/etc/apcupsd/commfailure',
             '/etc/apcupsd/commok',
             '/etc/apcupsd/offbattery',
             '/etc/apcupsd/onbattery',
             '/sbin/apcaccess',
             '/sbin/apctest',
             '/sbin/apcupsd',
             '/sbin/smtp']

FULL_PATH_EXE_FILES = [os.path.join(__addondir__, 'resources/lib/apcupsd', f) for f in EXE_FILES]

def __set_executable(f):
    st = os.stat(f)
    if not (st.st_mode & stat.S_IEXEC):
        os.chmod(f, st.st_mode | stat.S_IEXEC)

def __check_files():
    if not os.path.exists(LOCKFILE_PATH):
        os.makedirs(LOCKFILE_PATH)
    if not os.path.exists(APCUPSD_CONF_PATH):
        if not os.path.exists(__userdir__):
            os.makedirs(__userdir__)
        shutil.copyfile(APCUPSD_EXAMPLE_CONF_PATH, APCUPSD_CONF_PATH)
    for f in FULL_PATH_EXE_FILES:
        __set_executable(f)

class ApcupsdInstance(object):
    def __init__(self, bin_path, conf_path):
        self.bin_path = bin_path
        self.conf_path = conf_path
        self.started = False
        self.pid = None

    def start(self):
        __check_files()
        if not self.started:
            self.pid = subprocess.Popen([self.bin_path, '-f', self.conf_path])

    def stop(self):
        if self.started:
            if self.pid.poll() is None:
                self.pid.terminate()

    def restart(self):
        self.stop()
        self.start()

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    apcupsd = ApcupsdInstance(APCUPSD_BIN_PATH, APCUPSD_CONF_PATH)
    apcupsd.start()
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort():
            # Abort was requested while waiting. We should exit
            break

    apcupsd.stop()
