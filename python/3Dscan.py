#! /usr/bin/python

# ********************************************************           
#
#  3DScan.py:  Program to capture a 3D scan using a        
#              Hokuyo laser range finder and a Dynamixel
#              MX-28T servo
#                                                          
#  Authors:    Biayna Bogosian - biayna.bogosian@gmail.com 
#              Narek Gharakhanian - nagharakhani@gmail.com                          
#                                                          
#  Purpose:    Final project for Glendale Community College
#              ENGR-298/299 class            
#                                                          
#  Usage:      Documentation can be found here:
#              TBD
#          
# ********************************************************


import os
from lib_robotis import *
import os.path
from termios import tcflush, TCIFLUSH
import subprocess
import sys
import math
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders
import shutil

dyn = USB2Dynamixel_Device('/dev/ttyUSB0')
p = Robotis_Servo( dyn, 1, series = "MX" )
p.move_angle(math.radians(0))


got_new_range = False
servo = p.read_angle()
j = 0
save_path = '/home/vision/3dpoint cloud'

name = input("Please enter your name: ")
email = input("Please enter an e-mail address: ")
major = input("What is your major? ")


min_range = 1.1
max_range = 2.5
srv_start_angle  = -20
precision = 4


with open(os.path.join(save_path, "Final.csv") , 'w') as f:
    process = subprocess.Popen("/opt/ros/indigo/bin/rostopic echo /scan", stdout=subprocess.PIPE, shell=True)
    shouldBreak= False
    angleRad = 0
    srv_angle_max = 80
 
    srv_angle_max = srv_angle_max * precision
    for j in range (0, srv_angle_max):
        angleRad = math.radians(srv_start_angle + j * (1/ float(precision)))

       
        p.move_angle(angleRad)
        process.stdout.flush()
        shouldBreak=False
        for line in iter(process.stdout.readline, ''):
            if(line.find("angle_min") >= 0):
                temp = line.split(":")
                angle_min = float(temp[1])

            elif(line.find("angle_max") >= 0):
                temp = line.split(":")
                angle_max = float(temp[1])

            elif(line.find("angle_increment") >= 0):
                temp = line.split(":")
                angle_increment = float(temp[1])

            elif(line.find("ranges") >= 0):
                got_new_range = True
                temp = line.split(":")
                temp = temp[1]
                temp = temp.replace("[", "")
                temp = temp.replace("]", "")
                range_list = temp.split(",")
                ranges = []
                for a in range_list:
                    if(a.find("inf") >= 0):
                        ranges.append(0.0)
                    else:
                        ranges.append(float(a))

                idx = 0
                for r in ranges:
                    # since 0 deg on the LIDAR frame is the Y axis,
                    # we need to 90 degrees to our calculated angle
                    angle = angle_min + idx*angle_increment + (math.pi / 2.0)
                    idx = idx + 1
                    if(angle> 1.22111 and angle<1.91889):
                        if(r>min_range and r<max_range):
                            x = r * math.sin(angle) * math.cos(angleRad) * (-1)
                            y = r * math.sin(angle) * math.sin(angleRad)
                            z = r * math.cos(angle)
                            f.write(str(x) + ", " + str(z) + ", " + str(y) + "\n")
                    
                shouldBreak = True
            if(shouldBreak):
                break
#---------------------------------------------------------------------------------------
#-----------------------------3D Plotting with Processing-------------------------------
shutil.copy("/home/vision/3dpoint cloud/Final.csv", "/home/vision/3dpoint cloud/final")
# os.rename("Final.csv", name + ".csv")
old_file = "/home/vision/3dpoint cloud/final/Final.csv" 
new_file = "/home/vision/3dpoint cloud/final" +'/' + name + ".csv" 
os.rename(old_file,new_file)
#---------------------------------------------------------------------------------------
#-----------------------------3D Plotting with Processing-------------------------------
os.chdir("/home/vision/Programms/processing-3.1.1")
os.system("./processing-java --sketch=/home/vision/Programms/Processing3views/FrontView --run")

os.chdir("/home/vision/Programms/processing-3.1.1")
os.system("./processing-java --sketch=/home/vision/Programms/Processing3views/SideView --run")

os.chdir("/home/vision/Programms/processing-3.1.1")
os.system("./processing-java --sketch=/home/vision/Programms/Processing3views/ThreeQuarterView --run")

#---------------------------------------------------------------------------------------
#----------------------------------Image Stitching--------------------------------------
im = Image.new("RGBA", (1000, 1000), 0)

im.paste((0, 0, 0), (0, 0, 1000, 1000))

im1 = Image.open("/home/vision/Programms/Processing3views/FrontView/FrontView.png")
im2 = Image.open("/home/vision/Programms/Processing3views/SideView/SideView.png")
im3 = Image.open("/home/vision/Programms/Processing3views/ThreeQuarterView/ThreeQuarterView.png")
im4 = Image.open("/home/vision/Programms/Processing3views/Background/image_4.png")

out = im1.resize((500, 500))
im.paste(out, (0, 0))
out = im2.resize((500, 500))
im.paste(out, (500, 0))
out = im3.resize((500, 500))
im.paste(out, (0, 500))
# out = im4.resize((500, 500))
# im.paste(out, (500, 500))

draw = ImageDraw.Draw(im)
font = ImageFont.truetype("/home/vision/Programms/Processing3views/OpenSans-Regular.ttf", 24)

draw.text((515, 540), "GCC Capstone Robotics Project Sp2016", (255, 255, 255), font)
draw.text((515, 600), "3D Scanned Profile", (255, 255, 255), font)
font = ImageFont.truetype("/home/vision/Programms/Processing3views/OpenSans-Regular.ttf", 17)
draw.text((515, 660), "Vision Team: ", (255, 255, 255), font)
draw.text((620, 660), "Narek Gharakhanian + Biayna Bogosian", (255,255,255), font)
os.chdir("/home/vision/Programms/Output Images/")
im.save(name + ".png", "PNG")


#---------------------------------------------------------------------------------------
#----------------------------------E-Mailing--------------------------------------------
# Reading the username and password for the email account from a text file
txt = open("eMailInfo.txt") 	# open file to read
line = txt.readlines()		# put everything into a list
temp = line[0].split(': ')[-1]	
temp = temp[:-1]		# read the sting without the “\n”
userName = temp
temp = line[1].split(': ')[-1]
passWord = temp
txt.close()

def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = userName
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(userName, passWord)
   mailServer.sendmail(userName, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

mail(email,
   "Hello from GCC Capstone!",
   "This is an e-mail sent from the vision team. \n Attached is your 3D Scan.",
   name + ".png")

