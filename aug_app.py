from tkinter import *
from tkinter import filedialog
import tkinter.font as font
from tkinter import messagebox
from tkinter.ttk import Progressbar
import utils
import cv2 as cv
import csv
import os
import random
import numpy as np
from tqdm import tqdm_gui
from PIL import ImageTk, Image

root = Tk()
root.geometry("1000x700")
root.title("Data Augmentation DESKTOP")
root.configure(background='#8d8f6d')
myFont = font.Font(size=20,weight='bold')
frame=Canvas(root,bg='#ecf296')
frame.pack(side=TOP, expand=YES)
frame.grid_propagate(True)
dict = {'i_input':'None','i_output':'None','csv_input':'None','csv_output':'None','translate_factor':0.2,'rotate_factor':45,'scale_factor':0.5}

def createNewWindow():
    newWindow = Toplevel(root)
    newWindow.geometry("900x400")
    newWindow.configure(background="#ecf296")
    T = Text(newWindow)
    fontStyle = font.Font(size=20)
    txt_help= Label(newWindow,text = "HELP",bg="black",fg="white",font=fontStyle).pack(side=TOP, expand=YES)
    T.pack(side=TOP, expand=YES)
    T.configure(font=("Arial", 16),background='#8d8f6d')
    quote = "1. INPUT IMAGE: Select the folder which contains images to be augmented.\n\n2. INPUT BOUNDING BOXES: Select the file which contains Bounding box of the images.\nNOTE: Comma seprated csv file.\n\n3. OUTPUT IMAGE: Select/Create the folder to save the augmented images. \n\n4. OUTPUT BOUNDING BOXES : Create the default .csv file path to store new bounding boxes.\n\n4. TECHNIQUE: Select any one of the given Augmentation Technique.\nNOTE: If Rotation, Scale or Translate is selected provide Rotation, Scale or Translate respectively.\n\n5. Press Start."
    T.insert(END, quote)
    T.config(state=DISABLED)
    newWindow.resizable(0, 0)
    
def path_directory_input():
    directory= filedialog.askdirectory()
    dict['i_input']=directory
    return directory
def path_directory_output():
    directory1= filedialog.askdirectory()
    dict['i_output']=directory1
    return directory1
def path_file():
    file= filedialog.askopenfilename(initialdir = "/",filetypes = (("txt files","*.txt"),("all files","*.*")))
    dict['csv_input']=file
    return file
def path_csv():
    csv_file= filedialog.asksaveasfilename(defaultextension=".csv")
    dict['csv_output']=csv_file
    return csv_file
def function_call():
    augmentationtype = clicked.get()
    if(all(dict.values())):
        print(dict['translate_factor'])
        print(dict['scale_factor'])
        aug_function(dict['i_input'],dict['i_output'],dict['csv_input'],dict['csv_output'],augmentationtype,dict['translate_factor'],dict['rotate_factor'],dict['scale_factor'])
        messagebox.showinfo("Title", "Augmentation  done")
    else:
        messagebox.showwarning("Title", "Incomplete Input")
def scale_active(self):
    if clicked.get()== 'Translate':
        scale_translate.config(state=NORMAL,highlightbackground="GREEN")
        scale_scale.config(state=DISABLED,length=200,highlightbackground="white")
        scale_rotate.config(state=DISABLED,length=200,highlightbackground="white")
    elif clicked.get()== 'Rotate':
        scale_rotate.config(state=NORMAL,highlightbackground="GREEN")
        scale_scale.config(state=DISABLED,length=200,highlightbackground="white")
        scale_translate.config(state=DISABLED,length=200,highlightbackground="white")
    elif clicked.get()== 'Scale':
        scale_scale.config(state=NORMAL,highlightbackground="GREEN")
        scale_rotate.config(state=DISABLED,length=200,highlightbackground="white")
        scale_translate.config(state=DISABLED,length=200,highlightbackground="white")
    elif clicked.get()=='Shear' or  clicked.get()=='Brightness and Contrast' or clicked.get()=='Flip' or clicked.get()=='Saturation':
        scale_rotate.config(state=DISABLED,length=200,highlightbackground="white")
        scale_translate.config(state=DISABLED,length=200,highlightbackground="white")
        scale_scale.config(state=DISABLED,length=200,highlightbackground="white")
        
def factor_t(value):
    dict['translate_factor']  =value
def factor_r(value):
    dict['rotate_factor']  =value
def factor_s(value):
    dict['scale_factor']  =value

