import maya.cmds as cmds
from functools import partial

class RDojo_UI:

    def __init__(self, *args):
        activeMenus = cmds.window('MayaWindow', q = True, ma = True)
        for a in activeMenus:
            if a == 'RDojo_Menu':
                cmds.deleteUI('RDojo_Menu', m = True)

        myMenu = cmds.menu('RDojo_Menu', l = 'RDMenu', to = True, p = 'MayaWindow')
        cmds.menuItem(l = 'Rig Tool', p =  myMenu, command = self.ui)

        self.uiElements = {}
        self.uiInfo = {}

        self.rigmodlist = []
        rigcontents = os.listdir(os.environ["RIGGING_TOOL"] + '/rig')
        for mod in rigcontents:
            if '.pyc' not in mod and '__init__' not in mod:
                self.rigmodlist.append(mod)

        print self.rigmodlist


        print 'Rig_Arm'

    def ui(self, *args):
        windowName = 'ARWindow'
        if cmds.window(windowName, exists = True):
            cmds.deleteUI(windowName)


        windowHeight = 400
        windowWidth = 300
        buttonHeight = 200
        buttonWidth = 150

        self.uiElements['window'] = cmds.window(windowName, w = windowWidth, h = windowHeight, t = 'Auto Rig V 0.5', sizeable = True, mnb = True)

        self.uiElements['mainColLayout'] = cmds.columnLayout("mainColLayout", w = windowWidth, adj = True)
        self.uiElements['layoutFrameLayout'] = cmds.frameLayout ("layoutTab", w = windowWidth, label = "Layout", cll = True, p = self.uiElements['mainColLayout'])

        self.uiElements['layoutButton'] = cmds.button(l= 'Generate Layout', w = windowWidth, h = buttonHeight/2, c = self.riglayout)
        self.uiElements['symmArmLayout'] = cmds.rowColumnLayout("Symm", numberOfColumns = 3, columnWidth = [(1, windowWidth/3), (2, windowWidth/3),(3, windowWidth/3)])
        cmds.text(l = ' ')
        self.uiElements['symmBox'] = cmds.checkBox( "symmBox", label = "Symmetry")
        cmds.text(l = ' ')
        cmds.separator( width = windowWidth, style='none', h = 5)


        self.uiElements['optionsFrameLayout'] = cmds.frameLayout ("optionsTab", w = windowWidth, label = "Options", cll = True, p = self.uiElements['mainColLayout'])
        self.uiElements['optionsTabLayout'] = cmds.tabLayout(w=windowWidth,
                                                                   p=self.uiElements['optionsFrameLayout'])

        for mod in self.rigmodlist:

            self.uiElements['optionsArmLayout'+mod] = cmds.rowColumnLayout(mod, numberOfColumns = 2, columnWidth = [(1, windowWidth/2), (2, windowWidth/2)], p=self.uiElements['optionsTabLayout'])

            self.uiElements['stretchBox'+mod] = cmds.checkBox( "stretchBox", label = "Stretch")
            self.uiElements['twistBox'+mod] = cmds.checkBox( "twistBox", label = "Twist Joints")
            cmds.separator( width = windowWidth, style='none', h = 10,  p = self.uiElements['optionsArmLayout'+mod])

            self.uiElements['modFrameLayout'+mod] = cmds.frameLayout ("ModuleTab"+mod, w = windowWidth, label = "Modules"+mod, cll = True)
            #self.uiElements['modFlowLayout'+mod] = cmds.flowLayout("moduleFlowLayout", v = False, w = windowWidth, h = windowHeight/2, wr = True)

            self.uiElements[mod + '_Button'] = cmds.button(l= mod, w = buttonWidth, h = buttonHeight/2, c = partial(self.rig_mod, mod))
            print self.uiElements['optionsTabLayout']
            cmds.tabLayout(self.uiElements['optionsTabLayout'], edit=True, tabLabel=(self.uiElements['optionsArmLayout'+mod], mod))
        #self.uiElements['legButton'] = cmds.button(l= 'Leg', w = buttonWidth, h = buttonHeight/2, c =  self.rig_leg)
        #self.uiElements['spineButton'] = cmds.button(l= 'Spine', w = buttonWidth, h = buttonHeight/2, c =  self.filler)
        #self.uiElements['footButton'] = cmds.button(l= 'Foot', w = buttonWidth, h = buttonHeight/2, c =  self.filler)




        cmds.showWindow(self.uiElements['window'])

    def rig_mod(self, mod, *args):
        print mod


    def riglayout(self, *args):
        import layout.rig_Layout as rig_Layout
        reload(rig_Layout)
        ly = rig_Layout.Layout()
        ly.importCoord()
        ly.createLayout()

    def filler(*args):
        print 'I do nothing yet'



