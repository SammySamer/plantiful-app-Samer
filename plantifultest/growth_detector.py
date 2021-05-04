#NEEDS TO BE ADJUSTED TO RETRIEVE IMAGE FROM HEROKU FELIX
#AFTER RETRIEVING IMAGE, CODE LOGIC SHOULD CHANGE TO JUST PREDICT IT 
#AND RETURN PREDICTION AND IMAGE TO DJANGO

import cv2 as cv
import os
print("Loading classifier....")
cascade_limestone = cv.CascadeClassifier('cascade/cascade.xml')
stages_file = open("stages.txt", "r")
stage=""
falsepos=0
truepos=0
falseneg=0
trueneg=0
total=0
for filename in stages_file:
    values = filename.split('_')
    image = cv.imread(values[0])
    stage=values[1]
    total=total+1
    if(total%300==0):
        print("300")

    rectangles = cascade_limestone.detectMultiScale(image)
    if(len(rectangles)>15):
    #    print("In fruiting stage")
        if(stage=="Fruiting\n"):
            truepos=truepos+1
        else:
            falsepos=falsepos+1
    else:
        #prediction is nonfruiting
        if(stage=="Initial\n" or stage=="Flowering\n"):
            trueneg=trueneg+1
        else:
            falseneg=falseneg+1

print(truepos)
print(falsepos)
print(trueneg)
print(falseneg)
print(total)
exit()