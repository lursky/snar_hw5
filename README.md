# Отчёт по домашнему заданию №5
Выполнили студенты группы КРБО-02-20:
Ухорский И.О.
Котляров Д.Р.

## Создание пакета
С помощью команды `catkin_create_package` создаём пакет под названием `robot_pkg`  по пути `~/catkin_ws/src`

После этого через терминал, войдя в папку `/catkin_ws` пишем команду `catkin_make` для того чтобы собрать проект. Через некоторое время получим следующую картину в папке `/catkin_ws` :

![project folder](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(1).png "Project Folder")

Далее, открываем в терминале папку `src` и пишем команду `catkin_create_package robot_pkg rospy geometry_msgs nav_msgs std_msgs` 
для того, чтобы создать пакет по требованию задания. Данная команда создаёт пакет `robot_pkg` с зависимостями от пакетов `rospy`, `geometry_msgs`, `nav_msgs` и `std_msgs`. 

-  `rospy` необходим чтобы можно было писать код на языке python
-  `geometry_msgs` для отправки сообщений с уставочными значениями по линейной и угловой скорости
- `nav_msgs` содержит сообщения типа `Odometry`
- `std_msgs` содержит сообщения типа `Header`.

Теперь в папке `/src` появился пакет `robot_pkg`, который, в свою очередь содержит ещё некоторые папки и файлы:

![pkg folder](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(2).png "Package Folder")

Снова соберём проект командой `catkin_make` открыв папку `catkin_ws` в терминале. Пересборка необходима для того, чтобы в файлах `package.xml` и `CMakeLists.txt` появились зависимости от вышеупомянутых пакетов. 

После этого `package.xml` имеет следующий вид:
```xml
<?xml version="1.0"?>
<package format="2">
  <name>robot_pkg</name>
  <version>0.0.1</version>
  <description>The robot_pkg package</description>

  <maintainer email="penekari@gmail.com">uhor</maintainer>
  <!--<license>TODO</license>-->
  <!--<url type="website">http://wiki.ros.org/robot_pkg</url>-->
  <!--<author email="jane.doe@example.com">Jane Doe</author>-->

  <buildtool_depend>catkin</buildtool_depend>
  
  <build_depend>geometry_msgs</build_depend>
  <build_depend>nav_msgs</build_depend>
  <build_depend>rospy</build_depend>
  <build_depend>std_msgs</build_depend>
  
  <build_export_depend>geometry_msgs</build_export_depend>
  <build_export_depend>nav_msgs</build_export_depend>
  <build_export_depend>rospy</build_export_depend>
  <build_export_depend>std_msgs</build_export_depend>
  
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>nav_msgs</exec_depend>
  <exec_depend>rospy</exec_depend>
  <exec_depend>std_msgs</exec_depend>

  <export>

  </export>
</package>
```

## Пользовательские сообщения

По заданию необходимо публиковать показания энкодеров в пользовательском формате сообщений.

Для того чтобы создавать пользовательские сообщения, необходимо создать в папке пакета папку `/msg`, внутри которой будут содержаться файлы `.msg` с форматами собщений. К сожалению, просто создавать такие файлы недостаточно для правильной работы пакета, так как нужно добавить ещё пару зависимостей в файл `package.xml`, а именно:

`<build_depend>message_generation</build_depend>`

и

`<exec_depend>message_runtime</exec_depend>`

далее, в файле `CMakeLists.txt` также необходимо сделать несколько изменений:
Привести следующие функцию в такому виду:

```cmake
find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  nav_msgs
  rospy
  std_msgs
  message_generation
)
```

```cmake
catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES robot_pkg
  CATKIN_DEPENDS geometry_msgs nav_msgs rospy std_msgs message_runtime
#  DEPENDS system_lib
)
```

А также добавить файл пользовательских сообщений (у нас он называется `Encoders.msg`)

```cmake
add_message_files(
  FILES
  Encoders.msg
)

```

Наши пользовательские сообщения имеют следующий вид:
```
std_msgs/Header header

uint32 enc_left
uint32 enc_right
```

Позднее, в `header` мы будем отправлять временную метку `stamp` формата `time` с помощью функции `rospy.Time.now()`, в `enc_left` и `enc_right` полученные показания энкодеров.

## Создание узла

Итак, теперь можно начинать создание узла. Для этого в нашем пакете `robot_pkg` создадим папку `/scripts`, в которой будут храниться исполняемые `.py` файлы. В ней создадим файл `control.py` и сделаем его исполняемым с помощью команды `chmod +x control.py`. Теперь можно открыть его в нашем любимом редакторе Visual Studio Code.
Первой строчкой всегда должна быть строчка