def drawRectangle(img,outputpath, bounding_box, output_name):
    '''
    Utility Function to draw rectangle around calculated coordinates (bounding box coords)

    Parameters
    =======
    1. img (np.array): Rectangle will be drawn around this image
    2. bounding_box (list/np.array): coords
    3. output_name (string): filename to save the image with

    '''
    #print("\ndraw rect")
    img_temp = img # Create image copy
    # Create a rectangle for given coordinates
    cv.rectangle(img_temp, (bounding_box[0], bounding_box[1]), (bounding_box[2], bounding_box[3]), (255, 0, 0), 2)
    # Write the output image
    write(img_temp,outputpath, str_output = output_name)

def write(img,outputpath, str_output = "output.jpeg"):
    '''
    Utility function to write image

    Parameters
    ======
    1. img (np.array): Image to write
    2. str_output (string): Filename to save the image with
    '''
    #print("\nwriting")
    #outputpath = '/home/shalini/Desktop/test_impl'     # 1. path of directory where augmented images are to be stored
    cv.imwrite(os.path.join(outputpath,str_output), img)
    #Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
    image_path=os.path.join(outputpath, str_output)
    
    #The Label widget is a standard Tkinter widget used to display a text or image on the screen.
    #The Pack geometry manager packs widgets in rows or columns.

def aug_function(inpath, outputpath, incsvfilepath,outcsvfilepath, augtype, t_factor, r_factor,s_factor):
    #print("\n")
    #print(augtype)
    #print("\n")

    

    file1 = open(incsvfilepath, 'r') # 2. open file containing bounding box coordinates
    lines = file1.readlines()
    randlist = lines          # selecting k random images to augment

    for i in tqdm_gui(randlist):

            x = i.strip().split(",")
            #print("\nx: ")
            #print(x)
            #print("\n")
            mylist = [int(float(x[1])),int(float(x[2])),int(float(x[3])),int(float(x[4]))] #extract coordinates from file
            cord = []
            for i in mylist:
                    a = int(i)
                    cord.append(a)


            a = x[0] # image filename

            imageFolderPath = inpath # 3. input image folder path
            loc = os.path.join(imageFolderPath, a)   #location of image


            # # Brightness and Contrast
            if(augtype == 'Brightness and Contrast'):


                image=cv.imread(loc)

                alpha=random.triangular(1,2)
                beta=random.randint(20,50)

                result=cv.addWeighted(image,alpha,np.zeros(image.shape,image.dtype),0,beta)


                oname = "brightness_"+a
                csvr = [oname] + mylist

                with open(outcsvfilepath,'a',newline ='') as file:       # 4. write to  csv file
                    writer = csv.writer(file)
                    writer.writerow(csvr)
                #print(mylist)

                #print(oname)
                drawRectangle(result,outputpath,cord, output_name = oname )



            else:


                img_class = utils.Image(path = loc) # Create image class
                img = img_class.getImage()
                coord = cord
                if(augtype == 'Scale'):
        # # Test Scaling
                    output = img_class.transform('scale', coord,s_factor)
                    oname = "scaled_"+a # name of output image

                    ocord = output[1] # augmented coordinates
                    csvr = [oname] + output[1]  # line to be written to output csv file

                    with open(outcsvfilepath,'a',newline ='') as file:  # 4. write to  csv file
                        writer = csv.writer(file)
                        writer.writerow(csvr)

                    drawRectangle(output[0],outputpath ,output[1], output_name = oname )  # for saving output image

                elif(augtype == 'Rotate'):
                    #print("\nrotate")
        ##Test Rotation
                    output = img_class.transform('rotate', coord, r_factor)
                    oname = "rotated_"+a
        #   ##print("ONAME",oname)
        #    ##print("New Bounding Boxes rotation: ", output[1])
                    ocord = output[1]
                    csvr = [oname] + output[1]
        #    ##print("ocord",ocord)
                    with open(outcsvfilepath,'a',newline ='') as file:
                        writer = csv.writer(file)
                        writer.writerow(csvr)

                    drawRectangle(output[0],outputpath ,output[1], output_name = oname )
            #drawRectangle(img,outputpath, coord, output_name = "output_original.jpeg")

                elif(augtype == 'Translate'):
                    #print("\ntranslate")
        # # Test Translation - Horizontal
                    output = img_class.transform('translate', coord, t_factor)
                    oname = "translated_"+a # name of output image

                    ocord = output[1] # augmented coordinates
                    csvr = [oname] + output[1]  # line to be written to output csv file

                    with open(outcsvfilepath,'a',newline ='') as file:  #write to  csv file
                        writer = csv.writer(file)
                        writer.writerow(csvr)

                    drawRectangle(output[0],outputpath, output[1], output_name = oname )  # for saving output image

                elif(augtype == 'Flip'):

                    #print("\nflip")
        #   # Test Flipping
                    output = img_class.transform('flip', coord)
                    oname = "flipped_"+a # name of output image

                    ocord = ' '.join(str(e) for e in output[1]) # augmented coordinates

                    csvr = oname + ' ' + ocord  # line to be written to output csv file
                    listcsvr = csvr.split(" ")
                    #print("\noutcsvfilepath: ")
                    #print(outcsvfilepath)
                    #print("\ncsvr: ")
                    #print(csvr)
                    with open(outcsvfilepath,'a',newline ='') as file:  #write to  csv file
                        writer = csv.writer(file)
                        writer.writerow(listcsvr)

                    drawRectangle(output[0],outputpath, output[1], output_name = oname )  # for saving output image


                elif(augtype == 'Shear'):
        # # Test Shear
                    #print("\nshear")
                    output = img_class.transform('shear', coord)
                    oname = "shear_"+a # name of output image

                    ocord = output[1] # augmented coordinates
                    csvr = [oname] + output[1]  # line to be written to output csv file

                    with open(outcsvfilepath,'a',newline ='') as file:  #write to  csv file
                        writer = csv.writer(file)
                        writer.writerow(csvr)

                    drawRectangle(output[0],outputpath, output[1], output_name = oname )  # for saving output image

                elif(augtype == 'Saturation'):
                    #print("\nhsv")
                    HSV_output_name = "Saturated_"+a
                    img_HSV,bboxes_HSV = utils.RandomHSV(hue=None, saturation=100, brightness=None)(img.copy(), cord.copy())
                    drawRectangle(img_HSV,outputpath,bboxes_HSV,output_name = HSV_output_name ) # for saving output image

                    csvr = [HSV_output_name] + bboxes_HSV   # line to be written to output csv file
                    with open(outcsvfilepath, 'a', newline='') as file:  #write to  csv file
                            writer = csv.writer(file)
                            writer.writerow(csvr)

