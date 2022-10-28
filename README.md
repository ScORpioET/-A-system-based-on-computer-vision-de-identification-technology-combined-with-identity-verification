# 一種基於電腦視覺特徵檢測之人臉圖像去識別化技術

專題報告書：https://drive.google.com/file/d/12yh4suCy9fCvvE52iMcX6T6TMDkWrEVj/view?usp=sharing

<br>

## About
本篇所描述利用低廉的設備完成基於電腦的人臉去識別化(電腦無法辨識但肉眼可以辨識)，並且添加了資料隱藏技術將該人的信息藏匿於影像之中，使該影像能夠進行身分驗證。

<br>
功能和UI展示：https://www.youtube.com/watch?v=8A1POCWfVZ8
<br>

## Method
### De-identification
透過Dlib提供的機器學習方法偵測人臉的106的特徵點，並利用特徵點將眉毛、鼻子、嘴巴這些臉部器官隨機替換成別人的器官，來達成去識別化的效果。
### Authentication
利用Chang等學者提出的魔術矩陣 (https://link.springer.com/article/10.1007/s11042-019-7252-x) 來達成資料隱藏的效果。


## 設備
### 硬體
- CPU == Intel i7-2600(3.4GHz)
- GPU == GTX 750 Ti (2G)
- RAM == 8GB (1600Mhz)

### 軟體
- python == 3.7.9
- numpy == 1.19.1
- cv2 == 4.5.0
- dlib == 19.21.1
- scipy == 1.5.2
- sqlite3 == 2.6.0


## 範例
### 轉換前
![image](orignal.png)
### 轉換後
![image](out.png)

範例中我們將他的眉毛、鼻子、嘴巴替換成資料庫中的隨機的男性白人的。
<br>
<br>
Microsoft API confidence level：0.75567
<br>
Euclidean Distance of facial featrue：0.45103000577102864
<br>
<br>
在人臉辨識中，信心值超過80%或是歐式距離低於0.4才會視為是同一個人，我們人類用肉眼可以說是很難分別出這兩個人的差異，但對於電腦來說這兩個是完全不同的人。
