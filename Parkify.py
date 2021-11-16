from tkinter import *
from tkinter import messagebox,filedialog
import cv2
from datetime import datetime
import imutils
import sqlite3
import numpy as np
import pytesseract
import csv
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\JATIN\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def imgrec(temp):#for image detection 
    car= cv2.imread(temp,cv2.IMREAD_COLOR)
    car = cv2.resize(car, (600,400) )

    gray = cv2.cvtColor(car, cv2.COLOR_BGR2GRAY) 
    gray = cv2.bilateralFilter(gray, 13, 15, 15) 

    edged = cv2.Canny(gray, 30, 200) 
    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None

    for c in contours:
        
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print ("No contour detected")
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(car, [screenCnt], -1, (0, 0, 255), 3)

    mask = np.zeros(gray.shape,np.uint8)
    new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
    new_image = cv2.bitwise_and(car,car,mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx+1, topy:bottomy+1]

    text = pytesseract.image_to_string(Cropped, config='--psm 11')
    for i in text:
        if(i=='O' or i=='-' or i=='o' or i=='~' or i=='?' or i==' '):
            text=text.replace(i,"")
    print("Detected license plate Number is:",text)
    img = cv2.resize(car,(500,300))
    Cropped = cv2.resize(Cropped,(400,200))
    cv2.imshow('car',car)
    cv2.imshow('Cropped',Cropped)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return text



        
      
def dialog():##for selecting image from image data set
    filename = filedialog.askopenfilename(initialdir="tkinter\main",title="Select a file", filetypes=(("jpg file","*.jpg"),("png files","*.png"),("jpg file","*.jpg")))
    text=imgrec(filename)
    vno_e.insert(0,str(text))


def write_to_csv(result):
    print("Function Called")
    with open('datarecord.csv','a',newline='',encoding="utf-8")as f:
        w=csv.writer(f,dialect='excel')
        for record in result:
            w.writerow(record)

def set_date_time():
    #Sets Date and Time
    global now
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date=now.strftime("%d/%m/%Y")
    print("Current Time =", current_time)
    print("Current date =", current_date)
    sdate_e.insert(0,str(current_date))
    stime_e.insert(0,str(current_time))


root=Tk()
root.geometry("700x500")
root.title("Parkify")
root.iconbitmap('tkinter\main\car_logo_copy_recovered_Sb1_icon.ico')




#DATABASES
#Create a database
conn=sqlite3.connect('Parkingrecord.db')

#creat curcor
c=conn.cursor()

#create Table

# c.execute("""
#             CREATE TABLE records(
#                 name text,
#                 age integer,
#                 pno integer,
#                 stime text,
#                 sdate text,
#                 etime text,
#                 edate text,
#                 vmanu text,
#                 vno text,
#                 space integer,
#                 duration REAL,
#                 amount REAL  
#             ) """)


def final():#Makes final update to Database
    conn=sqlite3.connect('Parkingrecord.db')
    
    c=conn.cursor()
    record_id=rem_e.get()
    c.execute("""UPDATE records SET
                name=:name,
                age=:age,
                pno=:pno,
                stime=:stime,
                sdate=:sdate,
                etime=:etime,
                edate=:edate,
                vmanu=:vmanu,
                vno=:vno,
                space=:space,
                duration=:duration,
                amount=:amount

                WHERE oid= :oid""",
                {   'name':name_r.get(),
                    'age':age_r.get(),
                    'pno':pno_r.get(),
                    'stime': stime_r.get(),
                    'sdate': sdate_r.get(),
                    'etime' : etime_r.get(),
                    'edate' : edate_r.get(),
                    'vmanu': vmanu_r.get(),
                    'vno': vno_r.get(),
                    'space': space_r.get(),
                    'duration': duration_r.get(),
                    'amount': amount_r.get(),
                    'oid':rem_e.get()    
                })
    c.execute(" SELECT * FROM records WHERE oid="+ record_id) 
    result=c.fetchall()
    write_to_csv(result)

    
    conn.commit()

    conn.close()


