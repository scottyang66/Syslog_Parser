"""
Date            Ver No.     Author      History
01/29/2018      V0.1        Scott Yang  First version
02/02/2018      V0.2        Scott Yang  Fix bugs
"""

import os
import sys
import re
import pandas as pd
from pandas import ExcelWriter
import glob
from tkinter import filedialog
from tkinter import *
from threading import Thread

#Re-arrangment the data frame
arrange = ["Time", "UeContextId", "CellId", "SC", "Syslog Statement"]

table = {}
log_list = []
write_path = os.getcwd()

def browse_button():
    global filename
    filename = filedialog.askdirectory() #get the .log folder location
    select_path.insert(END, filename)

def result_button():
    output = filedialog.askopenfile(filetypes=(("Template files","*.xlsx"),("All files", "*.*")))
    # Using "Thread" module the GUI thread will not get stuck waiting for the external process to finish.
    t = Thread(target = lambda: os.system(output.name))
    t.start()

def write_file(data, write_path, UEID):  # This funcation is to save the ouptut results in .xlsx files
    output = data[arrange]
    writer = ExcelWriter(write_path + "\\" + "SYSLOG_" + UEID + ".xlsx")
    output.to_excel(writer)
    try:
        writer.save()
    except PermissionError:
        print("Oops! Please check the output .xlsx is close")
        status.insert(END, "Oops! Please make sure the output .xlsx are close..." + '\n')
    #Close file and clear list and table before next run
    writer.close()
    del log_list[:]
    table.clear()
    


def addTable(string):
    # Search target time regex
    table["Time"] = re.search("\<\d+\-\d+\-\w+\:\d+\:\d+\.\w+\>", string).group(0)
    # Search target software component regex
    table["SC"] = re.search("\w+\/\w+\/\w+", string).group(0)
    # Search for UE Context ID regex
    try:
        table["UeContextId"] = re.search(r"ueContextId[^:]*:\D*(\d+)", string).group(1)
    except:
        table["UeContextId"] = "N/A"
    # Search for CELL ID regex
    try:
        table["CellId"] = re.search("cellId[^:]*:\D*(\d+)", string).group(1)
    except:
        table["CellId"] = "N/A"
    # Search for CELL ID regex: There are two different possible styles
    try:
        table["Syslog Statement"] = re.search("(\])+\s([\w\W]+)", string).group(2)
    except:
        table["Syslog Statement"] = re.search("(\>)+\s([\w\W]+)", string).group(2)
    # Add table to dict list
    log_list.append(table.copy())

def syslog_parser():
    #Prepare serach pattern from the GUI input
    UEID = UEID_value.get()
    pattern = "(ueContextId:{} |UeId:{} )".format(UEID,UEID)
    mp = re.compile(pattern)

    print("Start Parsing....")
    status.insert(END,"Start parsing...." + "ID:" + UEID + '\n')
    current_path = filename + "//*.log" #file name is getting from the "browse_button" tk funcation
    write_path = filename   #path for output .xlsx files
    status.insert(END, write_path + '\n')

    for file in glob.glob(current_path):
        #read syslog file from directory
        f = open(file, "r")

        lines = f.readlines()
        for line in lines:
            result = mp.search(line) #Serach based on pattern: All lines contains the input UE context
            if result != None: #If UE founded
                # Add to the log table
                addTable(line)

    print(log_list)
    f.close()
    output = pd.DataFrame(log_list)
    write_file(output, write_path, UEID)
    status.insert(END, "DONE!!!" + '\n')

#### Tk GUI section ######
window = Tk()
window.title("Nokia Syslog Parser")
window.geometry("600x600")


#Button for folder locator
b1=Button(window,text="Browse Syslog *.log", command=browse_button)
b1.grid(row=0,column=0, sticky=W)

#Label for Load location
lable=Label(window,text="Load Location:  ")
lable.grid(row=1,column=0, sticky=W)

#Print folder path
select_path=Text(window,height=1,width=50)
select_path.grid(row=1,column=0, sticky=E)

#Label for PM counter entry
UEID_lable=Label(window,text="UE context ID filter:  ")
UEID_lable.grid(row=2,column=0, sticky=W)

#Print PM filter
UEID_value=StringVar()
UEID_Filter=Entry(window,textvariable=UEID_value)
UEID_Filter.grid(row=2,column=0, sticky=E)
UEID_Filter.insert(END,"")


#Run button
b1=Button(window,text="Run", command = syslog_parser)
b1.grid(row=3,column=0, sticky=W)

#Status
status=Text(window,height=25,width=70)
status.grid(row=4,column=0)

#Button for result locator
b1=Button(window,text="Results Folder", command = result_button)
b1.grid(row=21,column=0, sticky=W)

#Button for Exit
b1=Button(window,text="Exit",command = lambda window = window:quit(window))
b1.grid(row=21,column=0)

#Button for About
About_lable=Label(window,text="Created by Scott Yang")
About_lable.grid(row=21,column=0, sticky=E)

window.mainloop()
#### End of Tk GUI section ######