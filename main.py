from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
import os
from tkcalendar import DateEntry
import time
import sqlite3


def clear():
    global widget

    for widget in root.winfo_children():

        widget.destroy()


def get_notifs():

    cursor.execute("SELECT * from GOALS")
    goals = cursor.fetchall()
    goal_dict = {}

    for goal in goals:
        if goal[0] != 'Savings':
            
            goal_dict.update({goal[0]:(goal[1])})

        else:
            savings_goal = goal[1]

    expenses = getExpense()
    number_of_records = expenses[5]
    totalExp = 0
    for i in range(number_of_records):
        totalExp += int(expenses[4][i])

    
    exp_dict={}
    
    cursor.execute("SELECT TYPE, AMOUNT from EXPENSES")
    exps = cursor.fetchall()

    for exp in exps:
        if exp[0] in exp_dict.keys():
            
            exp_dict[exp[0]] += (exp[1])
        else:
            exp_dict.update({exp[0]:(exp[1])})
    

    notifs = []

    for category in exp_dict:
        try:
            corres_goal_pair_amt = goal_dict[category]
            
            
            if exp_dict[category] > 3*(corres_goal_pair_amt)/4 :
                notifs.append(category + ' expense crossed 75% of amount alloted to it as per goal.')
        except Exception as e:
            print(e)

    calculateIncome()
    
    
    try:
        if totalExp > 3*(INCOME-savings_goal)/4:
            notifs.insert(0,'Total expense crossed 75% of savings goal amount.')
    except Exception as e:
        print(e)
    
    
    return notifs

def reConfigMenu(button_clicked):

    for widget in menu.winfo_children():
        
        if str(type(widget)) == "<class 'tkinter.Button'>":
            
            if widget != button_clicked:
                widget.configure(bg='#383838',relief='raised')
            else:
                widget.configure(bg='yellow',relief='flat')

def getExpense():

    #expFile = open(os.getcwd()+'\data\expense.txt','r')
    cursor.execute('SELECT * from EXPENSES ORDER by DATE;')
    records = cursor.fetchall()


    dates,types,descriptions,amounts=[],[],[],[]

    '''tot_exp=expFile.readline()          #1st line is the total expense

    expFile.readline()                     #expenses start from 3rd line so omitting 2nd one

    while True:
        if expFile.readline()=='[\n':             #each new record starts with '['
            dates.append(expFile.readline())
            types.append(expFile.readline())
            descriptions.append(expFile.readline())
            amounts.append(expFile.readline())
            expFile.readline()                  #every record ends with ']' so omitting that line
        else:
            break'''

    number_of_records = len(records)
    for record in records:
        dates.append(str(record[0]))
        types.append(record[1])
        descriptions.append(record[2])
        amounts.append(str(record[3]))

    '''for i in range(len(dates)):
            dates[i]=dates[i][:-1]
    for i in range(len(types)):
            types[i]=types[i][:-1]
    for i in range(len(descriptions)):
            descriptions[i]=descriptions[i][:-1]
    for i in range(len(amounts)):
            amounts[i]=amounts[i][:-1]'''

    for i in range(len(descriptions)):
        if len(descriptions[i])>27:
            descriptions[i]=descriptions[i][:28]+'....'

    #expFile.close()
    tot_exp = 3456
    
    return [str(tot_exp),dates,types,descriptions,amounts,number_of_records]
    

def log_expense():

    cont = True
    date_input = cal.get()
    expType = typeVar.get()
    date_split = date_input.split('/')
    date = date_split[0]
    monthInp = date_split[1]
    yearInp = date_split[2]
    desc = descVar.get()

    try:
        amt = str(float(amtVar.get()))
    except:
        messagebox.showerror('Invalid input','Please check the amount input.')
        cont = False
        return
    
    if monthInp != month or yearInp != CurrentYear or expType == 'Select type':
        cont = False
        messagebox.showerror('Invalid input','Please check all the fields are properly filled.')

    if cont == True:

        cursor.execute("INSERT into EXPENSES values('"+date + "','" + expType + "','" + desc + "','" + amt +"');")
        connection.commit()
        messagebox.showinfo('Success','Logged expense.')
        cursor.execute('select * from expenses;')
        print(cursor.fetchall())
        expense_page()

