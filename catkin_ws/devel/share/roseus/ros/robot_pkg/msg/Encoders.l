;; Auto-generated. Do not edit!


(when (boundp 'robot_pkg::Encoders)
  (if (not (find-package "ROBOT_PKG"))
    (make-package "ROBOT_PKG"))
  (shadow 'Encoders (find-package "ROBOT_PKG")))
(unless (find-package "ROBOT_PKG::ENCODERS")
  (make-package "ROBOT_PKG::ENCODERS"))

(in-package "ROS")
;;//! \htmlinclude Encoders.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass robot_pkg::Encoders
  :super ros::object
  :slots (_header _enc_left _enc_right ))

(defmethod robot_pkg::Encoders
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:enc_left __enc_left) 0)
    ((:enc_right __enc_right) 0)
    )
   (send-super :init)
   (setq _header __header)
   (setq _enc_left (round __enc_left))
   (setq _enc_right (round __enc_right))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:enc_left
   (&optional __enc_left)
   (if __enc_left (setq _enc_left __enc_left)) _enc_left)
  (:enc_right
   (&optional __enc_right)
   (if __enc_right (setq _enc_right __enc_right)) _enc_right)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; uint32 _enc_left
    4
    ;; uint32 _enc_right
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; uint32 _enc_left
       (write-long _enc_left s)
     ;; uint32 _enc_right
       (write-long _enc_right s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; uint32 _enc_left
     (setq _enc_left (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; uint32 _enc_right
     (setq _enc_right (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get robot_pkg::Encoders :md5sum-) "0fa5222877dbcfb0e51225cee374cf9a")
(setf (get robot_pkg::Encoders :datatype-) "robot_pkg/Encoders")
(setf (get robot_pkg::Encoders :definition-)
      "std_msgs/Header header

uint32 enc_left
uint32 enc_right

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

")



(provide :robot_pkg/Encoders "0fa5222877dbcfb0e51225cee374cf9a")


