# Face_Tracker
face recognition and face tracking on RaspberryPi 4B

要开始人脸追踪的功能，只需要在树莓派的终端执行如下命令：

```
$  cd face_tracker
$  python3 function_start.py
```

等待几秒之后，该功能自动开启，对周围环境中的人脸进行识别，并对识别到的人脸进行追踪。



调试注意：

1. 如果要对舵机进行归中操作，可在终端执行如下命令：

```
$ cd servo_test
$ python3 PWMServo.py
```

2. 要调节摄像头的焦距使画面更清晰，在终端执行如下命令：

```
$ cd py_ws
$ python3 video.py
```

这时如果是在VNC桌面连接下，可以看到几秒后出现一个显示摄像头画面的窗口。根据窗口显示的图片对摄像头进行调节即可。