def add_exp_page():

    global cal; global typeVar; global descVar; global amtVar

    clear()
    make_menu()
    show_menu()
    reConfigMenu(eb)

    addFrame = Frame(root)

    typeVar = StringVar()
    descVar = StringVar()
    amtVar = StringVar()
    typeVar.set('Select type')
    
    types = ['Clothes','Food','Groceries','Education','Travel']

    Label(root,text="Add an Expense",font=('Lucida Handwriting',50,'underline'),bg='white',fg='#de430b').place(x=menu_width+use_width/5,y=65)

    Label(addFrame,text='Select date:',font=('Impact',35)).grid(row=1,column=1)
    cal = DateEntry(addFrame, width=10, background='#f0bd26',foreground='black', font=('MV Boli',25), year = int(CurrentYear), month = int(month), date_pattern='d/m/y', borderwidth=2)
    #cal.selection_range('1/2/2020','1/3/2020')
    cal.grid(row=1,column=2)

    Label(addFrame,text='Type:',font=('Impact',35)).grid(row=2,column=1)
    om = OptionMenu(addFrame, typeVar, *types)
    om.configure(font=('MV Boli',35))
    om.grid(row=2,column=2)

    Label(addFrame,text='Description:',font=('Impact',35),pady=10).grid(row=3,column=1)
    Entry(addFrame, textvariable=descVar, font=('MV Boli',35), width=7).grid(row=3,column=2)

    Label(addFrame,text='Amount:',font=('Impact',35),pady=10).grid(row=4,column=1)
    Entry(addFrame, textvariable=amtVar, font=('MV Boli',35), width=7).grid(row=4,column=2)

    crossIcon = ImageTk.PhotoImage(file = "cross.png")
    tickIcon = ImageTk.PhotoImage(file = "tick.png")
    cb = Button(addFrame,image=crossIcon, bg='red', command=expense_page)
    cb.image=crossIcon
    cb.grid(row=5,column=1)
    tb = Button(addFrame, bg='green', image=tickIcon, command=log_expense)
    tb.image=tickIcon
    tb.grid(row=5,column=2)

    addFrame.place(x=550,y=200)
    

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def expense_page():


    clear()
    make_menu()
    show_menu(slide=True)
    reConfigMenu(eb)

    expenses = getExpense()
    number_of_records = expenses[5]
    totalExp = 0
    for i in range(number_of_records):
        totalExp += int(expenses[4][i])

    Label(root,text="Expenditure",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+20,y=25)
    Button(root,text = CurrentMonth+' '+CurrentYear, font=('MV Boli',20),bg='#7e6fd9',fg='white',command=select_monthNyear).place(x=menu_width+20,y=120)
    Label(root,text='Total',font=('Segoe UI Black',40,'underline'),bg='white').place(x=menu_width+500,y=25)
    Label(root,text=totalExp, font=('DUBAI MEDIUM',40),bg='white',fg='red').place(x=menu_width+500,y=100)

    Button(root,text='Add',font=('Roboto',40),bg='Green',fg='white',command=add_exp_page).place(x=menu_width+800,y=35)

    mainFrame = Frame(root,border=3,bg='#4d4949')
    canvas=Canvas(mainFrame,width=930,height=450,bg='white')
    expFrame = Frame(canvas,bg='white')
    
    scrollbar=Scrollbar(mainFrame,command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT,fill=Y)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0,0), window=expFrame, anchor="nw")

    expFrame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    mainFrame.place(x=menu_width+50,y=240)

    
    Label(expFrame,text='DATE',font=('Roboto',25,'underline'),bg='white').grid(row=1,column=1)
    Label(expFrame,text='Type',font=('Roboto',25,'underline'),bg='white').grid(row=1,column=2)
    Label(expFrame,text='Description',font=('Roboto',25,'underline'),bg='white').grid(row=1,column=3)
    Label(expFrame,text='Amount',font=('Roboto',25,'underline'),bg='white').grid(row=1,column=4)
    
    Label(expFrame,text='',font=('Roboto',25),bg='white',padx=10).grid(row=2,column=1)
    Label(expFrame,text='',font=('Papyrus',25),bg='white',fg='green',padx=10).grid(row=2,column=2)
    Label(expFrame,text='',font=('Tahoma',25),bg='white',padx=10).grid(row=2,column=3)
    Label(expFrame,text='',font=('Segoe UI Black',25),bg='white',padx=10).grid(row=2,column=4)

    if number_of_records == 0:
            Label(expFrame,text='NO',font=('Impact',55),bg='white', fg='red').grid(row=2,column=1)
            Label(expFrame,text='RECORDS',font=('Impact',55),bg='white', fg='red').grid(row=3,column=2)
            Label(expFrame,text='FOUND',font=('Impact',55),bg='white', fg='red').grid(row=4,column=3)
            Label(expFrame,text=':(',font=('Impact',55,),bg='white').grid(row=5,column=4)



    for i in range(0,number_of_records):
        Label(expFrame,text=expenses[1][i],font=('Roboto',25),bg='white', fg='#de430b',padx=10).grid(row=i+3,column=1)
        Label(expFrame,text=expenses[2][i],font=('Papyrus',25),bg='white',fg='green',padx=10).grid(row=i+3,column=2)
        Label(expFrame,text=expenses[3][i],font=('Tahoma',25),bg='white', fg='blue', padx=10).grid(row=i+3,column=3)
        Label(expFrame,text=expenses[4][i],font=('Segoe UI Black',25),bg='white',padx=10).grid(row=i+3,column=4)
        binIcon = ImageTk.PhotoImage(file = "b2.png")
        bb = Button(expFrame,bg='red',image=binIcon, command = lambda i=i: delExp(expenses[1][i],expenses[2][i],expenses[3][i],expenses[4][i]))
        bb.image=binIcon
        bb.grid(row=i+3,column=5,sticky='e')


