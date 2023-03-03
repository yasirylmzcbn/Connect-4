# imports
from functools import partial
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import numpy as np
import sqlite3
import os

# variables
lb_table = []
buttons = []
data = [5]*7
clicked = True
count = 0     

# query to create table
create_table = '''CREATE TABLE IF NOT EXISTS leaderboard (
                                        name text PRIMARY KEY,
                                        score INTEGER NOT NULL
                                        );'''

def submit(name1, name2):
    '''Function to submit the names of the players and destroy the login window.'''
    name1 = str(name1.get())
    name2 = str(name2.get())
    root.destroy()

# initialize tkinter window to prompt the users for their names
root = Tk()
root.title('Enter Names')
root.geometry('300x100')
root.configure(bg=('#856ff8'))

name_label = Label(root, text = 'Player 1', font=('calibre',10, 'bold'))
name1 = StringVar()
name_entry = Entry(root,textvariable = name1, font=('calibre',10,'normal'), width=30)

name2_label = Label(root, text = 'Player 2', font = ('calibre',10,'bold'))
name2 = StringVar()
name2_entry = Entry(root, textvariable = name2, font = ('calibre',10,'normal'), width=30)
submit = partial(submit, name1, name2)

sub_btn = Button(root, text = 'Start Game', command = submit)
root.bind('<Return>', lambda event=None: sub_btn.invoke())

name_label.config(bg='#856ff8')
name2_label.config(bg='#856ff8')
sub_btn.config(bg='black', fg='#856ff8')

name_label.grid(row=0,column=0)
name_entry.grid(row=0,column=1)
name2_label.grid(row=1,column=0)
name2_entry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)

root.mainloop()

# launch the main game window
root = Tk()
root.title('Connect 4 - Python Implementation')
root.attributes('-fullscreen', True)
# root.geometry('1920x1080')
root.configure(bg=('#856ff8'))   

# this class creates a table that is suitable to display in tkinter from an array of tuples
class Table:   
    def __init__(self,root):
        # code for creating table
        for i in range(len(lb_table)):
            for j in range(2):
                self.e = Entry(root, justify='center', width=12, bg='black', fg='#856ff8',
                            font=('Arial',16,'bold'))
                self.e.grid(row=i, column=j)
                self.e.insert(END, lb_table[i][j])

def addToDB(n, s):
    '''Adds name n and score s into the sqlite file.'''
    
    # make sure the parameters are the correct variable type
    n = str(n.get())
    s = int(s)
    
    # connect to the database and initialize cursor
    conn = sqlite3.connect('leaderboard.sqlite')
    cursor = conn.cursor()

    # create table
    cursor.execute(create_table)
    
    # see if the name already exists as an entry in the database
    try:
        cursor.execute(f'SELECT score from leaderboard where name = "{n}"')
        cur = cursor.fetchone()
        s += int(cur[0])
    except:
        pass
    
    # insert into the leaderboard and update score
    cursor.execute(f'INSERT OR REPLACE INTO leaderboard (name, score) VALUES ("{n}", {s})')
    cursor.execute(f'UPDATE leaderboard SET score = {s} WHERE name="{n}"')
    
    conn.commit()

def disable_all_buttons():
    for i in buttons:
        for x in i:
            x.config(state = DISABLED)
def enable_all_buttons():
    for i in buttons:
        for x in i:
            x.config(state = NORMAL)

def checkWinner():
    '''Checks to see if there is a winning condition on the board. Called every turn.'''
    board = np.arange(42).reshape(6,7)
    allbut = ''
    
    # add all buttons' text content to a string.
    for r in range(0, 6):
        for c in range(0, 7):
            allbut += buttons[r][c]['text'] # if the button is red, this value will be 'R'
                                            # if yellow: 'Y'
                                            # if empty: ' '

    allbut = [*allbut] # convert the string to a list
    board = np.reshape(allbut, (6,7)) # convert the list to a 6x7 board
    
    # check for horizontal
    for r in board:
        r = ''.join(r)
        if 'RRRR' in r:
            messagebox.showinfo('Connect 4', 'Congratulations!\nRed Wins!')
            addToDB(name1,1)
            disable_all_buttons()
        elif 'YYYY' in r:
            messagebox.showinfo('Connect 4', 'Congratulations!\nYellow Wins!')
            addToDB(name2,1)
            disable_all_buttons()
    
    # check for vertical
    for c in board.T:
        c = ''.join(c)
        if 'RRRR' in c:
            messagebox.showinfo('Connect 4', 'Congratulations!\nRed Wins!')
            addToDB(name1,1)
            disable_all_buttons()
        elif 'YYYY' in c:
            messagebox.showinfo('Connect 4', 'Congratulations!\nYellow Wins!')
            addToDB(name2,1)
            disable_all_buttons()
            
    # check for left to right diagonal
    diag = -2
    while diag <= 3:
        d = ''.join(board.diagonal(diag))
        if 'RRRR' in d:
            messagebox.showinfo('Connect 4', 'Congratulations!\nRed Wins!')
            addToDB(name1,1)
            disable_all_buttons()
        elif 'YYYY' in d:
            messagebox.showinfo('Connect 4', 'Congratulations!\nYellow Wins!')
            addToDB(name2,1)
            disable_all_buttons()
        diag += 1
        
    # check for right to left diagonal
    diag = -2
    while diag <= 3:
        d = ''.join(np.fliplr(board).diagonal(diag))
        if 'RRRR' in d:
            messagebox.showinfo('Connect 4', 'Congratulations!\nRed Wins!')
            addToDB(name1,1)
            disable_all_buttons()
        elif 'YYYY' in d:
            messagebox.showinfo('Connect 4', 'Congratulations!\nYellow Wins!')
            addToDB(name2,1)
            disable_all_buttons()
        diag += 1
    
    # check for tie
    for t in board:
        if ' ' in t:
            return
    messagebox.showinfo('Connect 4', 'The game has ended in a tie!')
    disable_all_buttons()