buttonExample = Button(root,text="Help",command=createNewWindow,bg="white",fg="black")
buttonExample.place(x=1,y=1)
inpath=Button(frame,text="IMAGE INPUT",command=path_directory_input,bg='white',activebackground='linen',height = 1, width = 25)
inpath.grid(row=0,column=0, padx=10, pady=10,columnspan=2)
incsvfilepath=Button(frame,text="BOUNDING BOX INPUT",command=path_file,bg='white',activebackground='linen',height = 1, width = 25)
incsvfilepath.grid(row=1,column=0,padx=10, pady=10,columnspan=2)
outputpath=Button(frame,text="IMAGE OUTPUT",command=path_directory_output,bg='white',activebackground='linen',height = 1, width = 25)
outputpath.grid(row=2,column=0,padx=10, pady=10,columnspan=2)
outcsvfilepath=Button(frame,text="BOUNDING BOX OUTPUT",command=path_csv,bg='white',activebackground='linen',height = 1, width = 25)
outcsvfilepath.grid(row=3,column=0,padx=10, pady=10,columnspan=2)

clicked=StringVar()
clicked.set("TECHNIQUE")

augtype=OptionMenu(frame,clicked,"Brightness and Contrast","Flip","Rotate","Shear","Scale","Saturation","Translate",command=scale_active)
augtype.grid(row=4,column=0,padx=10, pady=10,columnspan=2)
augtype['font']=myFont
augtype.config(bg = "white",width="25",height='1')

txttranslate = Label(frame, text = "Tanslation factor: ",bg="black",fg="white")
txtrotate = Label(frame, text = "Rotation angle: ",bg="black",fg="white")
txtscale= Label(frame,text = "Scaling factor:",bg="black",fg="white")


scale_translate= Scale( frame, from_ = 0, to = 1, orient = HORIZONTAL,resolution = 0.1,command=factor_t,bg="white")
txttranslate.grid(row=5,column=0)
scale_translate.grid(row=5,column=1,padx=10, pady=10)
scale_translate.config(state=DISABLED,length=200,highlightbackground="white")

scale_rotate= Scale( frame, from_ = 0, to = 360, orient = HORIZONTAL,resolution = 1,command=factor_r,bg="white")
txtrotate.grid(row=6,column=0)
scale_rotate.grid(row=6,column=1,padx=10, pady=10)
scale_rotate.config(state=DISABLED,length=200,highlightbackground="white")

scale_scale= Scale( frame, from_ = 0, to = 1, orient = HORIZONTAL,resolution = 0.1,command=factor_s,bg="white")
txtscale.grid(row=7,column=0)
scale_scale.grid(row=7,column=1,padx=10, pady=10)
scale_scale.config(state=DISABLED,length=200,highlightbackground="white")

call=Button(frame,text="Start",command=function_call,bg='white',activebackground='linen',height = 1, width = 25)
call.grid(row=8,column=0,padx=10, pady=10,columnspan=2)
call['font']=inpath['font'] =outputpath['font']=incsvfilepath['font']=outcsvfilepath['font']=myFont
#now pass this parameters to main

root.mainloop()
