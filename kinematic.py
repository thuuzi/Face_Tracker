import numpy as np
import cv2
import math as m

class calcKinematic(object):

    def __init__(self,p1=np.array([0,0,0]),theta1=0,p2=np.array([0,0,0]),theta2=0,p3=np.array([0,0,0])):
        #初始化坐标系的原点位置和转角
        self.p1=p1
        self.theta1=theta1
        self.p2=p2
        self.theta2=theta2
        self.p3=p3

        #初始化相机参数
        #self.K=np.loadtxt()
        self.K=None
        self.alpha=None
        self.r_face=18.0

    def _get_rotation_theta1(self):
        #计算绕z旋转theta1的旋转矩阵
        return np.array([[m.cos(theta1),-m.sin(theta1),0.0],[m.sin(theta1),m.cos(theta1),0.0],[0.0,0.0,1.0]])

    def _get_rotation_theta2(self):
        #计算绕z旋转theta2的旋转矩阵
        return np.array([[m.cos(theta2),-m.sin(theta2),0.0],[m.sin(theta2),m.cos(theta2),0.0],[0.0,0.0,1.0]])

    def _get_rotation_camera(self):
        #计算相机相对2坐标系的旋转矩阵
        return np.array([[0.0,1.0,0.0],[0.0,0.0,1.0],[1.0,0.0,0.0]])

    def _camera_transform(self,img_v,w,h):
        #计算人脸在相机坐标系内的位置
        #img_v为图像坐标，最后一个分量为1
        #估算深度Z
        r_img=0.5*np.sqrt(w**2+h**2)
        Z=(self.alpha*self.r_face)/r_img

        #计算人脸位置
        #P=Z*np.matmul(np.linalg.inv(self.K),np.reshape(img_v,(3,1)))
        P=Z*np.matmul(np.linalg.inv(self.K),img_v)
        return P

    def calcFacePosition(self,cx,cy,w,h):
        #计算人脸相对电机位置
        #单位：mm
        face_position_img=np.array([cx,cy,1.0])
        face_position_camera=self._camera_transform(face_position_img,w,h)
        face_position_axis2=np.matmul(self._get_rotation_camera(),face_position_camera)+self.p3
        face_position_axis1=np.matmul(self._get_rotation_theta2(),face_position_axis2)+self.p2
        face_position_axis0=np.matmul(self._get_rotation_theta1(),face_position_axis1)+self.p1

        return face_position_axis0[0]

if __name__=="__main__":
    calcKinematic()