def btnClicked(b, row, colum):
    global clicked, count, buttons
    valid = True
    done = False
    # if the button is clicked, animate its column based on which color the button is supposed to be
    if clicked:
        for r in range(6, 0, -1): 
            if (not done) and buttons[r-1][colum]['text'] == ' ':
                done = True
                for bt in range(0, r-1):
                    buttons[bt][colum]['bg'] = 'red'
                    buttons[bt][colum]['highlightbackground'] = 'red'
                    buttons[bt][colum]['text'] = 'R'
                    disable_all_buttons()
                    root.update()
                    buttons[bt][colum].after(1, buttons[bt][colum].config(bg='lightblue'), buttons[bt][colum].config(highlightbackground='lightblue'), buttons[bt][colum].config(text=' '))
                buttons[r-1][colum]['bg'] = 'red'
                buttons[r-1][colum]['highlightbackground'] = 'red'
                buttons[r-1][colum]['text'] = 'R'
        if not done:
            messagebox.showerror("Connect 4", "Can't place there, please try a different spot")
            valid = False
    else:
        done = False
        for r in range(6, 0, -1): 
            if (not done) and buttons[r-1][colum]['text'] == ' ':
                done = True
                for bt in range(0, r-1):
                    buttons[bt][colum]['bg'] = 'yellow'
                    buttons[bt][colum]['highlightbackground'] = 'yellow'
                    buttons[bt][colum]['text'] = 'Y'
                    disable_all_buttons()
                    root.update()
                    buttons[bt][colum].after(1, buttons[bt][colum].config(bg='lightblue'), buttons[bt][colum].config(highlightbackground='lightblue'), buttons[bt][colum].config(text=' '))
                buttons[r-1][colum]['bg'] = 'yellow'
                buttons[r-1][colum]['highlightbackground'] = 'yellow'
                buttons[r-1][colum]['text'] = 'Y'
        if not done:
            messagebox.showerror("Connect 4", "Can't place there, please try a different spot")
            valid = False
    enable_all_buttons()
    
    checkWinner()
    if valid:
        clicked = not clicked

def createButton(r, c, iteration):
    '''Creates a button in the given row and column and return the button'''
    but = Button(root, text = " ", font=('Helvetica', 20), height = 2, width = 8, bg='LightBlue', command=lambda: btnClicked(but, r, c))
    if r == 0:
        if c == 0:
            but.grid(row = iteration-c, column = c, pady=(150,0), padx=(280,0))    
        else:
            but.grid(row = iteration-c, column = c, pady=(150,0))
    if c == 0:
            but.grid(row = iteration-c, column = c, padx=(280,0))    
    else:
        but.grid(row = iteration-c, column = c)
    return but

def reset(): 
    '''Clears the game board and recreates empty buttons'''
    global clicked, count
    clicked = True
    count = 0
    buttons.clear()
    ind = 0
    for r in range(6): #creates all buttons
        arr = []
        for c in range(7):
            but = createButton(r, c, ind)
            ind+=1
            arr.append(but)
        buttons.append(arr)
        
def getLB():
    '''Gets the leaderboard from the sqlite file and orders it by score and assigns it to lb_table'''
    global lb_table
    conn = sqlite3.connect('leaderboard.sqlite')
    cursor = conn.cursor()
    cursor = conn.execute('SELECT * FROM leaderboard ORDER BY score DESC').fetchall()
    lb_table = cursor

def viewLB():
    '''Opens a new window to show the leaderboard'''
    lb = Tk()
    lb.title('Leaderboard')
    lb.geometry('290x560')
    lb.configure(bg=('#856ff8'))
    getLB()
    t = Table(lb)
    lb.mainloop()
    
def viewIns():
    '''Opens a new window to show the leaderboard'''
    os.startfile('instructions.txt')
    
# create menu
my_menu = Menu(root)
root.config(menu = my_menu)

# options
options_menu = Menu(my_menu, tearoff = False)
my_menu.add_cascade(label = 'Options', menu = options_menu)
options_menu.add_command(label = 'Reset Game', command = reset)
options_menu.add_command(label = 'View Leaderboard', command = viewLB)

help_menu = Menu(my_menu, tearoff = False)
my_menu.add_cascade(label = 'Help', menu = help_menu)
help_menu.add_command(label = 'View Instructions', command = viewIns)

reset()

root.mainloop()