```python
#!/usr/bin/env python3
```

так как с её помощью мы указываем, в какой среде будет выполняться код (в данном случае в среде `python3`, так как у нас стоит ROS Noetic)

Дальше нужно импортировать необходимые библиотеки:
```python
import rospy
from geometry_msgs.msg import Twist
from robot_pkg.msg import Encoders
from nav_msgs.msg import Odometry
from math import sin, cos, pi
```

- `rospy` используется для написания кода ROS на языке Python
- `Twist` нужен для подписки узла на сообщения от органа управления (мы используем `turtlebot3_teleop_key`)
- `Encoders` нужен для публикации наших пользовательских сообщений, содержащих временную метку и показания энкодеров
- `Odometry` нужен для публикации положения робота в пространстве, а также обозначения имени фрейма робота, относительно которого будет происходить движение
- `sin, cos, pi` мы импортируем для упрощения математических вычислений

### Инициализация

Теперь напишем главную функцию, в которой и будет задаваться имя узла, а также декларируем константы, начальные значения, публикаторов (извините за дурацкое слово, просто "издатель" как-то странно звучит) и подписчиков.
```python
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
encr_prev = 0 # initial right encoder data
encl_prev = 0 # initial right encoder data

# Pubs&Subs
odom_pub = rospy.Publisher("odom", Odometry, queue_size=10)
enc_pub = rospy.Publisher("encoders", Encoders, queue_size=10)
ctrl_sub = rospy.Subscriber("/cmd_vel", Twist, callback=pose_callback)

rospy.loginfo("robot_sim node has started!")

rospy.spin()
```

Здесь 
- под `# Constants`
```python
# Constants
L = 0.287 # length between the wheels
r = 0.033 # radius of wheels
N = 4096 # encoders resolution
T = 1.0 # time constant
```
понимаются константы, данные по заданию.

- под `# Time`
```python
# Time
t_prev = rospy.Time.now() # initial time
```
понимается время начала отслеживания за движением робота

- под `# Position`, `# Orientation` и `# Encoders`
```python
# Position
x_prev = 0.0 # initial x coordinate of the robot
y_prev = 0.0 # initial y coordinate of the robot

# Orientation
wr_prev = 0.0 # initial right wheel angular velocity
wl_prev = 0.0 # initial left wheel angular velocity
Th_prev = 0.0 # initial robot angular velocity

# Encoders
encr_prev = 0 # initial right encoder data
encl_prev = 0 # initial right encoder data
```
понимаются, соответсвенно, начальные значения координат позиции робота, ориентации робота и показаний энкодеров.

- под `# Pubs&Subs`
```python
# Pubs&Subs
odom_pub = rospy.Publisher("odom", Odometry, queue_size=10)
enc_pub = rospy.Publisher("encoders", Encoders, queue_size=10)
ctrl_sub = rospy.Subscriber("/cmd_vel", Twist, callback=pose_callback)
```
обозначаются два публикатора и подписчик 
- публикатор одометрии и публикатор показаний энкодеров. В них задаются имя топика, тип сообщений который они передают, а также размер очереди для эжидания публикации при большом потоке сообщений, когда сеть не справляется. `odom_pub` публикует сообщение типа `nav_msgs/Odometry`, в которых содержится множетсво данных, но нас интересуют только позиция по x и y. `enc_pub` публикует пользовательское сообщение типа `robot_pkg/Encoders`, которые состоят из заголовка `std_msgs/Header` а также двух `uint32` значений для показаний энкодеров. В заголовке нас интересует только значение `stamp` содержащее метку времени.
- подписчик на сообщения `/cmd_vel` от `turtlebot3_teleop_key` типа `geometry_msgs/Twist` в которых он получает данные об уставке по линейной и угловой скорости робота. Через него вызывается callback функция `pose_callback`, которой перейдём чуть позже

- последние 2 строчки
```python
rospy.loginfo("robot_sim node has started!")

rospy.spin()
```
говорят узлу выдать сообщение об успешном запуске, а также быть запущеным и "крутиться", пока работает узел  `turtlebot3_teleop_key`. Это возможно благодаря тому, что в нашем узле `robot_sim` есть подписчик на `turtlebot3_teleop_key`.

### Приём, обработка и публикация

Теперь перейдём к callback-функции `pose_callback`. 
```python
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

# calculating dt
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
```

Пойдём по порядку.
Итак в этих строчках
```python
def pose_callback(twist: Twist):
odom = Odometry()
enc = Encoders()
```

