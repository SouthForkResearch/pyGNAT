import os

def InitDebug():
    """This module is used for remotely debugging the GNAT Plugin"""
    if 'DEBUG_PLUGIN' in os.environ and os.environ['DEBUG_PLUGIN'] == "GNATPlugin":
        import pydevd
        pydevd.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True, suspend=False)