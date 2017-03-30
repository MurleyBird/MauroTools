import maya.cmds as cmds
from functools import partial
from importlib import import_module
import os

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
		print rigcontents
		for m in rigcontents:
			if '.pyc' not in m and '__init__' not in m:
				self.rigmodlist.append(m)
		

		print 'Rig_Arm'
		
	def ui(self, *args):
		windowName = 'ARWindow'
		if cmds.window(windowName, exists = True):
			cmds.deleteUI(windowName)

		
		windowHeight = 400
		windowWidth = 303
		buttonHeight = 200
		buttonWidth = 150

		self.uiElements['window'] = cmds.window(windowName, w = windowWidth, h = windowHeight, t = 'Auto Rig V 0.5', sizeable = True, mnb = True)

		self.uiElements['mainColLayout'] = cmds.columnLayout("mainColLayout", w = windowWidth, adj = True)
		self.uiElements['layoutFrameLayout'] = cmds.frameLayout ("layoutTab", w = windowWidth, label = "Layout", cll = True, p = self.uiElements['mainColLayout'])

		self.uiElements['layoutButton'] = cmds.button(l= 'Generate Layout', w = windowWidth, h = buttonHeight/2, c = self.riglayout)
		self.uiElements['symmArmLayout'] = cmds.rowColumnLayout("Symm", numberOfColumns = 3, columnWidth = [(1, windowWidth/4), (2, windowWidth/1.3)])
		self.uiElements['symmBox'] = cmds.checkBox( "symmBox", label = "Symmetry")
		cmds.text(l = '*Note: Activate before generating.')
		cmds.separator( width = windowWidth, style='none', h = 3,  p = self.uiElements['layoutFrameLayout'])
		

		
		self.uiElements['optionsFrameLayout'] = cmds.frameLayout ("optionsTab", w = windowWidth, label = "Options", cll = True, p = self.uiElements['mainColLayout']) 
		self.uiElements['optionsTabLayout'] = cmds.tabLayout('optionsTabs', w = windowWidth)

		##Using the file list gathered form the directory we do a for loop creating ui elements for each module##
		for m in self.rigmodlist:
			name = m.split('.')
			print name
			self.uiElements['options'+ name[0] +'Layout'] = cmds.rowColumnLayout(name[0], numberOfColumns = 2, columnWidth = [(1, windowWidth/2), (2, windowWidth/2)], p =self.uiElements['optionsTabLayout'])

			mod = __import__("rig." + name[0], {}, {}, name[0])
			moduleClass = getattr(mod, mod.classname)
			moduleInstance = moduleClass()
			self.uiElements[name[0] + 'Boxes'] = moduleInstance.ui(name[0])
		
			cmds.separator( width = windowWidth, style='none', h = 10,  p = self.uiElements['options'+ name[0] +'Layout'])

		##Since the boxes are in a different part of the UI, we need to do a separate for loop for the##
		self.uiElements['modFrameLayout'] = cmds.frameLayout ("ModuleTab", w = windowWidth, label = "Modules", cll = True, p = self.uiElements['mainColLayout'])
		self.uiElements['modFlowLayout'] = cmds.flowLayout("moduleFlowLayout", v = False, w = windowWidth, h = windowHeight/2, wr = True)
		for m in self.rigmodlist:
			name = m.split('.')[0]
			self.uiElements[name + 'Button'] = cmds.button(l= name, w = buttonWidth, h = buttonHeight/2, c = partial(self.modules, name), p = self.uiElements['modFlowLayout'])
	


		cmds.showWindow(self.uiElements['window'])

	def modules(self, name, *args):
		if name == 'Arm':
			self.arm_rig()
		elif name == 'Leg':
			self.leg_rig()

	def arm_rig(self, *args):
		#import the module with an alias
		import rig.Arm as arm_rig
		reload(arm_rig)
		#store the class within a variable
		rig_arm = arm_rig.rig_arm()
		print 'Rigging Arm'
		#excecute the arm bulding function from within the variable that houses the class
		self.stretch = cmds.checkBox(self.uiElements['ArmBoxes'][0], q = True, v = True)
		rig_arm.rig_arm(self.stretch)


	def leg_rig(self, *args):
		#import the module with an alias
		import rig.Leg as leg_rig
		reload(leg_rig)
		#store the class within a variable
		rig_leg = leg_rig.rig_leg()
		print 'Rigging Leg'
		print self.uiElements['LegBoxes']
		#excecute the arm bulding function from within the variable that houses the class
		self.stretch = cmds.checkBox(self.uiElements['LegBoxes'][0], q = True, v = True)
		rig_leg.rig_leg(self.stretch)

	def riglayout(self, *args):
		import layout.rig_Layout as rig_Layout
		reload(rig_Layout)
		ly = rig_Layout.Layout()
		ly.importCoord()
		ly.createLayout()

	def filler(*args):
		print 'I do nothing yet'