def showrec():#Show all records that are present in the database
    rec=Tk()
    rec.title(" --Parking Records-- ")
    root.iconbitmap('tkinter\main\car_logo_copy_recovered_Sb1_icon.ico')
    conn=sqlite3.connect('Parkingrecord.db')

    c=conn.cursor()

    c.execute("SELECT *,OID FROM records")
    datas=c.fetchall()
     
    #loop Through Results

    show_rec=''
    for data in datas:
        show_rec+=str(data) + "\n"
    rec_label=Label(rec,text=show_rec)
    rec_label.pack()

    
    conn.commit()

    conn.close()

def delete(a):#Delete A record from database using unique Identity
    conn=sqlite3.connect('Parkingrecord.db')

    c=conn.cursor()

    c.execute("DELETE FROM records WHERE oid=" + a)
    
    conn.commit()

    conn.close()

def delt():#Get unique Id of the record to be delete
     det = Tk()
     det.title("DELETE RECORD")
     root.iconbitmap('tkinter\main\car_logo_copy_recovered_Sb1_icon.ico')
     btn=Button(det,text="Delete",command=lambda:delete(rem_e.get()))
     btn.grid(row=1,column=0,columnspan=2,padx=10,pady=10)
     
     rem_e=Entry(det,width=10)
     rem_e.grid(row=0,column=1,padx=10)
     rem=Label(det,text="ENTER UNIQUE ID :")
     rem.grid(row=0,column=0 , padx=10)
         