мы принимаем сообщение от `turtlebot3_teleop_key` типа `geometry_msgs/Twist`, а также создаём новые сообщения `odom` типа `nav_msgs/Odometry` и `enc` типа `robot_pkg/Encoders`.

Далее
```python
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
```
Мы обозначаем все начальные значения, указанные ранее как глобальные, чтобы их можно было изменить внутри функции.

Далее, мы читаем сообщение `twist`, получая данные о линейной скорости по оси `x` и угловую скорость по оси `z` и считаем уставочные значения скорости вращения колёс робота через функцию `angvel_target()`
```python
# reading cmd_vel
wr_target = angvel_target(twist.linear.x, twist.angular.z, side="left")
wl_target = angvel_target(twist.linear.x, twist.angular.z, side="right")
```

Функция `angvel_target()`
```python
def angvel_target(V_target, Om_target, side):
	if Om_target > 0.0 or Om_target < 0:
		if side == "left": return (V_target/Om_target - L/2)*Om_target/r
		elif side == "right": return (V_target/Om_target + L/2)*Om_target/r
	else: return V_target/r
```
здесь, `V_target` - уставочное значение линейной скорости робота, `Om_target` - уставочное значение угловой скорости робота относительно мгновенного центра скоростей (МЦС).

Вернёмся к `pose_callback()`
```python
# calculating dt
t = rospy.Time.now()
dt = rospy.Time.to_sec(t - t_prev)
t_prev = t
```
здесь мы в переменную `t` получаем нового значения времени, затем находим в секундах разницу между текущим и предыдущим значением времени для последующего численного интегрирования и заносим новое значения времени вместо старого для применения на следующей итерации.

Далее
```python
# calculating wheels real ang vel
beta = dt/(T+dt)
wr = beta*wr_prev + (1-beta)*wr_target
wl = beta*wl_prev + (1-beta)*wl_target
```
мы вычисляем реальные значения угловых скоростей колёс с помощью формул

![formulas](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(3).png "Formulas")

где 
```
beta = β - сглаживающий коэффициент 
wr, wl, wr_prev, wl_prev = ω[n], ω[n-1] - угловые скорости колеса на текущей и предыдущей итерациях 
соответственно 
wr_target, wl_target = ω_target - расчитанная целевая угловая скорость колеса 
dt = Δt - шаг интегрирования 
T - постоянная времени (в данном случае равна 1.0)
```

Находим реальную линейную скорость и угловую скорость относительно МЦС
```python
# calculating linear vel and ang vel of the robot
V = (r/2)*(wr + wl)
Om = (r/L)*(wr - wl)
```

Находим угол, на который повёрнут робот в данный момент относительно начального положения
```python
# calculating the angle of the robot
Th = Om + Th_prev
Th_prev = Th
```

Вычисляем координаты позиции робота
```python
# calculating the position
x = x_prev + V*cos(Th)
y = y_prev + V*sin(Th)
x_prev = x
y_prev = y
```

Находим показания энкодеров в целочисленном виде
```python
# calculating the encoders
encr = encr_prev + int(wr*dt*N/(2*pi))
encl = encl_prev + int(wl*dt*N/(2*pi))
encr_prev = encr
encl_prev = encl
```

Заносим полученные значения координат, а также название фрейма `frame_id` в сообщение `odom`, а также время и показания энкодеров в сообщение `enc`

Затем публикуем их.
```python
# Publishing
odom.header.frame_id = "odom_frame"
odom.pose.pose.position.x = x
odom.pose.pose.position.y = y
enc.header.stamp = rospy.Time.now()
enc.enc_right = encr
enc.enc_left = encl

odom_pub.publish(odom)
enc_pub.publish(enc)
```

## Демонстрация работы

### Запуск узлов

Чтобы запустить любой узел, необходимо сначала запустить Мастера ROS с помощью команды `roscore`
```
uhor@uhor-VirtualBox:~$ roscore
... logging to /home/uhor/.ros/log/872efe72-f800-11ed-9938-e3c4019ddf45/roslaunch-uhor-VirtualBox-3304.log
Checking log directory for disk usage. This may take a while.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://uhor-VirtualBox:42247/
ros_comm version 1.16.0


SUMMARY
========

PARAMETERS
 * /rosdistro: noetic
 * /rosversion: 1.16.0

NODES

auto-starting new master
process[master]: started with pid [3314]
ROS_MASTER_URI=http://uhor-VirtualBox:11311/

setting /run_id to 872efe72-f800-11ed-9938-e3c4019ddf45
process[rosout-1]: started with pid [3324]
started core service [/rosout]
```