def delExp(dt,tp,des,amt):

    print("DELETE from EXPENSES where (DATE="+dt+") AND (TYPE='"+tp+"') AND (DESCRIPTION='"+des+"') AND (AMOUNT="+amt+");")
    cursor.execute("DELETE from EXPENSES where (DATE="+dt+") AND (TYPE='"+tp+"') AND (DESCRIPTION='"+des+"') AND (AMOUNT="+amt+");")
    connection.commit()
    expense_page()

def calculateLines(filepath):

    file = open(filepath,'r')
    lines = file.readlines()   
    file.close()
    
    return lines

def goals_page():

    clear()
    make_menu()
    show_menu(slide=True)
    reConfigMenu(gb)

    cursor.execute("SELECT * from GOALS;")
    result = cursor.fetchall()

    goal_list = []

    for goal in result:
        if goal[0] == 'Savings':
            '''keeping savings goal first'''
            goal_list.insert(0, "I will save INR " + str(goal[1]) + " from my income this month.")
        else:
            goal_list.append("I will not spend more than INR " + str(goal[1]) + " for " + goal[0] + " this month.")

    violated_goals = AccomplishmentStatus()

    goals_Frame = Frame(root)
    goals_Frame.place(x=550,y=50)
    
    Label(goals_Frame,text='SET NEW',font=('Segoe UI Black',35),bg='orange',padx=10).grid(row=1,column=1,columnspan=2)
    Button(goals_Frame,text='Savings Goals',font=('Segoe UI Black',25),bg='white',padx=10,border=5,command=savings_goal_page).grid(row=2,column=1)
    Button(goals_Frame,text='Expense Goals',font=('Segoe UI Black',25),bg='white',padx=10,border=5,command=expense_goal_page).grid(row=2,column=2)    

    mainFrame = Frame(root,border=3,bg='#4d4949')
    canvas=Canvas(mainFrame,width=950,height=350,bg='white')
    goalsFrame = Frame(canvas,bg='white')
    
    scrollbar=Scrollbar(mainFrame,command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT,fill=Y)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0,0), window=goalsFrame, anchor="nw")

    goalsFrame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    mainFrame.place(x=menu_width+50,y=240)

    Label(goalsFrame,text='No.',font=('Roboto',25,'bold'),bg='#49f72a').grid(row=1,column=1)
    Label(goalsFrame,text='                    Goal                    ',font=('Roboto',25,'bold'),bg='#de540b').grid(row=1,column=2)
    
    Label(goalsFrame,text='',font=('Roboto',25),bg='white',padx=10).grid(row=2,column=1)
    Label(goalsFrame,text='',font=('Papyrus',25),bg='white',fg='green',padx=10).grid(row=2,column=2)
    

    for i in range(0,len(goal_list)):
        Label(goalsFrame,text=str(i+1),font=('Roboto',22),bg='white').grid(row=i+3,column=1)
        print(goal_list[i].split()[9])

        if goal_list[i].split()[2] == 'save' and 'Savings' in violated_goals:
            fontColour = 'red'
        elif goal_list[i].split()[9] in violated_goals:
            fontColour = 'red'
        else:
            fontColour = 'green'
            
        Label(goalsFrame,text=goal_list[i],font=('Ink Free',22),bg='white',fg=fontColour).grid(row=i+3,column=2,sticky='w')
        binIcon = ImageTk.PhotoImage(file = "b2.png")
        bb = Button(goalsFrame,bg='red',image=binIcon, command = lambda i=i: delGoal(goal_list[i]))
        bb.image=binIcon
        bb.grid(row=i+3,column=3,sticky='e')

    Button(root,text = CurrentMonth+' '+CurrentYear, font=('MV Boli',20),bg='#7e6fd9',fg='white',command=select_monthNyear).place(x=menu_width+30,y=630)    