def retrive(b):#Does final calculation for duration, bill
    
    toot=Tk()
    toot.title("Exit Entry")
    toot.geometry("800x600")
    root.iconbitmap('tkinter\main\car_logo_copy_recovered_Sb1_icon.ico')

    conn=sqlite3.connect('Parkingrecord.db')

    c=conn.cursor()

    c.execute("SELECT * FROM records WHERE oid=" + b)
    info=c.fetchall()

    name=Label(toot,text="Name:")
    name.grid(row=1,column=0,padx=20)

    age=Label(toot,text="Age:")
    age.grid(row=2,column=0,padx=20)

    pno=Label(toot,text="Phone no.:")
    pno.grid(row=3,column=0,padx=20)

    sdate=Label(toot,text="Entry Date:")
    sdate.grid(row=4,column=0,padx=20)

    stime=Label(toot,text="Entry time:")
    stime.grid(row=5,column=0,padx=20)

    edate=Label(toot,text="Exit Date:")
    edate.grid(row=6,column=0,padx=20)

    etime=Label(toot,text="Exit time.:")
    etime.grid(row=7,column=0,padx=20)

    vmanu=Label(toot,text="Vehicle Manufacturer:")
    vmanu.grid(row=8,column=0,padx=20)

    vno=Label(toot,text="Vehicle No.:")
    vno.grid(row=9,column=0,padx=20)

    space=Label(toot,text="Parking Space:")
    space.grid(row=10,column=0)
    
    #Two new entries that we calculate
    duration=Label(toot,text="Duration:")
    duration.grid(row=11,column=0,padx=(10,0))

    amount =Label(toot,text="Bill:")
    amount.grid(row=12,column=0)

    global name_r
    global age_r
    global pno_r
    global sdate_r
    global stime_r
    global edate_r
    global etime_r
    global vmanu_r
    global vno_r
    global space_r
    global duration_r
    global amount_r
    
    #entry Fields
    name_r=Entry(toot,width=30)
    name_r.grid(row=1,column=1,padx=20)

    age_r=Entry(toot,width=30)
    age_r.grid(row=2,column=1,padx=20)

    pno_r=Entry(toot,width=30)
    pno_r.grid(row=3,column=1,padx=20)

    sdate_r=Entry(toot,width=30)
    sdate_r.grid(row=4,column=1,padx=20)

    stime_r=Entry(toot,width=30)
    stime_r.grid(row=5,column=1,padx=20)

    edate_r=Entry(toot,width=30)
    edate_r.grid(row=6,column=1,padx=20)

    etime_r=Entry(toot,width=30)
    etime_r.grid(row=7,column=1,padx=20)

    vmanu_r=Entry(toot,width=30)
    vmanu_r.grid(row=8,column=1,padx=20)

    vno_r=Entry(toot,width=30)
    vno_r.grid(row=9,column=1,padx=20)

    space_r=Entry(toot,width=30)
    space_r.grid(row=10,column=1,padx=20)

    duration_r=Entry(toot,width=30)
    duration_r.grid(row=11,column=1,padx=20)

    amount_r=Entry(toot,width=30)
    amount_r.grid(row=12,column=1,padx=20)

   


    #Sets Date and Time
    global when
    when = datetime.now()
    current_time = when.strftime("%H:%M")
    current_date=when.strftime("%d/%m/%Y")
    print("Current Time =", current_time)
    print("Current date =", current_date)
 
    edate_r.insert(0,current_date)
    etime_r.insert(0,current_time)


    
    for dat in info:
        name_r.insert(0,dat[0])
        age_r.insert(0,dat[1])
        pno_r.insert(0,dat[2])
        sdate_r.insert(0,dat[3])
        stime_r.insert(0,dat[4])
        vmanu_r.insert(0,dat[7])
        vno_r.insert(0,dat[8])
        space_r.insert(0,dat[9])


    print(when)

    def cal_fee(duration):
        base_fee = 5
        amount = base_fee + 1*duration
        return amount
    k=datetime.combine(datetime.strptime(sdate_r.get(),'%d/%m/%Y'),datetime.strptime(stime_r.get(),'%H:%M').time())
    #now=datetime.strptime(k,'%Y-%m-%d %H:%M')
    

    dur=(when-k).total_seconds()/60.0
    dur=round(dur,2)
    am=cal_fee(dur)
    print(dur)
    print("Total fee =",am)
    am=round(am,2)
    
    duration_r.insert(0,str(dur)+" "+"minutes")
    amount_r.insert(0,str(am))

    save=Button(toot,text="SAVE",command=final())
    save.grid(row=16,column=0,columnspan=2)

    
    conn.commit()

    conn.close()


def retr():#get unique Id for record to calculate Bill
    det = Tk()
    det.title("Leaving Entry")
    root.iconbitmap('tkinter\main\car_logo_copy_recovered_Sb1_icon.ico')
    global rem_e
    rem_e=Entry(det,width=10)
    rem_e.grid(row=0,column=1,padx=10)
    rem=Label(det,text="ENTER UNIQUE ID :")
    rem.grid(row=0,column=0 , padx=10)
    btn=Button(det,text="Proceed",command=lambda:retrive(rem_e.get()))
    btn.grid(row=1,column=0,columnspan=2,padx=10,pady=10)
     
def submit():#Submit the Entry to Database
    
    # now = datetime.now()
    # current_time = now.strftime("%H:%M")
    # print("Current Time =", current_time)

    
        
    duration_e.insert(0,0.0)
    amount_e.insert(0,0.0)


    conn=sqlite3.connect('Parkingrecord.db')

    c=conn.cursor()

    #insert into Tables
    c.execute("INSERT INTO records VALUES(:name,:age,:pno,:sdate,:stime,:edate,:etime,:vmanu,:vno,:space,:duration,:amount)",
        {
                'name': name_e.get(),
                'age': age_e.get(),
                'pno': pno_e.get(),
                'sdate':sdate_e.get(),
                'stime':stime_e.get(),
                'edate':edate_e.get(),
                'etime':etime_e.get(),
                'vmanu': vmanu_e.get(),
                'vno': vno_e.get(),
                'space':space_e.get(),
                'duration':duration_e.get(),
                'amount':amount_e.get()


        }
       

    
    )
    c.execute("SELECT MAX(oid) from records")
    uid=c.fetchone()
    for x in uid:
        k=("Unique ID="+str(x))
    

    conn.commit()

    conn.close()
    messagebox.showinfo("Note Your Unique ID",message=(k))

    name_e.delete(0,END)
    age_e.delete(0,END)
    pno_e.delete(0,END)
    sdate_e.delete(0,END)
    stime_e.delete(0,END)
    set_date_time()
    vmanu_e.delete(0,END)
    vno_e.delete(0,END)
    space_e.delete(0,END)

