# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 20:44:30 2020
@author: Maria Lara C (mlaracue), Mengyao Xu (mengyaox) and Lu Zhang (luzhang3)

This is the pop window to ask users if they want to refresh data

Imported by: app.py
"""
from tkinter import *
from tkinter import ttk
import os, datetime

def scrape():
    global answer
    answer = 0
    # print('yes')
    master.destroy()

def cache():
    global answer
    answer = 1
    # print('no')
    master.destroy()
    
def pop_window():
    global master
    old_file = 'previous scraped data.csv'
    lmd = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(r'..\raw-data',old_file)))
    
    master = Tk()
    master.title('New Data?')
    master.geometry('380x100')
    frame = ttk.Frame(master, padding = (3,3,12,12))
    t = Label(frame, text = "Do you want to refresh for the new data?\n Rental listings and restaurants data were last updated on %s. \nWARNING: refresh takes ~4 hours to complete" % lmd.strftime('%b %d, %Y'))
    b1 = ttk.Button(frame, text = 'YES', command = scrape)
    b2 = ttk.Button(frame, text = 'NO', command = cache)
    t.grid(columnspan = 2, row = 0)
    b1.grid(column = 0, row = 1)
    b2.grid(column = 1, row = 1)
    frame.grid(column = 0, row = 0)
    master.mainloop()

# pop_window()
