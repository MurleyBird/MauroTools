import maya.cmds as cmds
import system.utils as utils
import os
from collections import OrderedDict
import json

class Layout:
	
	def __init__(self):
		self.rlayout = {}
		self.layoutLog = {}
		self.symmCheckbox = cmds.checkBox('symmBox', q = True, v = True)
		self.layoutPath = os.environ["RDOJO_DATA"] + '/layoutPositions.json'
		

	def importCoord(self, *args):
		importLayout = utils.readJson(self.layoutPath)
		self.rlayout = json.loads(importLayout, object_pairs_hook=OrderedDict)
		print 'Importing Coordinates'

	def createLayout(self):
		self.importCoord(self.layoutPath)
		self.symmTargets_L = []
		self.symmTargets_R = []
		self.layoutObjs = []
		keys = self.rlayout.keys()

		for k in keys:
			side = k.split('_')
			if side[1] == 'L': 
				self.symmTargets_L.append(k)
			elif side[1] == 'R':
				self.symmTargets_R.append(k)

		for key, value in self.rlayout.iteritems():
			self.currentLayout = []
			for k, val in value.iteritems():
				self.currentLayout.append(cmds.joint(n = k, p = val))
				if self.currentLayout.index(k) != 0:
					cmds.joint(self.currentLayout[self.currentLayout.index(k)-1], e = True, zso = True, oj = 'xyz', sao = 'yup')
			self.layoutObjs.append(self.currentLayout)
			cmds.select(d=True)

		symmCons = self.layoutSymmetry()
		for s in symmCons:
			cmds.delete(s)		
		
		for lay in self.layoutObjs:
			for l in lay:
				currentMan = self.layoutManipulators(l)
				manTrans = cmds.xform(l, ws = True, q = True, t = True)
				manRot = cmds.xform(l, ws = True, q = True, ro = True)
				cmds.move(manTrans[0], manTrans[1], manTrans[2], currentMan)
				cmds.rotate(manRot[0], manRot[1], manRot[2], currentMan)

		if 	self.symmCheckbox == True:
			self.layoutSymmetry()




	def layoutSymmetry(self):
		counter = 0
		cons = []
		#variables for both keys to store their internal keys#
		for s in self.symmTargets_L:
			rBones = self.rlayout[self.symmTargets_R[counter]].keys()
			keyCounter = 0
			for key in self.rlayout[self.symmTargets_L[counter]].iteritems():
				currentCons = utils.symmetryConstraint(key[0], rBones[keyCounter])
				cons.append(currentCons)
				keyCounter += 1
				cmds.select(d = True)
			counter += 1
		return cons
		print 'Generating Layout'

	def layoutManipulators(self, name):
		manipulatorShapes = []
		currentCube = cmds.polyCube(n = str(name) + '_Manipulator', d = 0.5, w = 0.5, h = 0.5)[0]
		manipulatorShapes.append(currentCube)
		cmds.polyExtrudeFacet(currentCube + '.f[4]', ltz = 2.5)
		duplicateA = cmds.duplicate(currentCube)[0]
		manipulatorShapes.append(duplicateA)
		cmds.rotate(0,0,'90deg', duplicateA)
		duplicateB = cmds.duplicate(currentCube)[0]
		manipulatorShapes.append(duplicateB)
		cmds.rotate(0, '-90deg', 0, duplicateB)
		utils.shapeCombine(manipulatorShapes)
		cmds.setAttr(currentCube + 'Shape.overrideEnabled', 1)
		cmds.setAttr(currentCube + 'Shape.overrideLevelOfDetail', 1)
		cmds.setAttr(currentCube + 'Shape.overrideColor', 13)
		cmds.setAttr(duplicateA + 'Shape.overrideEnabled', 1)
		cmds.setAttr(duplicateA + 'Shape.overrideLevelOfDetail', 1)
		cmds.setAttr(duplicateA + 'Shape.overrideColor', 14)
		cmds.setAttr(duplicateB + 'Shape.overrideEnabled', 1)
		cmds.setAttr(duplicateB + 'Shape.overrideLevelOfDetail', 1)
		cmds.setAttr(duplicateB + 'Shape.overrideColor', 6)
		return currentCube