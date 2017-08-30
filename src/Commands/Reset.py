#!/usr/bin/env python


import sys
import copy
import rospy
import moveit_commander
import yumi_moveit_utils as yumi
import moveit_msgs.msg
import geometry_msgs.msg
from std_srvs.srv import Empty



class Reset():
    def __init__(self, args):
        pass

    def close_grippers(self, arm):
        """Closes the grippers.

        Closes the grippers with an effort of 15 and then relaxes the effort to 0.

        :param arm: The side to be closed (moveit_utils LEFT or RIGHT)
        :type arm: int
        :returns: Nothing
        :rtype: None
        """
        yumi.gripper_effort(arm, 15.0)
        yumi.gripper_effort(arm, 0.0)

    def open_grippers(self, arm):
        """Opens the grippers.

        Opens the grippers with an effort of -15 and then relaxes the effort to 0.

        :param arm: The side to be opened (moveit_utils LEFT or RIGHT)
        :type arm: int
        :returns: Nothing
        :rtype: None
        """
        yumi.gripper_effort(arm, -15.0)
        yumi.gripper_effort(arm, 0.0)



    def move_and_grasp(self, arm, pose_ee, grip_effort):
        try:
            yumi.traverse_path([pose_ee], arm, 10)
        except Exception:
            if (arm == yumi.LEFT):
                yumi.plan_and_move(yumi.group_l, yumi.create_pose_euler(pose_ee[0], pose_ee[1], pose_ee[2], pose_ee[3], pose_ee[4], pose_ee[5]))
            elif (arm == yumi.RIGHT):
                yumi.plan_and_move(yumi.group_r, yumi.create_pose_euler(pose_ee[0], pose_ee[1], pose_ee[2], pose_ee[3], pose_ee[4], pose_ee[5]))

        if (grip_effort <= 20 and grip_effort >= -20):
            yumi.gripper_effort(arm, grip_effort)
        else:
            print("The gripper effort values should be in the range [-20, 20]")




    def run(self):
        """Starts the node

        Runs to start the node and initialize everthing. Runs forever via Spin()

        :returns: Nothing
        :rtype: None
        """

        #Start by connecting to ROS and MoveIt!
        yumi.init_Moveit()


        # Print current joint angles
        yumi.print_current_joint_states(yumi.RIGHT)
        yumi.print_current_joint_states(yumi.LEFT)

        # Reset YuMi joints to "home" position
        yumi.reset_pose()


        pose_ee = [0.25, -0.25, 0.2, 0.0, 3.14, 0.0]
        grip_effort = -10.0
        self.move_and_grasp(yumi.RIGHT, pose_ee, grip_effort)

        # Drive YuMi end effectors to a desired position (pose_ee), and perform a grasping task with a given effort (grip_effort)
        # Gripper effort: opening if negative, closing if positive, static if zero
        pose_ee = [0.25, 0.25, 0.3, 0.0, 3.14, 0.0]
        grip_effort = -10.0
        self.move_and_grasp(yumi.LEFT, pose_ee, grip_effort)

        yumi.reset_pose()
        

        #rospy.spin()