Запускаем узел `robot_sim` и `turtlebot3_teleop_key`
```
uhor@uhor-VirtualBox:~$ rosrun robot_pkg control.py 
[INFO] [1684696090.714235]: robot_sim node has started!
```

```
uhor@uhor-VirtualBox:~$ rosrun turtlebot3_teleop turtlebot3_teleop_key 

Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity (Burger : ~ 0.22, Waffle and Waffle Pi : ~ 0.26)
a/d : increase/decrease angular velocity (Burger : ~ 2.84, Waffle and Waffle Pi : ~ 1.82)

space key, s : force stop

CTRL-C to quit
```
Проверим что узел публикует сообщения через топик `/odom` с помощью команды `rostopic echo /odom`
```
uhor@uhor-VirtualBox:~$ rostopic echo /odom
header: 
  seq: 1
  stamp: 
    secs: 0
    nsecs:         0
  frame_id: "odom_frame"
child_frame_id: ''
pose: 
  pose: 
    position: 
      x: 0.0
      y: 0.0
      z: 0.0
    orientation: 
      x: 0.0
      y: 0.0
      z: 0.0
      w: 0.0
  covariance: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
twist: 
  twist: 
    linear: 
      x: 0.0
      y: 0.0
      z: 0.0
    angular: 
      x: 0.0
      y: 0.0
      z: 0.0
  covariance: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
---
```

Проверим что узел публикует сообщения через топик `/encoders` с помощью команды `rostopic echo /encoders`
```
uhor@uhor-VirtualBox:~$ rostopic echo /encoders
header: 
  seq: 1
  stamp: 
    secs: 1684696443
    nsecs: 845871210
  frame_id: ''
enc_left: 0
enc_right: 0
---
```

Все узлы запустились, а топики передают необходимые сообщения. Посмотрим на получившуюся структуру с помощью команды `rqt_graph`

![graph](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(6).png "Structure of Nodes")

Успех! 

### Запуск симуляции

Для симуляции движения и показа траектории используем RViz.

Запустим RViz с помощью команды `rosrun rviz rviz`
```
uhor@uhor-VirtualBox:~$ rosrun rviz rviz
[ INFO] [1684696874.994314205]: rviz version 1.14.20
[ INFO] [1684696874.994367845]: compiled against Qt version 5.12.8
[ INFO] [1684696874.994384072]: compiled against OGRE version 1.9.0 (Ghadamon)
[ INFO] [1684696875.012076624]: Forcing OpenGl version 0.
[ INFO] [1684696876.676751953]: Stereo is NOT SUPPORTED
[ INFO] [1684696876.676880161]: OpenGL device: SVGA3D; build: RELEASE;  LLVM;
[ INFO] [1684696876.677037712]: OpenGl version: 3,3 (GLSL 3,3) limited to GLSL 1.4 on Mesa system.
```

Открылось следующее окно

![rviz def window](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(8).png "RViz Default Window")

Здесь необходимо во вкладке `Global Options` изменить значение параметра `Fixed Frame` с `map` на указанный ранее в коде `odom_frame`

Также нужно добавить визуализацию типа `Odometry` 

Для этого нужно нажать кнопку `Add` в левом нижнем углу

![add](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(9).png "Where's Add Button")

Затем в появившемся списке выбрать `Odometry` и нажать `OK`

![vis](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(10).png "Where's Odometry")

В параметрах добавленной визуализации нужно выбрать `/odom` в поле `Topic`

![params](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(11).png "Change the Topic")

После всех манипуляций получим следующуюю компановку первоначального окна

![rviz fin window](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(12).png "Configured RViz Window")

Для наглядности мы также поменяли размеры стрелки и увеличили количество отрисованных объектов.

Теперь необходимо открыть окно терминала, где мы ранее запустили `turtlebot3_teleop_key` и начать контролировать робота!

После непродолжительного балования траектория получилась следующая

![trajectory](https://github.com/lursky/snar_hw5/blob/main/img/scr%20(13).png "Final Trajectory!")

Топик `/encoders` после конца движения 

```
uhor@uhor-VirtualBox:~$ rostopic echo /encoders
header: 
  seq: 23
  stamp: 
    secs: 1684698996
    nsecs: 957848072
  frame_id: ''
enc_left: 222298
enc_right: 211430
---
```
Топик `/odom` после конца движения

```
uhor@uhor-VirtualBox:~$ rostopic echo /odom
header: 
  seq: 7222
  stamp: 
    secs: 0
    nsecs:         0
  frame_id: "odom_frame"
child_frame_id: ''
pose: 
  pose: 
    position: 
      x: 1.829900314689471
      y: -0.3124608669187821
      ...
---
```


