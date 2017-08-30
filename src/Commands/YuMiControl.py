#!/usr/bin/env python


import copy
import os
import select
import signal
import socket
import sys
import threading
import traceback

import geometry_msgs.msg
import moveit_commander
import moveit_msgs.msg
import rospy
from std_srvs.srv import Empty

import yumi_moveit_utils as yumi

from Client import Client
from Logger import Logger


class YuMiControl():
    CTRL_Z = 0.3
    DISK_Z = 0.2
    DROP_X = 0.45
    DROP_Y = 0.0
    DROP_Z = 0.2
    def __init__(self, args):
        server_address = "localhost"
        if args["--host"]:
            server_address = args["--host"]
        server_port = 5000
        if args["--port"]:
            server_port = int(args["--host"])
        # Connect to ROS and MoveIt!
        yumi.init_Moveit()

        # Reset YuMi joints to "home" position
        yumi.reset_pose()

        # Connect to the server
        args = {"-v":True, "-l":True}
        self.logger = Logger("YuMiControl Client", args)
        # Create a pipe to communicate to the client process
        self.pipe_in_client, self.pipe_out_dia = os.pipe()
        self.pipe_in_dia, self.pipe_out_client = os.pipe()
        # Create a client object to communicate with the server
        self.client = Client(client_type="yumi",
                             pipe_in=self.pipe_in_client,
                             pipe_out=self.pipe_out_client,
                             port=server_port,
                             host=server_address,
                             logger=self.logger)
        self.client.start()
    
    def run(self):
        """ Main loop of the YuMiControl.
        """
        try:
            while True:
                # Wait for either incomming message from the server (via the client)
                socket_list = [self.pipe_in_dia]

                # Get the list sockets which are readable
                read_sockets, _, _ = select.select(socket_list, [], [])

                for sock in read_sockets:
                    # Incoming message from remote server
                    if sock == self.pipe_in_dia:
                        data = os.read(self.pipe_in_dia, 1024)
                        if not data:
                            raise SystemExit("Disconnected from server")
                        else:
                            self.parse(data)

        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.secure_close()

    def parse(self, data):
        data = data.decode("utf-8")
        if "disconnected" in data:
            raise SystemExit("Disconnected from server")
        else:
            self.logger.log(data)
            data = data.split(";")
            print data
            try:
                if "pick" in data[0]:
                    self.pick_up(data)
                if "point" in data[0]:
                    self.point_at(data)
            except IndexError:
                print "invalid data sent: {}".format(data)


    def secure_close(self):
        self.client.close()
        os.kill(self.client.pid, signal.SIGTERM)
        os.close(self.pipe_out_dia)
        os.close(self.pipe_in_dia)
    
    def pick_up(self, args):
        # Redefine to YuMi's coordinates
        print args
        x = 0.75 - float(args[2])
        y = float(args[1]) - 0.475
        print("Block position:  {0:.4f}, {1:.4f}".format(float(args[1]), float(args[2])))
        print("Target position: {0:.4f}, {1:.4f}".format(x, y))
        arm = yumi.LEFT
        if y < 0:
            arm = yumi.RIGHT
        
        # Move to target, grasp it and drop it in the drop zone
        self.move_to_target(arm, x, y)
        self.move_and_drop(arm)
        yumi.reset_arm(arm)
        yumi.reset_pose()

    def move_to_target(self, arm, x, y):
        # Move arm above the target with open grippers
        pose_ee = [x, y, self.CTRL_Z, 0.0, 3.14, 0.0]
        grip_effort = -10.0
        self.move_and_grasp(arm, pose_ee, grip_effort)

        # Move arm down to the target with open grippers
        pose_ee = [x, y, self.DISK_Z, 0.0, 3.14, 0.0]
        self.move_and_grasp(arm, pose_ee, grip_effort)

        # Grip target
        grip_effort = 10.0
        self.move_and_grasp(arm, pose_ee, grip_effort)

        # Move back up
        pose_ee = [x, y, self.CTRL_Z, 0.0, 3.14, 0.0]

        
    
    def move_and_drop(self, arm):
        # Move to drop zone
        pose_ee = [self.DROP_X, self.DROP_Y, self.CTRL_Z, 0.0, 3.14, 0.0]
        grip_effort = 10.0
        self.move_and_grasp(arm, pose_ee, grip_effort)

        # Release into drop zone
        pose_ee = [self.DROP_X, self.DROP_Y, self.DROP_Z, 0.0, 3.14, 0.0]
        grip_effort = -10.0
        self.move_and_grasp(arm, pose_ee, grip_effort)

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