def AccomplishmentStatus():

    cursor.execute("SELECT * from GOALS")
    goals = cursor.fetchall()
    goal_dict = {}

    for goal in goals:
        if goal[0] != 'Savings':
            goal_dict.update({goal[0]:int(goal[1])})
        else:
            savings_goal = goal[1]

    
    exp_dict={}
    
    cursor.execute("SELECT TYPE, AMOUNT from EXPENSES")
    exps = cursor.fetchall()

    for exp in exps:
        if exp[0] in exp_dict.keys():
            
            exp_dict[exp[0]] += int(exp[1])
        else:
            exp_dict.update({exp[0]:int(exp[1])})

    violated = []

    for category in exp_dict:
        try:
            corres_goal_pair_amt = goal_dict[category]
            print(exp_dict[category])
            print(corres_goal_pair_amt)
            print(3*(corres_goal_pair_amt)/4)
            
            if exp_dict[category] > corres_goal_pair_amt :
                violated.append(category)
        except Exception as e:
            print(e)

    calculateIncome()
    print('income',INCOME)
    print(INCOME-savings_goal)
    
    expenses = getExpense()
    number_of_records = expenses[5]
    totalExp = 0
    for i in range(number_of_records):
        totalExp += int(expenses[4][i])
    print(totalExp)
    try:
        if totalExp > (INCOME-savings_goal):
            violated.append('Savings')
    except Exception as e:
        print(e)
    print(violated)
    
    
    return violated


def delGoal(statement):

    if 'I will save' in statement:
        cursor.execute("DELETE from GOALS where (TYPE = 'Savings');")
        connection.commit()
        goals_page()
    else:
        words = statement.split()
        typ = words[9]
        cursor.execute("DELETE from GOALS where (TYPE = '"+typ+"');")
        connection.commit()
        goals_page()
        


def commitGoal(goalType):

    limit = goalInt_input.get()
    if limit.isdigit():
        
            cursor.execute('SELECT TYPE from GOALS;')
            loggedTypes = cursor.fetchall()
            for typ in loggedTypes:
                if typ[0] == goalType:
                    messagebox.showerror('Goal is already set !', goalType + ' goal is already set! Delete the goal to set new one.')
                    return


            cursor.execute("INSERT into GOALS values('"+goalType+"', '"+limit+"');")
            connection.commit()
            messagebox.showinfo('Committed', 'Great! You successfully logged your goal')
            cursor.execute('SELECT * from GOALS')
            print(cursor.fetchall())
            goals_page()

    else:
        messagebox.showerror('Invalid input','Please check your input.')
    
