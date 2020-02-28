import cv2
  
image = cv2.imread('ced.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('Test_gray1.jpg', gray)
  

  
(thresh, im_bw) = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 90
im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]

cv2.imwrite('bw_image.jpg', im_bw)

cv2.imshow('Original image',image)
cv2.imshow('Gray image', gray)
cv2.imshow('bw image', im_bw)



cv2.waitKey(0)
cv2.destroyAllWindows()

 