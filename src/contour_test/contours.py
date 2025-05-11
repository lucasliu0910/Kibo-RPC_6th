# import numpy as np
import cv2 as cv
import imutils

from enum import Enum
class Hierarchy(Enum):
    Next     = 0
    Previous    = 1
    First_Child  = 2
    Parent   = 3

# img = cv.imread('./data/images/coin_100p_0_1.png', cv.IMREAD_GRAYSCALE)
# img = cv.imread('./data/images/key_100p_0_1.png', cv.IMREAD_GRAYSCALE)
# img = cv.imread('./data/images/4b76e214-5bef-4adc-981f-ad6119932306.png', cv.IMREAD_GRAYSCALE)
# img = cv.imread('./data/images/468070fc-23e0-4034-90ae-ca86b39935b7.png', cv.IMREAD_GRAYSCALE)
img = cv.imread('./data/images/c07d7f1c-581c-4b12-9105-9a131705f785.png', cv.IMREAD_GRAYSCALE)
img = imutils.resize(img, width=1024)
assert img is not None, "file could not be read, check with os.path.exists()"
ret,thresh = cv.threshold(img,127,255,0)
# im2,contours,hierarchys = cv.findContours(thresh, 1, 2)
# contours,hierarchys = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
# contours,hierarchys = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contours,hierarchys = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# contours,hierarchys = cv.findContours(thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
# contours,hierarchys = cv.findContours(thresh, cv.RETR_FLOODFILL, cv.CHAIN_APPROX_SIMPLE)
# cnt = contours[0]
# M = cv.moments(cnt)
# print( M )
# print("contours: ", len(contours))
# for cnt in contours:
    # print(cnt)
    # print(cv.contourArea(cnt))
    # print(cv.isContourConvex(cnt))
    # cv.drawContours(img, [cnt], 0, (0, 255, 0), 2)
    # cv.imshow('img', img)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    # if cv.contourArea(cnt) > 100:
    #     cv.drawContours(img, [cnt], 0, (0, 255, 0), 2)
    #     break
# 
    # x,y,w,h = cv.boundingRect(cnt)
    # cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

# for h in hierarchy:
print("contours count:",len(contours))
i=0
for cnt in contours:
    x,y,w,h = cv.boundingRect(cnt)
    print(f"contour {i}:", x,y,w,h)
    i += 1
# print("contours:",contours)
print("hierarchys count:",len(hierarchys))
print("hierarchys:",hierarchys)

def find_parent(hierarchy, index):
    # print("index:",index)
    # print("hierarchy[index]:",hierarchy[index])
    if hierarchy[index][Hierarchy.Parent.value] == -1:
        return index
        # return hierarchy[index][2]
    else:
        return find_parent(hierarchy, hierarchy[index][Hierarchy.Parent.value])

# for h in hierarchy:
    # print(h)
    # print(h[0])
    # print(h[1])
    # print(h[2])
    # print(h[3])
    # for i in range(len(h)):
    #    p = find_parent(h, i)
    #    print(f"contour {i}'s head is {p}")    

hierarchy = hierarchys[0]
headi = find_parent(hierarchy,0) 
childi = hierarchy[headi][Hierarchy.First_Child.value]

# cnt = contours[1]
# x,y,w,h = cv.boundingRect(cnt)
# cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
# i=0
# for cnt in contours:
#     x,y,w,h = cv.boundingRect(cnt)
#     cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
#     # cv.putText(img, str(cv.contourArea(cnt)), (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#     cv.putText(img, str(i), (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#     i += 1

while childi != -1:
    cnt = contours[childi]
    x,y,w,h = cv.boundingRect(cnt)
    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    # cv.putText(img, str(cv.contourArea(cnt)), (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv.putText(img, str(childi), (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    childi = hierarchy[childi][Hierarchy.Next.value]

cv.imshow('img', img)
# cv.imshow('thresh', thresh)
cv.waitKey(0)
cv.destroyAllWindows()

cv.imwrite('./data/images/contours.png', img)