'''
def savings_goal_pagePercent():

    global goalInt_input

    clear()
    make_menu()
    show_menu()
    reConfigMenu(gb)

    goalInt_input = StringVar()
    
    checkBtn = Radiobutton(root,text='Set by %',variable=typeVar,value=1,font=('arial',20),command=savings_goal_page)
    checkBtn.place(x=600,y=0)    

    Label(root,text="I will Save",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/7,y=135)
    Entry(root,textvariable=goalInt_input,font=('Segoe UI Black',50),borderwidth=7,width=3).place(x=menu_width+use_width/3,y=225)
    Label(root,text="%",font=('DUBAI MEDIUM',60),bg='white').place(x=menu_width+use_width/2.1,y=225)
    Label(root,text='of my income this month.',font=('MV Boli',35,'bold'),bg='white').place(x=(menu_width+use_width/12.5)+130,y=405)
    Button(root,text='Commit',font=('MV Boli',20,'bold'),bg='orange', command = lambda: commitGoal('Savings%')).place(x=menu_width+use_width/1.9,y=620)
'''

def savings_goal_page():

    global typeVar; global goalInt_input

    cursor.execute('SELECT TYPE from GOALS;')
    loggedTypes = cursor.fetchall()
    for typ in loggedTypes:
        if typ[0] == 'Savings':
            messagebox.showerror('Goal is already set !', 'Savings goal is already set! Delete the goal to set new one.')
            return

    clear()
    make_menu()
    show_menu()
    reConfigMenu(gb)

    goalInt_input = StringVar()
    typeVar = IntVar()
    #checkBtn = Radiobutton(root,text='Set by %',variable=typeVar,font=('arial',20),command=savings_goal_pagePercent)
    #checkBtn.place(x=600,y=0)

    
    Label(root,text="I will Save",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/7,y=135)
    Label(root,text="INR",font=('DUBAI MEDIUM',60),bg='white').place(x=menu_width+use_width/3,y=245)
    Label(root,text='from my income this month.',font=('MV Boli',35,'bold'),bg='white').place(x=menu_width+use_width/3,y=460)
    Entry(root,textvariable=goalInt_input,font=('Segoe UI Black',50),borderwidth=7,width=7).place(x=(menu_width+use_width/3)+150,y=245)
    Button(root,text='Commit',font=('MV Boli',20,'bold'),bg='orange', command = lambda: commitGoal('Savings')).place(x=menu_width+use_width/1.9,y=620)

def expense_goal_page():

    global goalInt_input

    clear()
    make_menu()
    show_menu()
    reConfigMenu(gb)

    goalInt_input = StringVar()
    typeVar = StringVar()
    typeVar.set('Select type')
    types = ['Clothes','Food','Groceries','Education','Travel']

    exp_goal_frame = Frame(root)

    Label(exp_goal_frame,text='I will not spend more than',font=('Bahnschrift',30,'bold')).grid(row=1,column=1,columnspan=2)
    Label(exp_goal_frame,text='INR',font=('Constantania',30),fg='green').grid(row=2,column=1,sticky=E)
    Entry(exp_goal_frame,textvariable=goalInt_input,font=('Ebrima',27),width=6).grid(row=2,column=2,sticky=W)
    Label(exp_goal_frame,text='behind',font=('Bahnschrift',30,'bold')).grid(row=3,column=1,sticky=E)
    om = OptionMenu(exp_goal_frame, typeVar, *types)
    om.configure(font=('MV Boli',30))
    om.grid(row=3,column=2,sticky=W)
    Label(exp_goal_frame,text='from my income',font=('Bahnschrift',30,'bold')).grid(row=4,column=1,columnspan=2)
    Label(exp_goal_frame,text='this month.',font=('Bahnschrift',30,'bold')).grid(row=5,column=1,columnspan=2)
    crossIcon = ImageTk.PhotoImage(file = "cross.png")
    tickIcon = ImageTk.PhotoImage(file = "tick.png")
    cb = Button(exp_goal_frame,image=crossIcon, command=goals_page)
    cb.image=crossIcon
    cb.grid(row=6,column=1)
    tb = Button(exp_goal_frame,image=tickIcon, command = lambda: commitGoal(typeVar.get()))
    tb.image=tickIcon
    tb.grid(row=6,column=2)

    exp_goal_frame.place(x=550,y=200)

