"""
Maya scene specific context managers.
"""


# ----------------------------------------------------------------------------------------------- #
# IMPORTS
from maya import cmds
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class BypassSceneName(object):
    """
    Context Manager for temporarily renaming the Maya scene.
    e.g. for saving a copy of the current scene under a different name.
    e.g. for generating animation clip names during FBX export.
    """
    def __init__(self, tempName):
        """
        :param tempName: (str) temporary name of the Maya scene.
        """
        self.sceneName = cmds.file(sceneName=True, q=True)
        directory = os.path.dirname(self.sceneName)
        self.newName = '{}/{}.ma'.format(directory, tempName)

    def __enter__(self):
        cmds.file(rename=self.newName)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        cmds.file(rename=self.sceneName)
# ----------------------------------------------------------------------------------------------- #
