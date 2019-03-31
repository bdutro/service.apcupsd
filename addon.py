import time
import xbmc
import xbmcaddon
import subprocess
import os
import shutil

__addon__ = xbmcaddon.Addon(id='service.apcupsd')
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('path'))
__userdir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
APCUPSD_BIN_PATH = os.path.join(__addondir__, 'resources/lib/apcupsd/sbin/apcupsd')
APCUPSD_CONF_PATH = os.path.join(__userdir__, 'apcupsd.conf')
LOCKFILE_PATH = '/run/apcupsd'
APCUPSD_EXAMPLE_CONF_PATH = os.path.join(__addondir__, 'resources/lib/apcupsd/etc/apcupsd.conf')

class ApcupsdInstance(object):
    def __init__(self, bin_path, conf_path):
        self.bin_path = bin_path
        self.conf_path = conf_path
        self.started = False
        self.pid = None

    def start(self):
        if not os.path.exists(LOCKFILE_PATH):
            os.makedirs(LOCKFILE_PATH)
        if not os.path.exists(APCUPSD_CONF_PATH):
            shutil.copyfile(APCUPSD_EXAMPLE_CONF_PATH, APCUPSD_CONF_PATH)
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