def calculateIncome():

    global INCOME

    cursor.execute("SELECT * from INCOME")
    read_income = cursor.fetchall()

    if read_income != []:
        INCOME = read_income[0][0]
    else:
        INCOME = 'not set'

def income_page():

    

    clear()
    make_menu()
    show_menu(slide=True)
    reConfigMenu(ib)

    calculateIncome()

    if INCOME != 'not set':

        

        Label(root,text="You have set this month's income as",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/7,y=135)
        Label(root,text="INR " + str(INCOME), font=('DUBAI MEDIUM',60),bg='white').place(x=menu_width+use_width/3,y=205)
        Button(root,text='Change',font=('MV Boli',20,'bold'),bg='orange',command=change_income_page).place(x=menu_width+use_width/1.9,y=495)
        Button(root,text = CurrentMonth+' '+CurrentYear, font=('MV Boli',20),bg='#7e6fd9',fg='white',command=select_monthNyear).place(x=menu_width+30,y=630)
        
    else:
        change_income_page()

def set_income():

    value = income_input.get()
    if value.isdigit() :
        cursor.execute("DELETE from INCOME where INCOME = '1' or '1';")       #deleting any previous record    
        cursor.execute('INSERT into INCOME values('+value+');')
        connection.commit()
        messagebox.showinfo('Success','New income value is set.')
        income_page()
    else:
        messagebox.showerror('Invalid input','Please check the input.')

def change_income_page():

    global income_input

    clear()
    make_menu()
    show_menu()
    reConfigMenu(ib)

    income_input = StringVar()
    
    Label(root,text="Set Income for",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/7,y=135)
    Label(root,text = CurrentMonth+' '+CurrentYear ,font=('DUBAI MEDIUM',60),bg='white').place(x=menu_width+use_width/3,y=205)
    Label(root,text='INR',font=('Segoe UI Black',50),bg='white',fg='red').place(x=menu_width+use_width/12.5,y=405)
    Entry(root,textvariable=income_input,font=('Segoe UI Black',50),borderwidth=7,width=10).place(x=(menu_width+use_width/12.5)+130,y=405)
    Button(root,text='Commit',font=('MV Boli',20,'bold'),bg='orange', command = set_income).place(x=menu_width+use_width/1.9,y=555)
    
def savings_page():

    global savings

    clear()
    make_menu()
    show_menu(slide=True)
    reConfigMenu(sb)

    cursor.execute("SELECT * from INCOME")
    read_income = cursor.fetchall()

    if read_income == []:
        income_set = False
    else:
        income_set = True

    if income_set == True:

        expenses = getExpense()
        number_of_records = expenses[5]
        totalExp = 0
        for i in range(number_of_records):
            totalExp += int(expenses[4][i])

        savings = int(read_income[0][0]) - totalExp

        if savings < 0:
            savings_colour = 'red'
        else:
            savings_colour = '#1d9106'

        Label(root,text="AS OF TODAY you have",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/7,y=135)
        Label(root,text="INR "+str(savings), font=('DUBAI MEDIUM',60),bg='white',fg=savings_colour).place(x=menu_width+use_width/3,y=235)
        Label(root,text="in your savings this month.",font=('DUBAI MEDIUM',40),bg='white').place(x=menu_width+use_width/4,y=345)
        Button(root,text = CurrentMonth+' '+CurrentYear, font=('MV Boli',20),bg='#7e6fd9',fg='white',command=select_monthNyear).place(x=menu_width+30,y=630)
        
    else:
        messagebox.showinfo('Income is not set !', 'Please set the income for the month to calculate savings.')
        change_income_page()

    


