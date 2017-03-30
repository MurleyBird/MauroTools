import maya.cmds as cmds
import system.utils as utils
import maya.OpenMaya as om

class Rig_Utils:

    def jointCreation(self, prefix, chainTypes, name, position, orient, extremity):
            joints = []
            for n in name:
                #For each chain created, it then creates each joint specified in the name argument #
                joints.append(cmds.joint(n = prefix + '_' + extremity + '_'+ chainTypes + '_' + n + '_jnt', p = position[n]))
                cmds.joint(n = prefix + '_' + extremity + '_'+ chainTypes + '_' + n + '_jnt', e = True, o = orient[n] )
                '''
                if name.index(n) != 0:
                    # If the joint isnt the first one, it will orient it's parent #
                    cmds.joint(prefix + '_' + extremity + '_' + chainTypes + '_' + name[name.index(n)-1] + '_jnt', e = True, zso = True, oj = 'xyz', sao = 'yup')
                '''
            cmds.select(d=True)
            return joints

    ## Get the positions from the layout objects ##
    def getCoords(self, ext, side):
        # Select all the layout objects by type#
        layoutObjs = cmds.ls(typ = 'joint')
        for l in layoutObjs:
            #Check to see if they should be taken into account for the arm#
            name = l.split('_')
            if name[0] == ext and name[2] == side:
                #List their transform node and query their position#
                name = l.split('_')[1]
                self.layoutPos[name] = cmds.xform(l, ws = True, q = True, t = True)


    def getOrients(self, ext, side):
        # Select all the layout objects by type#
        layoutObjs = cmds.ls(typ = 'joint')
        for l in layoutObjs:
            #Check to see if they should be taken into account for the arm#
            name = l.split('_')
            if name[0] == ext and name[2] == side:
                #Query their orient to be used in the rig creation#
                name = l.split('_')[1]
                self.layoutOrient[name] = cmds.joint(l, q = True, o = True)




        ## Creating the IK Arm ##
    def ikSystemCreation(self, startJoint, midJoint, endJoint, extremity):
        # Creating the IK handle    
        ikH = cmds.ikHandle( sj=startJoint, ee=endJoint, p=2, w=.5, n = extremity + '_ikHandle', sol = 'ikRPsolver')[0]
        
        # Creating the IK Arm Control   
        ikControl = cmds.circle(n = 'ctrl_IK_' + extremity, nr = (1,0,0))[0]
        ikGroup = cmds.group(ikControl, n = str(ikControl) + '_grp')
        
        # Query wrist location and rotation
        pos = cmds.xform(endJoint, ws = True, q=True, t=True)
        rot = cmds.xform(endJoint, ws = True, q=True, ro=True)
        
        # Snap the group to the wrist joint
        cmds.xform(ikGroup, t=pos, ws=True)
        cmds.xform(ikGroup, ro=rot, ws=True)
        
        # Constrain the handle to the control, and the control to the wrist rotation
        cmds.pointConstraint(ikControl, ikH, mo=True)
        cmds.orientConstraint(ikControl, endJoint, mo=True)
        
        # Creating and Positioning PV
        # Query shoulder Position and Vectors
        sRaw = cmds.xform(startJoint, q = True, ws = True, t = True)
        sPos = om.MVector(sRaw[0], sRaw[1], sRaw[2])
        
        #Query Elbow Position and Vectors
        eRaw = cmds.xform(midJoint, q = True, ws = True, t = True)
        ePos = om.MVector(eRaw[0], eRaw[1], eRaw[2])
        
        #Query Wrist Position and Vectors
        wRaw = cmds.xform(endJoint, q = True, ws = True, t = True)
        wPos = om.MVector(wRaw[0], wRaw[1], wRaw[2])
        
        # Create the control
        poleVector = cmds.circle(n = 'ctrl_PV_' + extremity, nr = (0,0,1))[0]
        pvGroup = cmds.group(poleVector, n = str(poleVector) + '_grp')
        
        #Calculate the elbow spot and position it behind
        midpoint = (wPos + sPos)/2
        
        #Calculate the Pv Direction
        pvOrigin = ePos - midpoint
        
        pvRaw = pvOrigin * 2
        
        pvPos = pvRaw + midpoint
        
        cmds.move(pvPos.x, pvPos.y, pvPos.z, pvGroup)
        
        # Create PV Constraint
        cmds.poleVectorConstraint(poleVector, ikH)
        
        return ikGroup, pvGroup, ikH, ikControl, poleVector

    ## Creating the FK Arm Controls ##
    def fkSystem(self, startJoint):
        #Creating needed variables for naming and parenting controls in a hierarchy
        cmds.select(startJoint, hi = True)
        fkJoints = cmds.ls(sl = True)
        fkControls = []
        
        
        for f in fkJoints:
            if fkJoints.index(f) != len(fkJoints)-1:
                #Querying joint transforms for control placement.
                currentPos = cmds.xform(f, q = True, ws = True, t = True)
                currentRot = cmds.xform(f, q = True, ws = True, ro = True)
                #Splitting joint names for control naming.
                name = f.split('_')
                #Control creation.
                fkControls.append(cmds.circle(n = 'ctrl_' + name[1] + '_' + name[2] + '_' + name[3], nr = (1,0,0))[0])
                currentGroup = cmds.group(fkControls[fkJoints.index(f)], n = str(fkControls[fkJoints.index(f)]) + '_grp')
                cmds.xform(currentGroup, t = currentPos, ws = True)
                cmds.xform(currentGroup, ro = currentRot, ws = True)
                #If statement: So if theres a previously created fk control, the new one gets parented under it.
                if fkJoints.index(f) >= 1:
                    cmds.parent(currentGroup, fkControls[fkJoints.index(f)-1])
                #Constraining control to joint    
                cmds.parentConstraint(fkControls[fkJoints.index(f)], f, mo = True)
                del name
                cmds.select(d=True)
        return fkControls

    def ikFkBlend(self, target, iksource, fksource, ext):
        
        # Binding both chains to target chain and creating blend control.
        tgJoints = target
        
        # Creating an IK FK blend control
        switchControl = cmds.circle(n = 'ctrl_' + str(ext) + '_IkFk_Switch', nr = (0,1,0))
        switchGroup = cmds.group(switchControl, n = switchControl[0] + '_grp')
        offset = cmds.xform(iksource[2], q = True, ws = True, t = True)
        cmds.move(offset[0], offset[1], offset[2]-2.5, switchGroup)
        cmds.parentConstraint(target[2], switchGroup, mo = True)
        
        #Creating the IK FK Blend Attribute
        cmds.addAttr(switchControl, ln = 'ikFk_Switch', at = 'float', k = True, min = 0, max = 1)
        
        nodes = []
        #Creating blend colors nodes and connecting the ik and fk chains to the target chain
        for t in tgJoints:
            nodeName = t.split('_')
            currentNode = cmds.shadingNode('blendColors', n = nodeName[2] + 'Blend_bc', au = True)
            nodes.append(currentNode)
            cmds.connectAttr(str(switchControl[0]) + '.ikFk_Switch', str(currentNode) + '.blender')
            cmds.connectAttr(iksource[tgJoints.index(t)] + '.rotate', currentNode + '.color1')            
            cmds.connectAttr(fksource[tgJoints.index(t)] + '.rotate', currentNode + '.color2')
            cmds.connectAttr(currentNode + '.output', t + '.rotate')

        return nodes




    def stretchNodes(self, prefix, startJnt, midJnt, endJnt, ikControl, target, side):
     
        ##Add the stretch attribute to the ikControl##
        cmds.addAttr(str(ikControl), sn = 'stretch', at = 'float', dv = 0, min = 0, max = 1, k = True )
       
        ##Creating the nodes and distance tool needed for the stretch##
        distance  = cmds.listRelatives(cmds.distanceDimension(sp = (-1,0,0), ep = (1,0,0)), p = True)[0]
        distConn = cmds.listConnections(cmds.listRelatives(distance, c = True ), scn = True)
        startLocator = cmds.rename(distConn[0], prefix + '_' + side + '_distanceLocator1')
        endLocator = cmds.rename(distConn[1], prefix + '_' + side + '_distanceLocator2')
        distanceDim = cmds.rename(distance, prefix + '_' + side + '_currentLength')
        cmds.pointConstraint(startJnt, startLocator)
        cmds.pointConstraint(ikControl, endLocator)
        mdDistanceDiff = cmds.shadingNode('multiplyDivide', au = True, n = prefix + '_' + side + '_distanceDiff_MD')
        mdScaleOffset = cmds.shadingNode('multiplyDivide', au = True, n = prefix + '_' + side + '_scaleOffset_MD')
        mdDistance = cmds.shadingNode('multiplyDivide', au = True, n = prefix + '_' + side + '_distance_MD')
        pmaDistanceDiff = cmds.shadingNode('plusMinusAverage', au = True, n = prefix + '_' + side + '_distanceDiff_PMA')
        pmaWristTX = cmds.shadingNode('plusMinusAverage', au = True, n = prefix + '_' + side + '_wrist_TX_PMA')
        pmaElbowTX = cmds.shadingNode('plusMinusAverage', au = True, n = prefix + '_' + side + '_elbow_TX_PMA')
        pmaTotalArmLength = cmds.shadingNode('plusMinusAverage', au = True, n = prefix + '_' + side + '_totalArmLength_PMA')
        cndStretch = cmds.shadingNode('condition', au = True, n = prefix + '_' + side + '_stretch_CND')
       
        ##Setting Attributes for Nodes##
        foreArmLength = cmds.getAttr(endJnt + '.translateX')
        bicepLength = cmds.getAttr(midJnt + '.translateX')
        cmds.setAttr(pmaTotalArmLength + '.input3D[0].input3Dx', bicepLength)
        cmds.setAttr(pmaTotalArmLength + '.input3D[1].input3Dx', foreArmLength)
        cmds.setAttr(mdScaleOffset + '.operation', 2)      
        cmds.setAttr(cndStretch + '.colorIfFalseG', foreArmLength)
        cmds.setAttr(cndStretch + '.colorIfFalseR', bicepLength)
        cmds.setAttr(pmaDistanceDiff + '.operation', 2)
        cmds.setAttr(mdDistanceDiff + '.operation', 2)        
        cmds.setAttr(mdDistanceDiff + '.input2X', 2)
        cmds.setAttr(pmaWristTX + '.input3D[2].input3Dx', foreArmLength)
        cmds.setAttr(pmaElbowTX + '.input3D[2].input3Dx', bicepLength)
       
        ##This determines the type of operation depending on the side it is for##
        if side == 'LA' or side == 'LL':
            cmds.setAttr(cndStretch + '.operation', 3)
        elif side == 'RA' or side == 'RL':
            cmds.setAttr(cndStretch + '.operation', 5)
           
        ##NodeConnections##
        cmds.connectAttr(distanceDim + 'Shape.distance', mdScaleOffset + '.input1X')
        cmds.connectAttr(ikControl + '.stretch', mdDistance + '.input2X')
        cmds.connectAttr(mdDistance + '.outputX', cndStretch + '.firstTerm')
        cmds.connectAttr(pmaTotalArmLength + '.output3Dx', cndStretch + '.secondTerm')
        cmds.connectAttr(pmaDistanceDiff + '.output3Dx', mdDistanceDiff + '.input1X')
        cmds.connectAttr(mdDistanceDiff + '.outputX', pmaWristTX + '.input3D[1].input3Dx')
        cmds.connectAttr(mdDistanceDiff + '.outputX', pmaElbowTX + '.input3D[1].input3Dx')
        cmds.connectAttr(pmaElbowTX + '.output3Dx', cndStretch + '.colorIfTrueR')
        cmds.connectAttr(pmaWristTX + '.output3Dx', cndStretch + '.colorIfTrueG')
        cmds.connectAttr(cndStretch + '.firstTerm', pmaDistanceDiff + '.input3D[0].input3Dx')
        cmds.connectAttr(cndStretch + '.secondTerm', pmaDistanceDiff + '.input3D[1].input3Dx')
        cmds.connectAttr(cndStretch + '.outColorR', midJnt + '.translateX')
        cmds.connectAttr(cndStretch + '.outColorG', endJnt + '.translateX')
        if side == 'LA' or side == 'LL':
            cmds.connectAttr(mdScaleOffset + '.outputX', mdDistance + '.input1X')
       
        ##value inversion for right side##
        if side == 'RA' or side == 'RL':
            mdDistanceInv = cmds.shadingNode('multiplyDivide', au = True, n = prefix + '_' + side + '_distance_Invert_MD')
            cmds.setAttr(mdDistanceInv + '.input2X', -1)
            cmds.connectAttr(mdScaleOffset + '.outputX', mdDistanceInv + '.input1X')
            cmds.connectAttr(mdDistanceInv + '.outputX', mdDistance + '.input1X')

        cmds.connectAttr(midJnt + '.translateX', target[1] + '.translateX')
        cmds.connectAttr(endJnt + '.translateX', target[2] + '.translateX')

