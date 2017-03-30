import maya.cmds as cmds
import os

print 'Startup'

cmds.currentUnit( linear = 'cm')
print 'Setting units to Centimeters'

cmds.currentUnit( time = 'ntsc')
print 'Setting time to NTSC 30 fps'

os.environ["RDOJO_DATA"] = os.environ["RIGGING_TOOL"] + '/layout'

import ui.ui as ui
reload(ui)
ui.RDojo_UI()