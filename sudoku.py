import cv2
import imutils
import numpy as np
import easyocr


def reorderPoints(points):
    points=points.reshape((4,2))
    newpoints=np.zeros((4,1,2),dtype=np.int32)
    sum=points.sum(1)
    newpoints[0]=points[np.argmin(sum)]
    newpoints[3]=points[np.argmax(sum)]
    diff=np.diff(points,axis=1)
    newpoints[1]=points[np.argmin(diff)]
    newpoints[2]=points[np.argmax(diff)]
    return newpoints

def processImg(img):
    grayimg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blurimg = cv2.GaussianBlur(grayimg, (9,9),0)
    
    
    
    # timg = cv2.adaptiveThreshold(blurimg,255,1,1,3,1)
    
    # blurimg = cv2.GaussianBlur(grayimg, (3,3), 1)
    
    timg = cv2.adaptiveThreshold(blurimg,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,9,2)
    timg=cv2.bitwise_not(timg)
    kernel = np.ones((3,3), np.uint8)
    timg = cv2.dilate(timg, kernel)
    keypoints = cv2.findContours(timg.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    # contours,h = cv2.findContours(timg.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    newimg = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)

    
    
    contours=sorted(contours,key=cv2.contourArea,reverse=True)
    location=None
    for c in contours:
        area=cv2.contourArea(c)
        if area>550:
            perimeter=cv2.arcLength(c,True)
            curve=cv2.approxPolyDP(c,0.02*perimeter,True)
            if(len(curve)==4):
                location=curve
                break
    # print(location)   
    location=reorderPoints(location)
    # print(location)
    newimg=cv2.drawContours(img,location,-1,(0,255,0),9)

    pts1=np.float32(location)
    pts2=np.float32([[0,0],[450,0],[0,450],[450,450]])
    matrix=cv2.getPerspectiveTransform(pts1,pts2)
    warpimg=cv2.warpPerspective(newimg,matrix,(450,450))
    warpimg=cv2.cvtColor(warpimg,cv2.COLOR_BGR2GRAY)

    # splitting the board into each cell
    rows=np.vsplit(warpimg,9)
    boxes=[]
    for r in rows:
        cols=np.hsplit(r,9)
        for c in cols:
            boxes.append(c)
    return boxes

def printGrid(grid):
    for i in range(81):
        temp=i%9
        if grid[i]=='0':
            print("_",end=' '),
        else:
            print(grid[i],end=' '),
        if temp==8:
            print("\n")    


imgpath="sudoku board images/images2.jpeg"
img=cv2.imread(imgpath)
img=cv2.resize(img,(450,450))
cv2.imshow("image",img)
cv2.waitKey(0)

boxes=processImg(img)
# for b in boxes:
#     cv2.imshow("box",b)
#     cv2.waitKey(0)
reader = easyocr.Reader(['en'],gpu=False)
grid=[]

for i in range(81):
    result=reader.readtext(boxes[i],detail=0)
    if(len(result)==0):
        grid.append('0')
    else:
        grid.append(result[0])

printGrid(grid)