#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from robot_pkg.msg import Encoders
from nav_msgs.msg import Odometry

from math import sin, cos, pi


def angvel_target(V_target, Om_target, side):
    if Om_target > 0.0 or Om_target < 0:
        if side == "left": return (V_target/Om_target - L/2)*Om_target/r
        elif side == "right": return (V_target/Om_target + L/2)*Om_target/r
    else: return V_target/r   


def pose_callback(twist: Twist):
    odom = Odometry()
    enc = Encoders()
    
    # Time
    global t_prev 

    # Position
    global x_prev 
    global y_prev 
    
    # Orientation
    global wr_prev 
    global wl_prev 
    global Th_prev

    # Encoders
    global encr_prev 
    global encl_prev 

    # reading cmd_vel
    wr_target = angvel_target(twist.linear.x, twist.angular.z, side="left")
    wl_target = angvel_target(twist.linear.x, twist.angular.z, side="right")
    
    # ============= TIME =============
    t = rospy.Time.now()
    dt = rospy.Time.to_sec(t - t_prev)
    t_prev = t

    # calculating wheels real ang vel
    beta = dt/(T+dt)
    wr = beta*wr_prev + (1-beta)*wr_target
    wl = beta*wl_prev + (1-beta)*wl_target

    # calculating linear vel and ang vel of the robot
    V = (r/2)*(wr + wl)
    Om = (r/L)*(wr - wl)

    # calculating the angle of the robot
    Th = Om + Th_prev
    Th_prev = Th

    # calculating the position
    x = x_prev + V*cos(Th)
    y = y_prev + V*sin(Th)
    #rospy.loginfo(str(x) + ", " + str(y))
    x_prev = x
    y_prev = y

    # calculating the encoders
    encr = encr_prev + int(wr*dt*N/(2*pi))
    encl = encl_prev + int(wl*dt*N/(2*pi))
    encr_prev = encr
    encl_prev = encl

    # Publishing
    odom.header.frame_id = "odom_frame"
    odom.pose.pose.position.x = x
    odom.pose.pose.position.y = y
    enc.header.stamp = rospy.Time.now()
    enc.enc_right = encr
    enc.enc_left = encl

    odom_pub.publish(odom)
    enc_pub.publish(enc)
    rospy.loginfo("pos: (" + str(odom.pose.pose.position.x) + ", " + str(odom.pose.pose.position.y) + ")")
    rospy.loginfo("encoders: (" + str(enc.enc_right) + ", " + str(enc.enc_left) + ")")


if __name__ == '__main__':
    rospy.init_node("robot_sim")

    # Constants
    L = 0.287 # length between the wheels
    r = 0.033 # radius of wheels
    N = 4096 # encoders resolution
    T = 1.0 # time constant

    # Time
    t_prev = rospy.Time.now() # initial time

    # Position
    x_prev = 0.0 # initial x coordinate of the robot
    y_prev = 0.0 # initial y coordinate of the robot
    
    # Orientation
    wr_prev = 0.0 # initial right wheel angular velocity
    wl_prev = 0.0 # initial left wheel angular velocity
    Th_prev = 0.0 # initial robot angular velocity

    # Encoders
    encr_prev = 0
    encl_prev = 0

    # Pubs and Subs
    odom_pub = rospy.Publisher("odom", Odometry, queue_size=10)
    enc_pub = rospy.Publisher("encoders", Encoders, queue_size=10)
    ctrl_sub = rospy.Subscriber("/cmd_vel", Twist, callback=pose_callback)

    rospy.loginfo("robot_sim node has started!")

    rospy.spin()