#label
name=Label(root,text="Name:")
name.grid(row=1,column=0,padx=20,pady=10)

age=Label(root,text="Age:")
age.grid(row=2,column=0,padx=20,pady=10)

pno=Label(root,text="Phone no.:")
pno.grid(row=3,column=0,padx=20,pady=10)

sdate=Label(root,text="Entry Date:")
sdate.grid(row=4,column=0,padx=20,pady=10)

stime=Label(root,text="Entry time:")
stime.grid(row=5,column=0,padx=20,pady=10)

# edate=Label(root,text="Exit Date:")
# edate.grid(row=6,column=0,padx=20,pady=10)

# etime=Label(root,text="Exit time.:")
# etime.grid(row=7,column=0,padx=20,pady=10)

vmanu=Label(root,text="Vehicle Manufacturer:")
vmanu.grid(row=6,column=0,padx=20,pady=10)

vno=Label(root,text="Vehicle No.:")
vno.grid(row=7,column=0,padx=20,pady=10)

space=Label(root,text="Parking Space:")
space.grid(row=8,column=0)

#entry Fields
name_e=Entry(root,width=30)
name_e.grid(row=1,column=1,padx=20,pady=10)

age_e=Entry(root,width=30)
age_e.grid(row=2,column=1,padx=20,pady=10)

pno_e=Entry(root,width=30)
pno_e.grid(row=3,column=1,padx=20,pady=10)

sdate_e=Entry(root,width=30)
sdate_e.grid(row=4,column=1,padx=20,pady=10)

stime_e=Entry(root,width=30)
stime_e.grid(row=5,column=1,padx=20,pady=10)

edate_e=Entry(root,width=30)
# edate_e.grid(row=6,column=1,padx=20,pady=10)

etime_e=Entry(root,width=30)
# etime_e.grid(row=7,column=1,padx=20,pady=10)

vmanu_e=Entry(root,width=30)
vmanu_e.grid(row=6,column=1,padx=20,pady=10)

vno_e=Entry(root,width=30)
vno_e.grid(row=7,column=1,padx=20,pady=10)

space_e=Entry(root,width=30)
space_e.grid(row=8,column=1,padx=20,pady=10)

duration_e=Entry(root)
amount_e=Entry(root)

set_date_time()
# #Sets Date and Time
# global now
# now = datetime.now()
# current_time = now.strftime("%H:%M")
# current_date=now.strftime("%d/%m/%Y")
# print("Current Time =", current_time)
# print("Current date =", current_date)
# sdate_e.insert(0,str(current_date))
# stime_e.insert(0,str(current_time))


#buttons
sel=Button(root,text="Select",command=dialog)
sel.grid(row=7,column=2,padx=20,pady=10)

sub=Button(root,text="Submit",command=submit)
sub.grid(row=9,column=0,pady=(20,0),columnspan=2)


srec=Button(root,text="Show all records",command=showrec)
srec.grid(row=10,column=0,pady=10)
ret=Button(root,text="Calculate Bill",padx=10,command=retr)
ret.grid(row=10,column=1,pady=10)
delrec=Button(root,text="Delete Record ",command=delt)
delrec.grid(row=10,column=2,pady=10)

#Commit changes
conn.commit()

#close connection
conn.close()


root.mainloop()

