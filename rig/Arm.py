import maya.cmds as cmds
import maya.OpenMaya as om
import system.utils as utils
import system.rig_utils as rig
import os
import json

classname = 'rig_arm'

class rig_arm(rig.Rig_Utils):

    def __init__(self):
        self.rig_info = {}
        self.rig_data = {}
        self.layoutPos = {}
        self.layoutOrient = {}
        self.sysPath =  os.environ["RDOJO_DATA"] + '/arm_log.json'
        self.dataPath = os.environ["RDOJO_DATA"] + '/arm_data.json'

    ## Importing parameters such as names and positions ##
    def importData(self, path):
        importData = utils.readJson(self.dataPath) 
        self.rig_data = json.loads(importData)
        print 'Parameters Imported'

    def ui(self, name, *args):
            self.stretchArmBox = cmds.checkBox( 'stretch'+ name +'Box', label = "Stretch")
            self.twistArmBox = cmds.checkBox( 'twist'+ name +'Box', label = "Twist Joints")
            testBox = cmds.checkBox( 'test'+ name +'Box', label = "Test Joints")
            return(self.stretchArmBox, self.twistArmBox)
    ## Executing the required functions for building the arm ##
    def rig_arm(self, stretch):
        self.stretch = stretch
        
        cmds.select(d = True)

        self.importData(self.dataPath)
        ## Build Left Arm ##
        self.getCoords('armLy', 'L')

        self.getOrients('armLy', 'L')
        
        self.rig_info['ikJnts_L'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][0], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][0])
        
        self.rig_info['fkJnts_L'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][1], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][0])
        
        self.rig_info['rigJnts_L'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][2], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][0])
           
        self.rig_info['ikArm_L'] = self.ikSystemCreation(self.rig_info['ikJnts_L'][0], self.rig_info['ikJnts_L'][1], self.rig_info['ikJnts_L'][2], self.rig_data['ext'][0])
        
        self.rig_info['fkCtrls_L'] = self.fkSystem(self.rig_info['fkJnts_L'][0])
        
        self.rig_info['nodes_L'] = self.ikFkBlend(self.rig_info['rigJnts_L'], self.rig_info['ikJnts_L'], self.rig_info['fkJnts_L'], self.rig_data['ext'][0])

        self.cleanUpLeft()

        utils.colOverride(self.rig_data['ext'][0], (self.rig_info['ikArm_L'][3], self.rig_info['ikArm_L'][4], self.rig_info['fkCtrls_L']))
        

        if self.stretch == 1:
            self.rig_info['stretchNodes_L'] = self.stretchNodes(self.rig_data['prefix'][0], self.rig_info['ikJnts_L'][0], self.rig_info['ikJnts_L'][1], self.rig_info['ikJnts_L'][2], self.rig_info['ikArm_L'][3], self.rig_info['rigJnts_L'], self.rig_data['ext'][0])


        ## Build Right Arm ##
        self.getCoords('armLy', 'R')

        self.getOrients('armLy', 'R')
        
        self.rig_info['ikJnts_R'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][0], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][2])
        
        self.rig_info['fkJnts_R'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][1], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][2])
        
        self.rig_info['rigJnts_R'] = self.jointCreation(self.rig_data['prefix'][0], self.rig_data['type'][2], self.rig_data['bones'], self.layoutPos, self.layoutOrient, self.rig_data['ext'][2])
           
        self.rig_info['ikArm_R'] = self.ikSystemCreation(self.rig_info['ikJnts_R'][0], self.rig_info['ikJnts_R'][1], self.rig_info['ikJnts_R'][2], self.rig_data['ext'][2])
        
        self.rig_info['fkCtrls_R'] = self.fkSystem(self.rig_info['fkJnts_R'][0])
        
        self.rig_info['nodes_R'] = self.ikFkBlend(self.rig_info['rigJnts_R'], self.rig_info['ikJnts_R'], self.rig_info['fkJnts_R'], self.rig_data['ext'][2])

        self.cleanUpRight()

        utils.colOverride(self.rig_data['ext'][2], (self.rig_info['ikArm_R'][3], self.rig_info['ikArm_R'][4], self.rig_info['fkCtrls_R']))
        
        if self.stretch == 1:   
            self.rig_info['stretchNodes_R'] = self.stretchNodes(self.rig_data['prefix'][0], self.rig_info['ikJnts_R'][0], self.rig_info['ikJnts_R'][1], self.rig_info['ikJnts_R'][2], self.rig_info['ikArm_R'][3], self.rig_info['rigJnts_R'], self.rig_data['ext'][2])

        utils.writeJson(self.sysPath, self.rig_info)


    def cleanUpLeft(self, *args):
        #Cleaning up the Outliner and Scene
        ikCGroup = cmds.group(self.rig_info['ikArm_L'][0], self.rig_info['ikArm_L'][1], n = 'ikControls_LA_grp')
        jntsGrp = cmds.group(self.rig_info['ikJnts_L'][0], self.rig_info['fkJnts_L'][0], self.rig_info['rigJnts_L'][0], n = 'joints_LA_grp')
        ikHGroup = cmds.group(self.rig_info['ikArm_L'][2], n = 'nodes_grp')
        cmds.group(ikCGroup, jntsGrp, ikHGroup, 'ctrl_LA_FK_shoulder_grp', 'ctrl_LA_IkFk_Switch_grp', n = 'L_arm_grp')
        cmds.select(d=True)
        cmds.setAttr(str(self.rig_info['ikJnts_L'][0]) +'.visibility', 0)
        cmds.setAttr(str(self.rig_info['fkJnts_L'][0]) + '.visibility', 0)

        #Control Visibility
        cmds.setDrivenKeyframe('ctrl_LA_FK_shoulder_grp.visibility', cd = 'ctrl_LA_IkFk_Switch.ikFk_Switch', dv = 0, v = 1 )
        cmds.setDrivenKeyframe('ctrl_LA_FK_shoulder_grp.visibility', cd = 'ctrl_LA_IkFk_Switch.ikFk_Switch',  dv = 1, v = 0 )
        cmds.setDrivenKeyframe(ikCGroup + '.visibility', cd = 'ctrl_LA_IkFk_Switch.ikFk_Switch',  dv = 1, v = 1 )
        cmds.setDrivenKeyframe(ikCGroup + '.visibility', cd = 'ctrl_LA_IkFk_Switch.ikFk_Switch',  dv = 0, v = 0 )

    def cleanUpRight(self, *args):
        #Cleaning up the Outliner and Scene
        ikCGroup = cmds.group(self.rig_info['ikArm_R'][0], self.rig_info['ikArm_R'][1], n = 'ikControls_RA_grp')
        jntsGrp = cmds.group(self.rig_info['ikJnts_R'][0], self.rig_info['fkJnts_R'][0], self.rig_info['rigJnts_R'][0], n = 'joints_RA_grp')
        ikHGroup = cmds.group(self.rig_info['ikArm_R'][2], n = 'nodes_grp')
        cmds.group(ikCGroup, jntsGrp, ikHGroup, 'ctrl_RA_FK_shoulder_grp', 'ctrl_RA_IkFk_Switch_grp', n = 'R_arm_grp')
        cmds.select(d=True)
        cmds.setAttr(str(self.rig_info['ikJnts_R'][0]) +'.visibility', 0)
        cmds.setAttr(str(self.rig_info['fkJnts_R'][0]) + '.visibility', 0)

        #Control Visibility
        cmds.setDrivenKeyframe('ctrl_RA_FK_shoulder_grp.visibility', cd = 'ctrl_RA_IkFk_Switch.ikFk_Switch', dv = 0, v = 1 )
        cmds.setDrivenKeyframe('ctrl_RA_FK_shoulder_grp.visibility', cd = 'ctrl_RA_IkFk_Switch.ikFk_Switch',  dv = 1, v = 0 )
        cmds.setDrivenKeyframe(ikCGroup + '.visibility', cd = 'ctrl_RA_IkFk_Switch.ikFk_Switch',  dv = 1, v = 1 )
        cmds.setDrivenKeyframe(ikCGroup + '.visibility', cd = 'ctrl_RA_IkFk_Switch.ikFk_Switch',  dv = 0, v = 0 )
