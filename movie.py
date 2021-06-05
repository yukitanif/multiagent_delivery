import cv2

img_array=[]
for i in range(30):
    img=cv2.imread("pics/step"+str(i)+".png")
    height,width,layers=img.shape
    size=(width,height)
    img_array.append(img)

name="mov_multi.mp4"
out = cv2.VideoWriter(name, cv2.VideoWriter_fourcc('M','P','4','V'),3,size)

for i in range(len(img_array)): out.write(img_array[i])
out.release()