def setPeriod():

    global connection; global cursor; global CurrentMonth; global CurrentYear; global month

    monthIn = monthVar.get()
    yearIn = yearVar.get()

    if monthIn.isdigit() and yearIn.isdigit():
        
        while monthIn[0]=='0':
            monthIn = monthIn[1:]
        while yearIn[0]=='0':
            yearIn = yearIn[1:]

        month = monthIn                 #declaring month so as to use it further in programme
        
        dbNAME = month + '_' + yearIn + '.db'

        connection = sqlite3.connect(os.getcwd()+'\\data\\'+dbNAME)
        cursor = connection.cursor()

        messagebox.showinfo('Success','Budgeting month and year are set!')
        make_tables()
        CurrentMonth = months[month]
        CurrentYear = yearIn
        cookie = open(os.getcwd()+r'\data\cookie.txt','w')
        cookie.write(month + '_' + yearIn)
        cookie.close()
        home_page()
    else:
        messagebox.showerror('Invalid input','Please check the input.')

def select_monthNyear():

    global monthVar; global yearVar

    clear()
    
    Label(root,text='Change month and year',font=('arial',55),bg='white').place(x=use_width/3.5,y=10)

    mny = Frame(root)

    monthVar = StringVar()
    yearVar = StringVar()

    Label(mny,text='Month:',font=('Impact',35),pady=10).grid(row=1,column=1)
    Entry(mny, textvariable=monthVar, font=('MV Boli',35), width=2, border=4).grid(row=1,column=2)

    Label(mny,text='Year:',font=('Impact',35),pady=10).grid(row=2,column=1)
    Entry(mny, textvariable=yearVar, font=('MV Boli',35), width=4, border=4).grid(row=2,column=2)

    crossIcon = ImageTk.PhotoImage(file = "cross.png")
    tickIcon = ImageTk.PhotoImage(file = "tick.png")
    cb = Button(mny,image=crossIcon, bg='red', command=home_page)
    cb.image=crossIcon
    cb.grid(row=3,column=1)
    tb = Button(mny, bg='green', image=tickIcon, command=setPeriod)
    tb.image=tickIcon
    tb.grid(row=3,column=2)

    mny.place(x=550,y=200)


def home_page():
    global nameLabel
    
    clear()
    make_menu()
    show_menu(slide=True)
    reConfigMenu(hb)

    Label(root,text='name of software',font=('arial',65),bg='white').place(x=menu_width+use_width/4.25,y=10)
    Label(root,text='HOUSEHOLD BUDGET MANAGEMENT SYSTEM',font=('DUBAI MEDIUM',25),bg='white').place(x=menu_width+use_width/4,y=95)
    Label(root,text='KEEP AN EYE HERE...',bg='white',fg='red',font=('MS Reference Sans Serif',22)).place(x=menu_width+50,y=230)   

    notifications = get_notifs()
    noti_frame=Frame(root)

    listbox=Listbox(noti_frame)
    scrollbar=Scrollbar(noti_frame)
    scrollbar.pack(side=RIGHT,fill=Y,expand=N)

    if len(notifications) == 0:
        listbox.insert(0,'      ')
        listbox.insert(1,'                 ')
        
        listbox.insert(2,'                   nothing')
        listbox.insert(3,'                              much')
        listbox.insert(4,'                                      important')
        listbox.insert(5,'                                                  currently')

    else:
        n=1
        for i in range(len(notifications)):
            listbox.insert(n,str(i+1)+') '+notifications[i])
            n+=1
            listbox.insert(n,'----------------------------------------------------')
            n+=1

    listbox.config(yscrollcommand=scrollbar.set,width=50,height=8,bg='#49f72a',font=('Segoe UI',22,'bold'))
    scrollbar.config(command=listbox.yview)
    listbox.pack()
    noti_frame.place(x=menu_width+50,y=270)

    Button(root,text = CurrentMonth+' '+CurrentYear, font=('MV Boli',20),bg='#7e6fd9',fg='white',command=select_monthNyear).place(x=menu_width+30,y=630)
    nameImage = ImageTk.PhotoImage(file = "name.png")
    nameLabel = Label(root,image=nameImage,bg='white')
    nameLabel.image = nameImage

