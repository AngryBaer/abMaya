"""
Maya attribute specific context managers.
"""


# IMPORTS --------------------------------------------------------------------------------------- #
import os
from maya import cmds
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class BypassValue(object):
    """
    Context Manager for temporarily renaming the Maya scene.
    e.g. for saving a copy of the current scene under a different name.
    e.g. for generating animation clip names during FBX export.
    """
    def __init__(self, channel, tempValue=None):
        """
        :param channel:  bypassed channel.
                          - str
        :param tempName: temporary value of the channel.
                          - bool
                          - str
                          - int
                          - float
                          - enum

        :return None:
        """
        # NOTE: WIP assertions
        self.channel = channel
        self.oldValue = cmds.getAttr(self.channel, q=True)
        self.newvalue = tempValue

    def __enter__(self):
        cmds.setAttr(self.channel, self.newvalue)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        cmds.setAttr(self.channel, self.oldValue)
# ----------------------------------------------------------------------------------------------- #


# NOTE: WIP, lock/unlock attribute
# NOTE: WIP, key/unkey
# NOTE: WIP, all channels