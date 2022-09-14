import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from numpy.lib.utils import source
import cv2
import random
from get_face_parts import get_mask
from Ordinary_Procrustes_Analysis import OPA
from poisson_img_editing import poisson_edit
from img2video import img2video
from get_features import return_features
import dlib
import time
import numpy as np
from color_detect import color_detect
import re
import os
import magic
import pinyin
import qrcode
from PIL import Image
from pyzbar import pyzbar
from create_qr import make_qr_code
from create_qr import make_qr_code_with_icon
from create_qr import decode_qr_code
from requests import get

import smtplib
import email.message
import time
import random

import sqlite3
import cv2

import socket
from requests import get

import platform

from PyQt5.uic.uiparser import QtCore


class send_email(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.email = ''

    def run(self):
        msg = email.message.EmailMessage()

        msg["From"] = '知心好朋友'
        msg["To"] = self.email
        msg["Subject"] = "帳號登入提醒"

        print(self.email)

        ipList = socket.gethostbyname_ex(socket.gethostname())

        self.out = False

        # 寄送郵件主要內容
        # msg.set_content("測試郵件純文字內容") #純文字信件內容
        msg.add_alternative("登入提醒，您目前已在「" + str(platform.system()) + "」上登入勤益去識別化軟體。<br><br><br>IP位址：" + str(get('https://api.ipify.org/').text) + "<br>裝置名稱：" + str(ipList[0]) + "<br><br><br>如果本人未執行相關操作，請盡速聯絡相關單位，電話：xxxxxxxxxx", subtype="html")  # HTML信件內容

        # 連線到SMTP Sevver
        # 可以從網路上找到主機名稱和連線埠
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # 建立gmail連驗
        server.login('3a717039@gm.student.ncut.edu.tw', 'djehnexprhviaohz')
        server.send_message(msg)
        server.close()  # 發送完成後關閉連線

class StartOPA(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ''
        self.source = ''

    def run(self):
        target = cv2.imread(self.target)
        source = cv2.imread(self.source)
        warped_source = OPA(target, source)
        cv2.imwrite('./img/warped.png', warped_source)
        self.callback.emit(0)

class StartGetMask(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ''

    def run(self):
        print(self.target)
        target = cv2.imread(self.target)
        mask = get_mask(target)
        cv2.imwrite('./img/mask.png', mask)
        self.callback.emit(0)

class StartBlend(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ''
        self.flag = True


    def run(self):
        blend.first = False
        while self.flag:
            if os.path.isfile('./img/mask.png') and os.path.isfile('./img/warped.png'):
                self.msleep(100)
                warped_source = cv2.imread('./img/warped.png')
                target = cv2.imread(self.target)
                mask = cv2.imread('./img/mask.png', 0)
                result = poisson_edit(warped_source, target, mask)
                cv2.imwrite('./img/result.png', result)
                self.callback.emit(0)
                os.remove('./img/mask.png')
                os.remove('./img/warped.png')
                break

class Startdetect(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sex = ''
        self.race = ''
        self.img = ''

    def run(self):    
        conn = sqlite3.connect('face_color.db')
        c = conn.cursor()

        color = color_detect(self.img)

        print('color = ' + str(color))
    
        count = 0

        for e in c.execute("SELECT * FROM stocks ORDER BY race"):
            if e[1] == self.race and e[2] == self.sex and e[4] >= color - 15 and e[4] <= color + 15:
                blend.bad.append(e[0])
                count += 1



        if count == 0:
            m = 256
            for e in c.execute("SELECT * FROM stocks ORDER BY race"):
                if e[1] == self.race and e[2] == self.sex:
                    if m > (int(e[4]) - color):
                        m = int(e[4]) - color
                        blend.bad = [e[0]]
                        print(m)

        self.callback.emit(0)




            
            


class ChangeLoadingThread(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.flag = True
        self.count = 0

    def stop(self):
        self.flag = False

    def rerun(self):
        self.flag = True

    def run(self):
        while True:
            if self.flag:
                self.callback.emit(self.count)
                time.sleep(0.05)
                self.count += 1
                if self.count >= 8:
                    self.count = 0

class ChangeBgThread(QThread):
    callback = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.flag = True
        self.pre = ''
        self.now = ''
        self.ratio = 0

    def __del__(self):
        self.flag = False
        self.wait()

    def run(self):
        ratio = 0
        img_pre = cv2.imread(self.pre)
        img_now = cv2.imread(self.now)
        while self.flag:
            self.ratio = ratio

            added_image = cv2.addWeighted(
                img_pre, ratio / 20, img_now, 1 - ratio / 20, 0)
            cv2.imwrite('./changing.png', added_image)
            self.msleep(10)
            ratio += 1
            self.callback.emit(ratio)
            self.msleep(10)
            if ratio >= 21:
                break

class GIFThread(QThread):
    Serial = pyqtSignal(str)
    Serial2 = pyqtSignal(str)
    
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.flag = True
        self.avatar = True
        self.start_flag = True
        self.count = 0

    def stop(self):
        self.flag = False


    def stop_run(self):
        self.start_flag = False

    def running(self):
        self.start_flag = True

    def resume(self):
        self.flag = True
        self.count = 0

    def flagAvatar(self):
        self.avatar = True

    def flagTarget(self):
        self.avatar = False
    
    def run(self):
        while self.start_flag:
            s = time.time()
            if self.flag:
                if self.avatar:
                    self.Serial.emit(str(self.count))
                    if self.count == 50:
                        self.count = 0
                    else:
                        self.count += 1            
                    self.msleep(35)
                else:
                    self.Serial2.emit(str(self.count))
                    if self.count == 77:
                        self.count = 0
                    else:
                        self.count += 1            
                    self.msleep(30)
            else:
                s = time.time()
                pass

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.password.setEchoMode(QLineEdit.Password)
        self.FaceBG.setStyleSheet(
            "border-image : url(pa02.jpg);border-top-left-radius:50px;")
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        
        self.exit.clicked.connect(QCoreApplication.instance().quit)
        self.ForgetPassword.clicked.connect(self.gotoChangePassword)
        self.enter.clicked.connect(self.gotoOperation)

        self.account = ''
        self.pw = ''        
        self.name = ''
        self.id = ''
        self.birthday = ''
        self.email = ''
        self.firstlogin = ''

        self.send = send_email()


    def gotoOperation(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()  


        for e in c.execute("SELECT * FROM stocks WHERE account LIKE '" + str(self.username.text()) + "'"):
            self.account = e[0]
            self.pw = e[1]
            self.name = e[2]
            self.id = e[3]
            self.birthday = e[4]
            self.email = e[5]
            self.firstlogin = e[6]
    

        if self.username.text() == '' or self.password.text() == '':
            self.warning.setText('請輸入帳號或密碼!!')
        elif self.username.text() != self.account or self.password.text() != self.pw:
            self.warning.setText("帳號或密碼錯誤!!")
        elif self.username.text() == self.account and self.password.text() == self.pw: 
            if self.firstlogin == '1':
                widget.setCurrentIndex(widget.currentIndex() + 1)
                operation.GIF.start()
                first_login.back.setVisible(False)
            else:
                try:
                    get('https://api.ipify.org/').text
                except:
                    self.warning.setText("請連接網際網路!!")
                    return

                widget.setCurrentIndex(widget.currentIndex() + 2)
                operation.GIF.start()

                self.send.email = self.email
                self.send.start()
                


        conn.commit()   
        conn.close()



    def gotoChangePassword(self):
        widget.setCurrentIndex(widget.currentIndex() + 7)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            self.gotoOperation()

class InfoScreen(QDialog):
    def __init__(self):
        super(InfoScreen, self).__init__()
        loadUi("info.ui", self)
        self.TopLabel.setStyleSheet(
            'background-image : url(top_background.png);border-radius: 65px;border-bottom-right-radius: 0px;')
        self.background.setStyleSheet(
            'background-image: url(Gradient_builder_2.jpg);border-radius: 65px;'
        )
        self.nextpageBTN.setStyleSheet('QPushButton#nextpageBTN{border-radius : 10px;border-image: url(rarrow.png);}QPushButton#nextpageBTN:hover{border-radius : 10px;border-image: url(brown rarrow.png);}QPushButton#nextpageBTN::pressed{border-radius : 10px;border-image: url(white rarrow.png);}')

        self.backpageBTN.setStyleSheet('QPushButton#backpageBTN{border-radius : 10px;border-image: url(larrow.png);}QPushButton#backpageBTN:hover{border-radius : 10px;border-image: url(brown larrow.png);}QPushButton#backpageBTN::pressed{border-radius : 10px;border-image: url(white larrow.png);}')

        self.TopLeftBG.setStyleSheet('background-image: url(Gradient_builder_small.jpg);')
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")

        self.color = 0


        self.backpageBTN.clicked.connect(self.gotoOperation)
        self.nextpageBTN.clicked.connect(self.gotoChoose)
        self.exit.clicked.connect(QCoreApplication.instance().quit)

    


    def gotoOperation(self):

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE stocks SET email = '"+self.email.text()+"' WHERE account = '"+login.account+"'")
        conn.commit()
        conn.close()

        widget.setCurrentIndex(widget.currentIndex() - 2)
        operation.GIF.running()
        operation.GIF.start()

    def gotoChoose(self):

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE stocks SET email = '"+self.email.text()+"' WHERE account = '"+login.account+"'")
        conn.commit()
        conn.close()
        
        widget.setCurrentIndex(widget.currentIndex() + 1)
        

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

class ChooseScreen(QDialog):
    def __init__(self):
        super(ChooseScreen, self).__init__()
        loadUi("choose.ui", self)
        # self.background.setStyleSheet(
        #     'background-image : url(black male2.png);border-radius: 65px;')
        self.background.setStyleSheet(
            'background-image : url(./black male2.png);border-radius: 65px;')

        
        self.nextpageBTN.setStyleSheet('QPushButton#nextpageBTN{border-radius : 10px;border-image: url(rarrow.png);}QPushButton#nextpageBTN:hover{border-radius : 10px;border-image: url(brown rarrow.png);}QPushButton#nextpageBTN::pressed{border-radius : 10px;border-image: url(white rarrow.png);}')

        self.backpageBTN.setStyleSheet('QPushButton#backpageBTN{border-radius : 10px;border-image: url(larrow.png);}QPushButton#backpageBTN:hover{border-radius : 10px;border-image: url(brown larrow.png);}QPushButton#backpageBTN::pressed{border-radius : 10px;border-image: url(white larrow.png);}')
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")

        self.exit.clicked.connect(QCoreApplication.instance().quit)

        self.nextpageBTN.clicked.connect(self.gotoBlend)
        self.backpageBTN.clicked.connect(self.gotoInfo)

        shadow_boy = QGraphicsDropShadowEffect()
        shadow_girl = QGraphicsDropShadowEffect()
        shadow_black = QGraphicsDropShadowEffect()
        shadow_white = QGraphicsDropShadowEffect()
        shadow_asian = QGraphicsDropShadowEffect()
        shadow_boy.setBlurRadius(40)
        shadow_girl.setBlurRadius(40)
        shadow_black.setBlurRadius(40)
        shadow_white.setBlurRadius(40)
        shadow_asian.setBlurRadius(40)
        self.boy.setGraphicsEffect(shadow_boy)
        self.girl.setGraphicsEffect(shadow_girl)
        self.black.setGraphicsEffect(shadow_black)
        self.white.setGraphicsEffect(shadow_white)
        self.asian.setGraphicsEffect(shadow_asian)



        self.boy.setStyleSheet(
            'QPushButton#boy{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#boy:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255)}')

        self.boy.clicked.connect(lambda: self.buttonClick(self.boy))
        self.girl.clicked.connect(lambda: self.buttonClick(self.girl))
        self.black.clicked.connect(lambda: self.buttonClick(self.black))
        self.white.clicked.connect(lambda: self.buttonClick(self.white))
        self.asian.clicked.connect(lambda: self.buttonClick(self.asian))

        self.sex = '男'
        self.race = '黑人'

        self.pre = './black male2.png'
        self.now = ''

        self.thread = ChangeBgThread()      

    def gotoBlend(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoInfo(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def buttonClick(self, button):
        if button.text() == '男':
            self.boy.setStyleSheet(
                'QPushButton#boy{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#boy:pressed{padding-left:3px;padding-top:3px;color: rgb(255, 255, 255);background-color:rgba(150,123,111,255)}')
            self.girl.setStyleSheet(
                'QPushButton#girl{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#girl:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.sex = '男'
        elif button.text() == '女':
            self.girl.setStyleSheet(
                'QPushButton#girl{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#girl:pressed{padding-left:3px;padding-top:3px;color: rgb(255, 255, 255);background-color:rgba(150,123,111,255)}')
            self.boy.setStyleSheet(
                'QPushButton#boy{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#boy:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.sex = '女'
        elif button.text() == '白人':
            self.white.setStyleSheet(
                'QPushButton#white{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#white:pressed{padding-left:3px;padding-top:3px;color: rgb(255, 255, 255);background-color:rgba(150,123,111,255)}')
            self.black.setStyleSheet(
                'QPushButton#black{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#black:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.asian.setStyleSheet(
                'QPushButton#asian{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#asian:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.race = '白人'
        elif button.text() == '黑人':
            self.black.setStyleSheet(
                'QPushButton#black{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#black:pressed{padding-left:3px;padding-top:3px;color: rgb(255, 255, 255);background-color:rgba(150,123,111,255)}')
            self.white.setStyleSheet(
                'QPushButton#white{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#white:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.asian.setStyleSheet(
                'QPushButton#asian{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#asian:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.race = '黑人'
        elif button.text() == '亞洲人':
            self.asian.setStyleSheet(
                'QPushButton#asian{background-color: rgb(35, 199, 130);color: rgb(255, 255, 255);border-radius:20px;}QPushButton#asian:pressed{padding-left:3px;padding-top:3px;color: rgb(255, 255, 255);background-color:rgba(150,123,111,255)}')
            self.white.setStyleSheet(
                'QPushButton#white{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#white:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.black.setStyleSheet(
                'QPushButton#black{background-color: rgb(255, 255, 255);color: rgb(0, 0, 0);border-radius:20px;}QPushButton#black:pressed{padding-left:3px;padding-top:3px;background-color:rgba(150,123,111,255);color: rgb(255, 255, 255);}')
            self.race = '亞洲人'
        if self.race == '黑人':
            blend.race = '0'
            if self.sex == '男':
                self.now = self.pre
                self.pre = './black male2.png'
                blend.sex = '1'
            else:
                self.now = self.pre
                self.pre = './black female.png'
                blend.sex = '0'
        elif self.race == '白人':
            blend.race = '1'
            if self.sex == '男':
                self.now = self.pre
                self.pre = './white male.png'
                blend.sex = '1'
            else:
                self.now = self.pre
                self.pre = './white female.png'
                blend.sex = '0'
        elif self.race == '亞洲人':
            blend.race = '2'
            if self.sex == '男':
                self.now = self.pre
                self.pre = './asian male.png'
                blend.sex = '1'
            else:
                self.now = self.pre
                self.pre = './asian female2.png'
                blend.sex = '0'
        
        self.thread.pre = self.pre
        self.thread.now = self.now
        self.thread.callback.connect(self.changeBg)
        self.thread.start()
  

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

    def changeBg(self):
        self.background.setStyleSheet(
                'background-image : url(changing.png);border-radius: 65px;')
     
class BlendingScreen(QDialog):
    def __init__(self):
        super(BlendingScreen, self).__init__()
        
        
        loadUi("blend.ui", self)
        self.background.setStyleSheet('border-radius:50px;border-image: url(./face.png);')
        self.uploadBTN.setStyleSheet('QPushButton#uploadBTN{border-radius : 10px;border-image: url(upload.png);}QPushButton#uploadBTN:hover{border-radius : 10px;border-image: url(brown upload.png);}QPushButton#uploadBTN::pressed{border-radius : 10px;border-image: url(white upload.png);}')
        self.refreshBTN.setStyleSheet('QPushButton#refreshBTN{border-radius : 10px;border-image: url(refresh.png);}QPushButton#refreshBTN:hover{border-radius : 10px;border-image: url(brown refresh.png);}QPushButton#refreshBTN::pressed{border-radius : 10px;border-image: url(white refresh.png);}')
        self.saveBTN.setStyleSheet('QPushButton#saveBTN{border-radius : 10px;border-image: url(save.png);}QPushButton#saveBTN:hover{border-radius : 10px;border-image: url(brown save.png);}QPushButton#saveBTN::pressed{border-radius : 10px;border-image: url(white save.png);}')
        self.saveqrBTN.setStyleSheet('QPushButton#saveqrBTN{border-radius : 10px;border-image: url(qr.png);}QPushButton#saveqrBTN:hover{border-radius : 10px;border-image: url(brown qr.png);}QPushButton#saveqrBTN::pressed{border-radius : 10px;border-image: url(white qr.png);}')
        self.backpageBTN.setStyleSheet('QPushButton#backpageBTN{border-radius : 10px;border-image: url(larrow.png);}QPushButton#backpageBTN:hover{border-radius : 10px;border-image: url(brown larrow.png);}QPushButton#backpageBTN::pressed{border-radius : 10px;border-image: url(white larrow.png);}')
        self.homeBTN.setStyleSheet('QPushButton#homeBTN{border-radius : 10px;border-image: url(home.png);}QPushButton#homeBTN:hover{border-radius : 10px;border-image: url(brown home.png);}QPushButton#homeBTN::pressed{border-radius : 10px;border-image: url(white home.png);}')
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        
        self.exit.clicked.connect(QCoreApplication.instance().quit)
        self.homeBTN.clicked.connect(self.gotoOperation)
        self.backpageBTN.clicked.connect(self.gotoChoose)
        self.uploadBTN.clicked.connect(self.uploadImage)
        self.refreshBTN.clicked.connect(self.refresh)
        self.saveBTN.clicked.connect(self.saveimg)
        self.saveqrBTN.clicked.connect(self.saveqr)
        

        self.result = ''

        self.loader = ChangeLoadingThread()
        self.detect = Startdetect()
        self.OPAer = StartOPA()
        self.mask = StartGetMask()
        self.blend = StartBlend()

        self.loader.callback.connect(self.changeloading)
        self.detect.callback.connect(self.colordetect)
        self.OPAer.callback.connect(self.blending)
        self.blend.callback.connect(self.stoploading)

        self.test_count = 0

        self.first = True

        self.target = ''
        self.source = ''

        self.sex = '1'
        self.race = '0'

        self. e = 0

        self.flag = True
        
        self.bad = []



    def saveimg(self):
        try:
            if self.result != '':
                imgName, imgType = QFileDialog.getSaveFileName(
                    self, "儲存圖片", "", "*.png;;*.jpg;;All Files(*)"
                )
                cv2.imwrite(imgName, cv2.imread('./img/fake.png'))
        except:
            pass

    def refresh(self):
        if self.result != '':
            self.security.setText('')
            self.security.setStyleSheet('')
            self.Source()
            self.loader.rerun()

    def Source(self):
        if self.first:
            bad = [11, 16, 22, 69, 34 ,60, 74, 83, 71, 30, 43, 5, 97, 64, 20, 59, 9, 4, 48, 25, 75, 26, 19, 76, 15, 32, 55, 44, 1, 94]
            location = random.randint(0, len(bad)-1)
            self.source = './img/' + self.race + self.sex + '/' + str(bad[location]) + '.jpg'
            print(self.source)
        else:

            self.detect.sex = ''
            self.detect.race = '' 


            
            if self.sex == '0':
                self.detect.sex = 'female'
            else:
                self.detect.sex = 'male'
            
            if self.race == '0':
                self.detect.race = 'black'
            elif self.race == '1':
                self.detect.race = 'white'
            else:
                self.detect.race = 'asian'

            self.detect.start()




    def encrypt(self):
        name = login.name
        name = pinyin.get(name, format='strip', delimiter="")
        name = name.upper()

        birthday = login.birthday

        qr_text = str(magic.encrypt(cv2.imread('./img/result.png'), login.id + name + birthday))
        make_qr_code("make_qr_code", "qrcode.png")

        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec_()

        make_qr_code_with_icon(
            qr_text, "./img/result.png", "./img/qr.png",)



    def saveqr(self):
        try:
            if self.result != '':
                imgName, imgType = QFileDialog.getSaveFileName(
                    self, "儲存圖片", "", "*.png;;*.jpg;;All Files(*)"
                )
                cv2.imwrite(imgName, cv2.imread('./img/qr.png'))
        except:
            pass
    def uploadImage(self):
        self.security.setText('')
        self.security.setStyleSheet('')
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', 'Image', '*.png *.jpg *.bmp')
        if filename is '':
            return
        self.img = cv2.imread(filename, -1)
        self.target = filename
        if self.img.size == 1:
            return
        self.detect.img = self.target        
        detector = dlib.get_frontal_face_detector()
        rects = detector(cv2.imread(self.target), 0)
        if len(rects) > 1:
            print("此照片人數超過一個人，請重新輸入。")            
            self.background.setStyleSheet('border-radius:50px;border-image: url(./noface.png);')
            return
        elif len(rects) < 1:
            print("此照片沒有人，請重新輸入。")
            self.background.setStyleSheet('border-radius:50px;border-image: url(./noface.png);')
            return
        self.loader.start()
        self.loader.rerun()
        self.background.setStyleSheet('border-radius:50px;border-image: url(' + str(filename) + ');')
        self.uploadBTN.setEnabled(False)
        self.refreshBTN.setEnabled(False)
        self.saveBTN.setEnabled(False)
        self.saveqrBTN.setEnabled(False)
        self.backpageBTN.setEnabled(False)
        self.homeBTN.setEnabled(False)
        self.Source()
        if self.first:
            self.OPA()
            self.getmask()
    
    def colordetect(self):
        print(len(self.bad))
        location = random.randint(0, len(self.bad)-1)
        self.source = './img/' + self.race + self.sex + '/' + str(self.bad[location])
        print(self.source)
        self.OPA()
        self.getmask()
        

    def OPA(self):
        self.OPAer.target = self.target
        self.OPAer.source = self.source
        self.OPAer.start()

    def getmask(self):
        self.mask.target = self.target
        self.mask.start()

    def blending(self):
        self.blend.target = self.target
        self.blend.start()

    def stoploading(self):
        self.loader.stop()
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec_()
        self.loading.setStyleSheet('')
        self.background.setStyleSheet('border-radius:50px;border-image: url(./img/result.png);')
        self.result = cv2.imread('./img/result.png')
        self.uploadBTN.setEnabled(True)
        self.refreshBTN.setEnabled(True)
        self.saveBTN.setEnabled(True)
        self.saveqrBTN.setEnabled(True)
        self.backpageBTN.setEnabled(True)
        self.homeBTN.setEnabled(True)

        feature_1 = return_features(cv2.imread(self.target))
        feature_2 = return_features(cv2.imread('./img/fake.png'))
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2) 
        self.e = np.sqrt(np.sum(np.square(feature_1 - feature_2)))

        print(self.e)

        if self.e >= 0.35:
            self.security.setText('安全性：高')
            self.security.setStyleSheet('color: rgb(0, 154, 102);background-color:rgba(0,0,0,100);border-top-right-radius:30px;border-bottom-right-radius:30px;')
        elif self.e >=0.3:
            self.security.setText('安全性：中')
            self.security.setStyleSheet('color: rgb(255, 140, 0);background-color:rgba(0,0,0,100);border-top-right-radius:30px;border-bottom-right-radius:30px;')
        else:
            self.security.setText('安全性：低')
            self.security.setStyleSheet('color: rgb(255, 0, 0);background-color:rgba(0,0,0,100);border-top-right-radius:30px;border-bottom-right-radius:30px;')

        self.encrypt()


    def changeloading(self):
        self.loading.setStyleSheet('border-image: url(./img/icon/loading' + str(self.loader.count) + '.png);')


    def gotoOperation(self):
        widget.setCurrentIndex(widget.currentIndex() - 4)
        operation.GIF.running()
        operation.GIF.start()

    def gotoChoose(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

class OperationScreen(QDialog):
    def __init__(self):
        super(OperationScreen, self).__init__()
        loadUi("operation.ui", self)
        self.FaceBG.setStyleSheet(
            "border-image : url(pa02.jpg);border-top-left-radius:50px;")
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        self.blend.setStyleSheet('border-image: url(./avatar/0.png);')
        self.authentication.setStyleSheet('border-image: url(./img/verification/0.png);')

        self.GIF = GIFThread()

        self.blend.setObjectName('blend')
        self.authentication.setObjectName('authentication')

        self.blend.installEventFilter(self) 
        self.authentication.installEventFilter(self)
        self.blend.clicked.connect(self.gotoInfo)
        self.authentication.clicked.connect(self.gotoAuthentication)
        self.exit.clicked.connect(QCoreApplication.instance().quit)
    
    def gotoInfo(self):
        info.username.setText(login.name)
        info.birthday.setText(login.birthday)
        info.id.setText(login.id[0:3] + '****' + login.id[7:])
        info.email.setText(login.email)
        widget.setCurrentIndex(widget.currentIndex() + 2)
        self.GIF.stop_run()

    def gotoAuthentication(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        Authentication.username.setText(login.name)
        Authentication.birthday.setText(login.birthday)
        Authentication.id.setText(login.id[0:3] + '****' + login.id[7:])
        self.GIF.stop_run()

    def eventFilter(self, object, event):
        if hasattr(object, 'text'): #check to see if the object has text, otherwise if you hover over something without text, PyQt will return an error
            if object.objectName() == 'blend':
                if event.type() == QEvent.Enter:
                    self.GIF.flagAvatar()
                    self.GIF.resume()
                    self.GIF.Serial.connect(self.changeAvatar)
                    return True
                elif event.type() == QEvent.Leave:
                    self.GIF.stop()
                    self.blend.setStyleSheet('border-image: url(./avatar/0.png);')
                return False
            elif object.objectName() == 'authentication':
                if event.type() == QEvent.Enter:
                    self.GIF.flagTarget()
                    self.GIF.resume()
                    self.GIF.Serial2.connect(self.changeAuthentication)
                    return True
                elif event.type() == QEvent.Leave:
                    self.GIF.stop()
                    self.authentication.setStyleSheet('border-image: url(./img/verification/0.png);')
                return False



    def changeAvatar(self,str):
        self.blend.setStyleSheet('border-image: url(./avatar/' + str + '.png);')

    def changeAuthentication(self,str):
        self.authentication.setStyleSheet('border-image: url(./img/verification/' + str + '.png);')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

class AuthenticationScreen(QDialog):
    def __init__(self):
        super(AuthenticationScreen, self).__init__()
        loadUi("authentication.ui", self)
        self.TopLabel.setStyleSheet(
            'background-image : url(top_background.png);border-radius: 65px;border-bottom-right-radius: 0px;')
        self.background.setStyleSheet(
            'background-image: url(Gradient_builder_2.jpg);border-radius: 65px;'
        )
        self.TopLeftBG.setStyleSheet('background-image: url(Gradient_builder_small.jpg);')
        self.color = 0

        self.home.setStyleSheet('QPushButton#home{border-radius : 10px;border-image: url(home.png);}QPushButton#home:hover{border-radius : 10px;border-image: url(brown home.png);}QPushButton#home::pressed{border-radius : 10px;border-image: url(white home.png);}')
        self.uploadBTN.setStyleSheet('QPushButton#uploadBTN{border-radius : 10px;border-image: url(upload.png);}QPushButton#uploadBTN:hover{border-radius : 10px;border-image: url(brown upload.png);}QPushButton#uploadBTN::pressed{border-radius : 10px;border-image: url(white upload.png);}')
        self.imgBTN.setStyleSheet('QPushButton#imgBTN{border-radius : 10px;border-image: url(image.png);}QPushButton#imgBTN:hover{border-radius : 10px;border-image: url(brown image.png);}QPushButton#imgBTN::pressed{border-radius : 10px;border-image: url(white image.png);}')
        self.qrBTN.setStyleSheet('QPushButton#qrBTN{border-radius : 10px;border-image: url(qr.png);}QPushButton#qrBTN:hover{border-radius : 10px;border-image: url(brown qr.png);}QPushButton#qrBTN::pressed{border-radius : 10px;border-image: url(white qr.png);}')
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")

        self.imgBTN.clicked.connect(self.openimg)
        self.qrBTN.clicked.connect(self.openqr)
        self.uploadBTN.clicked.connect(self.decrypt)

        self.image = ''
        self.qr_image = ''



        self.home.clicked.connect(self.gotoOperation)        
        self.exit.clicked.connect(QCoreApplication.instance().quit)

        
    def decrypt(self):
        if self.qr_image == '' or self.image == '':
            return
        else:
            results = decode_qr_code(self.qr_image)
            if len(results):
                print("解碼結果是：")
                print(results[0].data.decode("utf-8"))

                img = cv2.imread(self.image)
            
                ste = ''
                
                flag = False
                row = False


                stego_col = []
                stego_row = []

                num = 0

                for i in results[0].data.decode("utf-8"):
                    if i == '[':
                        flag = True
                    if flag:
                        if ord(i) <= 57 and ord(i) >= 48:
                            num = num * 10 + int(i)
                        elif i == ',' and not row:
                            stego_col.append(num)
                            num = 0
                        elif i == ',' and row:
                            stego_row.append(num)
                            num = 0
                        elif i == ']' and not row:
                            stego_col.append(num)
                            row = True
                            flag = False
                            num = 0
                        elif i == ']' and row:
                            stego_row.append(num)

                print(stego_col)
                print(stego_row)
                print(int(results[0].data.decode("utf-8")[1]))

                magic_matrix = magic.create_magic(int(results[0].data.decode("utf-8")[1]))


                for i in range(0, len(stego_col)):
                    stego_pix_first = img[stego_col[i]][stego_row[i]][0]
                    stego_pix_second = img[stego_col[i]][stego_row[i] + 1][0]
                    ste += str(magic_matrix[stego_pix_first][stego_pix_second])

                print(ste)

                ans = ""

                for i in range(0, len(ste), 3):
                    ans += chr(int(ste[i : i + 3], 9)) 

                print(ans)
                
                name = login.name
                name = pinyin.get(name, format='strip', delimiter="")
                name = name.upper()

                hide = login.id + name + login.birthday

                print(hide)

                flag = True

                if hide == ans:
                    print('成功')
                    self.correct.setStyleSheet('border-image : url(./img/icon/check.png);')
                    self.correct2.setStyleSheet('border-image : url(./img/icon/check.png);')
                    self.correct3.setStyleSheet('border-image : url(./img/icon/check.png);')
                else:
                    self.correct.setStyleSheet('border-image : url(./img/icon/remove.png);')
                    self.correct2.setStyleSheet('border-image : url(./img/icon/remove.png);')
                    self.correct3.setStyleSheet('border-image : url(./img/icon/remove.png);')


            else:
                self.correct.setStyleSheet('border-image : url(./img/icon/remove.png);')
                self.correct2.setStyleSheet('border-image : url(./img/icon/remove.png);')
                self.correct3.setStyleSheet('border-image : url(./img/icon/remove.png);')


    def openimg(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', 'Image', '*.png *.jpg *.bmp')
        if filename is '':
            return
        img = cv2.imread(filename, -1)
        if self.img.size == 1:
            return
        self.img.setStyleSheet('border-image : url(' + filename + ');')
        self.image = filename

    def openqr(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', 'Image', '*.png *.jpg *.bmp')
        if filename is '':
            return
        img = cv2.imread(filename, -1)
        if img.size == 1:
            return
        self.qr.setStyleSheet('border-image : url(' + filename + ');')
        self.qr_image = filename

    def gotoOperation(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)
        operation.GIF.running()
        operation.GIF.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

class First_login(QDialog):
    def __init__(self):
        super(First_login, self).__init__()
        loadUi("firstlogin.ui", self)
        self.FaceBG.setStyleSheet(
            "border-image : url(pa02.jpg);border-top-left-radius:50px;")
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        self.back.setStyleSheet("border-image : url(backarrow.png);border : none")
        self.enter.clicked.connect(self.gotoOperation)
        self.back.clicked.connect(self.gotologin)
        self.authBTN.clicked.connect(self.sendemail)
        self.exit.clicked.connect(QCoreApplication.instance().quit)
        self.time = 120
        self.out = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.showtime)
        self.code = ''
        self.flag = False
        self.codeedit.textChanged.connect(self.check)
        self.password.setEchoMode(QLineEdit.Password)
        self.checkps.setEchoMode(QLineEdit.Password)

    def gotologin(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)



    def check(self):
        code = self.codeedit.text()
        if len(self.codeedit.text()) == 8:
            if self.codeedit.text() == self.code and self.code != '' and self.time != 120:
                self.flag = True
                self.codeedit.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(0, 0, 0);')
            else:
                self.flag = False
                self.codeedit.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(255, 0, 0);')
        elif len(self.codeedit.text()) > 8:
            self.codeedit.setText(code[0:8])
        else:
            self.flag = False
            self.codeedit.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(0, 0, 0);')
        

    def gotoOperation(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
            
        if not self.flag :
            self.warning.setText('請驗證信箱')
        elif self.password.text() == '':
            self.warning.setText('請輸入變更的密碼!!')
        elif len(self.password.text()) < 8:
            self.warning.setText('密碼至少要8位元!!')
        elif self.password.text() == login.account:
            self.warning.setText('密碼不能和帳號相同!!')
        elif self.password.text() != self.checkps.text():
            self.warning.setText('密碼不相符!!')
        elif self.password.text() == self.checkps.text():
            widget.setCurrentIndex(widget.currentIndex() + 1)
            c.execute("UPDATE stocks SET password = '" + self.password.text() + "' WHERE account = '" + login.account + "'")
            c.execute("UPDATE stocks SET first_login = '0' WHERE account = '" + login.account + "'")
            c.execute("UPDATE stocks SET email = '" + self.email.text() + "' WHERE account = '" + login.account + "'")
            login.email = self.email.text()

        conn.commit()   
        conn.close()

    def sendemail(self):
        

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        e_mail = ''
        for e in c.execute("SELECT * FROM stocks WHERE email LIKE '" + str(self.email.text()) + "'" ):
                e_mail = e[5]

        if e_mail != '':
            self.warning.setText('此信箱已被註冊')
        elif self.email.text() == '':
            self.warning.setText('請輸入信箱')
        elif self.time == 120:
            # 建立訊息物件
            msg = email.message.EmailMessage()

            msg["From"] = '知心好朋友'
            msg["To"] = self.email.text()
            msg["Subject"] = "人臉去識別化驗證碼"

            for i in range(8):
                self.code += chr(random.randint(97, 122))
            

            self.out = False

            print(self.code)

            # 寄送郵件主要內容
            # msg.set_content("測試郵件純文字內容") #純文字信件內容
            msg.add_alternative('您取得的驗證碼為 ' + self.code + ' ，請在60秒內完成輸入。', subtype="html")  # HTML信件內容

            # 連線到SMTP Sevver
            # 可以從網路上找到主機名稱和連線埠
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # 建立gmail連驗
            server.login('3a717039@gm.student.ncut.edu.tw', 'djehnexprhviaohz')
            try:
                server.send_message(msg)
                self.starttimer()
                self.warning.setText('')
            except:
                self.warning.setText('此信箱不符合規格')
                self.code = ''
            server.close()  # 發送完成後關閉連線

    def starttimer(self):
        self.timer.start(1000)

    def showtime(self):
        self.time -= 1
        self.authBTN.setText(str(self.time) + 's')
        if self.time == 0:
            self.endtimer()

    def endtimer(self):
        self.out = True
        self.timer.stop()
        self.authBTN.setText('傳送驗證碼')
        self.time = 120
        

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            self.gotoOperation()

class ChangePassword(QDialog):
    def __init__(self):
        super(ChangePassword, self).__init__()
        loadUi("changepassword.ui", self)

        self.FaceBG.setStyleSheet(
            "border-image : url(pa02.jpg);border-top-left-radius:50px;")
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        self.back.setStyleSheet("border-image : url(backarrow.png);border : none")
        
        self.exit.clicked.connect(QCoreApplication.instance().quit)

        self.authBTN.clicked.connect(self.sendemail)
        self.vcode.textChanged.connect(self.check)
        self.enter.clicked.connect(self.gotochangepassword2)
        self.back.clicked.connect(self.gotologin)
        self.account = ''
        
        self.time = 120
        self.out = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.showtime)
        self.flag = False
        self.code = ''
        

    def gotochangepassword2(self):
        if self.flag:
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            self.warning.setText('請輸入正確的驗證碼')  

    def gotologin(self):
        widget.setCurrentIndex(widget.currentIndex() - 7)


    def check(self):
        code = self.vcode.text()
        if len(self.vcode.text()) == 8:
            if self.vcode.text() == self.code and self.code != '' and self.time != 120:
                self.flag = True
                self.vcode.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(0, 0, 0);')
            else:
                self.flag = False
                self.vcode.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(255, 0, 0);')
        elif len(self.vcode.text()) > 8:
            self.vcode.setText(code[0:8])
        else:
            self.flag = False
            self.vcode.setStyleSheet('background-color:rgba(0,0,0,0);border:none;border-bottom:2px solid rgba(46,82,101,200);padding-bottom:7px;color: rgb(0, 0, 0);')

    def starttimer(self):
        self.timer.start(1000)

    def showtime(self):
        self.time -= 1
        self.authBTN.setText(str(self.time) + 's')
        if self.time == 0:
            self.endtimer()

    def endtimer(self):
        self.out = True
        self.timer.stop()
        self.authBTN.setText('傳送驗證碼')
        self.time = 120

    def sendemail(self):

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        e_mail = ''
        for e in c.execute("SELECT * FROM stocks WHERE account LIKE '" + str(self.username.text()) + "'" ):
                e_mail = e[5]
                self.account = e[0]

        if self.username.text() == '':
            self.warning.setText('請輸入學號')
        elif self.account != self.username.text():
            self.warning.setText('沒有此學號')
        elif self.email.text() == '':
            self.warning.setText('請輸入信箱')
        elif e_mail != self.email.text():
            self.warning.setText('此信箱不是驗證信箱')  
        elif self.time == 120:
            # 建立訊息物件
            msg = email.message.EmailMessage()

            msg["From"] = '知心好朋友'
            msg["To"] = self.email.text()
            msg["Subject"] = "人臉去識別化驗證碼"

            for i in range(8):
                self.code += chr(random.randint(97, 122))
            


            self.out = False

            print(self.code)

            # 寄送郵件主要內容
            # msg.set_content("測試郵件純文字內容") #純文字信件內容
            msg.add_alternative('您取得的驗證碼為 ' + self.code + ' ，請在60秒內完成輸入。', subtype="html")  # HTML信件內容

            # 連線到SMTP Sevver
            # 可以從網路上找到主機名稱和連線埠
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # 建立gmail連驗
            server.login('3a717039@gm.student.ncut.edu.tw', 'djehnexprhviaohz')
            try:
                server.send_message(msg)
                self.starttimer()
                self.warning.setText('')
            except:
                self.warning.setText('此信箱不符合規格')
                self.code = ''
            server.close()  # 發送完成後關閉連線

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            self.gotochangepassword2()

class ChangePassword2(QDialog):
    def __init__(self):
        super(ChangePassword2, self).__init__()
        loadUi("changepassword2.ui", self)
        self.FaceBG.setStyleSheet(
            "border-image : url(pa02.jpg);border-top-left-radius:50px;")
        self.exit.setStyleSheet("border-image : url(cross.png);border : none")
        self.back.setStyleSheet("border-image : url(backarrow.png);border : none")
        
        self.exit.clicked.connect(QCoreApplication.instance().quit)
        self.back.clicked.connect(self.gotologin)
        self.enter.clicked.connect(self.change)

    def gotologin(self):
        widget.setCurrentIndex(widget.currentIndex() - 8)

    def change(self):
        if self.password.text() == '':
            self.warning.setText('請輸入密碼')
        elif len(self.password.text()) < 8:
            self.warning.setText('密碼至少要8位元')
        elif self.password.text() != self.checkps.text():
            self.warning.setText('兩邊密碼並不相同')
        else:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("UPDATE stocks SET password = '"+self.password.text()+"' WHERE account = '"+changepassword.account+"'")
            conn.commit()
            conn.close()
            widget.setCurrentIndex(widget.currentIndex() - 8)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            self.change()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.moveFlag = False
            


# main
app = QApplication(sys.argv)
login = LoginScreen()
widget = QStackedWidget()
widget.setWindowFlags(Qt.FramelessWindowHint)
widget.setAttribute(Qt.WA_TranslucentBackground)
widget.addWidget(login)
widget.setFixedHeight(2000)
widget.setFixedWidth(2000)



first_login = First_login()
operation = OperationScreen()
Authentication = AuthenticationScreen()
info = InfoScreen()
choose = ChooseScreen()
blend = BlendingScreen()
changepassword = ChangePassword()
changepassword2 = ChangePassword2()
widget.addWidget(first_login)
widget.addWidget(operation)
widget.addWidget(Authentication)
widget.addWidget(info)
widget.addWidget(choose)
widget.addWidget(blend)
widget.addWidget(changepassword)
widget.addWidget(changepassword2)



widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