def show_name():
    
    x=1
    while x>0.5:
        nameLabel.place(relx=x,rely=0.9)
        root.update()
        x-=0.001
        
    root.after(8000,hide_name)

def hide_name():
    global sn_btn
    
    x=0.6

    try:
        while x<1.1:
            nameLabel.place(relx=x,rely=0.9)
            root.update()
            x+=0.001
    except:
        pass

def make_menu():
    global menu;global hb;global ib;global eb;global sb;global gb;global vb;global menu_children_ids
    menu = Frame(root)
    menu.configure(bg='#383838')


    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    homeIcon = ImageTk.PhotoImage(file = "homeIcon.png")
    hb=Button(menu,image=homeIcon,bg='#383838',command=home_page)
    hb.image=homeIcon
    
    hb.pack()
    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    incomeIcon = ImageTk.PhotoImage(file = "incomeIcon.png")
    ib=Button(menu,image=incomeIcon,bg='#383838',command=income_page)
    ib.image=incomeIcon
    ib.pack()
    
    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    expensesIcon = ImageTk.PhotoImage(file = "expensesIcon.png")
    eb=Button(menu,image=expensesIcon,bg='#383838',command=expense_page)
    eb.image=expensesIcon
    eb.pack()
    
    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    savingsIcon = ImageTk.PhotoImage(file = "savingsIcon.png")
    sb=Button(menu,image=savingsIcon,bg='#383838',command=savings_page)
    sb.image=savingsIcon
    sb.pack()

    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    goalsIcon = ImageTk.PhotoImage(file = "goalsIcon.png")
    gb=Button(menu,image=goalsIcon,bg='#383838',command = goals_page)
    gb.image=goalsIcon
    gb.pack()

    Label(menu,text='',font=('arial',20),bg='#383838').pack()
    visualisationsIcon = ImageTk.PhotoImage(file = "visualisationsIcon.png")
    vb=Button(menu,image=visualisationsIcon,bg='#383838')
    vb.image=visualisationsIcon
    vb.pack()

    Label(menu,text='',font=('arial',100),bg='#383838').pack()
        

    #menu.place(x=0,y=0)
    menu_children_ids = []
    menu_children = menu.winfo_children()
    menu_widgets=[]

    for widget in menu_children:
        menu_children_ids.append(id(widget))

        
def show_menu(slide=False):

    if slide == True:
        mx=-330
        while mx<0:
            mx+=3
            menu.place(x=mx,y=0)
            root.update()

    else:
        menu.place(x=0,y=0)


def hide_menu():

    mx=0
    while mx>-330:
        mx-=3
        menu.place(x=mx,y=0)
        root.update()
    smb = Button(root,text='show menu',command=show_menu).place(x=0,y=0)

def establish_connection():

    global cursor; global connection; global CurrentMonth; global CurrentYear; global month

    cookie = open(os.getcwd()+r'\data\cookie.txt')
    content = cookie.read()
    cookie.close()
    
    dbName = content + '.db'

    connection = sqlite3.connect(os.getcwd()+"\\data\\"+dbName)
    cursor = connection.cursor()
    make_tables()

    date_split = content.split('_')
    month = date_split[0]
    CurrentMonth = months[date_split[0]]
    CurrentYear = date_split[1]

def make_tables():

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if ('INCOME',) not in tables:
        cursor.execute("Create table INCOME (INCOME int)")
        cursor.execute("Create table EXPENSES (DATE int, TYPE char(20), DESCRIPTION char(35), AMOUNT int)")
        cursor.execute("Create table GOALS (TYPE char(20), upperLIMIT int)")
        cursor.execute("Create table NOTIFICATIONS (NOTIFS CHAR(30))")
        connection.commit()
        

if __name__=='__main__':

    root = Tk()
    root.state('zoomed')
    root.configure(bg='white')

    width=root.winfo_screenwidth()
    height=root.winfo_screenheight()
    use_width=width-310
    menu_width=310
    months = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

    make_menu()
    establish_connection()
    home_page()
    show_name()
    
    root.mainloop()
