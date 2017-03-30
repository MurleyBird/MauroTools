import maya.cmds as cmds
import json
import tempfile


def writeJson(fileName, data):
	with open (fileName, 'w') as outfile:
		json.dump(data, outfile)
	file.close(outfile)

def readJson(fileName):
	with open (fileName, 'r') as infile:
		data = (open(infile.name, 'r').read())
	return data

def colOverride(ext, controls):

	if ext == 'LA' or ext == 'LL':
		color = 6
	elif ext == 'RA' or ext == 'RL':
		color = 13
	elif ext == 'LA' or ext == 'LL':
		color = 17

	for c in controls:
		targetShape = cmds.listRelatives( c , s = True, pa = True)
		cmds.setAttr( str(targetShape[0]) + ".overrideEnabled", 1)
		cmds.setAttr( str(targetShape[0]) + ".overrideColor", color)
		shapeAmount = len(targetShape)
		if shapeAmount > 1:
			for t in targetShape[1:]:
				cmds.setAttr( str(t) + ".overrideEnabled", 1)
				cmds.setAttr( str(t) + ".overrideColor", color)

def symmetryConstraint(source, target):
    sourceType = cmds.nodeType(source)
    targetType = cmds.nodeType(target)
    currentCons = cmds.shadingNode('symmetryConstraint', au = True)    
    cmds.connectAttr(source + '.translate', currentCons + '.targetTranslate')  
    cmds.connectAttr(source + '.rotate', currentCons + '.targetRotate')  
    cmds.connectAttr(source + '.scale', currentCons + '.targetScale')  
    cmds.connectAttr(source + '.parentMatrix[0]', currentCons + '.targetParentMatrix')  
    cmds.connectAttr(source + '.worldMatrix[0]', currentCons + '.targetWorldMatrix')  
    cmds.connectAttr(source + '.rotateOrder', currentCons + '.targetRotateOrder')  
    cmds.connectAttr(currentCons + '.constraintTranslate', target + '.translate')  
    cmds.connectAttr(currentCons + '.constraintRotate', target + '.rotate')  
    cmds.connectAttr(currentCons + '.constraintScale', target + '.scale')  
    cmds.connectAttr(currentCons + '.constraintRotateOrder', target + '.rotateOrder')  
    cmds.connectAttr(target + '.parentInverseMatrix[0]', currentCons + '.constraintInverseParentWorldMatrix')
    if sourceType == 'joint' and targetType == 'joint':
        cmds.connectAttr(source + '.jointOrient', currentCons + '.target.targetJointOrient')
        cmds.connectAttr(currentCons + '.constrained.constraintJointOrient', target + '.jointOrient')
    cmds.parent(currentCons, target)
    return currentCons

def shapeCombine(target):

	parentCtrls = []

	for t in target:
		cmds.makeIdentity(t, a = True, r = True)
		parentCtrls.append(t)

	cmds.parent(cmds.listRelatives(parentCtrls[1:], s = True, pa = True), parentCtrls[0],  r = True, s = True)

	cmds.select(clear = True)

	cmds.delete(parentCtrls[1:])