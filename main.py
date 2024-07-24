import random
import sys
import tkinter as tk
from io import BytesIO
from tkinter import messagebox, filedialog
import sqlite3
import io
from PIL import Image,ImageTk
import datetime
class MyDatabase:         #数据库类 包含数据库的操作方法
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        today = datetime.date.today() # 获取当前日期                                  为每日消费的值，进行每日清零操作
        # 检查是否已经执行过清零操作
        self.cursor.execute("SELECT * FROM daily_reset WHERE date = ?", (today,))
        result = self.cursor.fetchone()
        if result is None:# 如果还没有执行过清零操作，执行清零操作
            self.cursor.execute("UPDATE students SET today_pay = 0")
            self.cursor.execute("INSERT INTO daily_reset (date) VALUES (?)", (today,))     # 记录清零操作的日期
            self.conn.commit()
    def get_all_rows(self, table_name):                                                                     #得到数据库所有行的信息
        self.cursor.execute(f'SELECT * FROM {table_name}')
        rows = self.cursor.fetchall()
        return rows
    def get_row_info(self, table_name, row_id):                                                              #得到数据库指定行的信息
        self.cursor.execute(f'SELECT * FROM {table_name}')
        rows = self.cursor.fetchall()
        return rows[row_id]
    def update_row_info(self, table_name, row_id, new_data):                                                  #更新数据库指定行的信息
        set_values = ', '.join(f'{key} = ?' for key in new_data)
        values = tuple(new_data.values())
        self.cursor.execute(f'UPDATE {table_name} SET {set_values} WHERE id = ?', values + (row_id,))
        self.conn.commit()
    def update_row_col_info(self, table_name, row_id, column_name, new_value):                                #更新数据库指定行指定属性的值
        self.cursor.execute(f'UPDATE {table_name} SET {column_name} = ? WHERE id = ?', (new_value, row_id))
        self.conn.commit()
    def add_new_row(self, table_name, new_data):                                                               #添加新行
        # Assuming new_data is a dictionary containing the new row information
        columns = ', '.join(new_data.keys())
        placeholders = ', '.join('?' for _ in new_data)
        values = tuple(new_data.values())
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
        self.conn.commit()
    def add_new_row_top(self, table_name, new_data):                                                           #添加新行至最顶行
        self.cursor.execute(f"CREATE TABLE temp_tab AS SELECT * FROM {table_name} WHERE 0")
        columns = ', '.join(new_data.keys())
        placeholders = ', '.join('?' for _ in new_data)
        values = tuple(new_data.values())
        old_values=db.get_all_rows(table_name)
        self.cursor.execute(f"INSERT INTO temp_tab ({columns}) VALUES ({placeholders})",values)
        for old_value in old_values:
            self.cursor.execute(f"INSERT INTO temp_tab ({columns}) VALUES ({placeholders})", old_value)
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.cursor.execute(f"ALTER TABLE temp_tab RENAME TO {table_name}")
        self.conn.commit()
    def get_column_values(self,table_name, column_name):                                                      #得到数据表所有行指定属性的值
        # 执行查询获取属性的所有值
        self.cursor.execute(f"SELECT {column_name} FROM {table_name}")
        values = [row[0] for row in self.cursor.fetchall()]
        return values
    def get_column_values_where_id(self,table_name,row_id):                                                   #得到数据表指定指定行的指定属性的值
        self.cursor.execute(f"SELECT money, bill_date, b_id,bill_id FROM {table_name} WHERE a_id = '{row_id}'")
        return self.cursor.fetchall()
    def close_connection(self):                                                                               #断开数据库链接
        self.conn.close()
def center_window(window, width, height):                                                                     #使tk界面弹出至屏幕中间
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')
class PinEntry:                                                                                                  #输入密码界面
    def __init__(self,title):
        self.title=title
        self.password=[]
        self.root=tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        self.root.protocol('WM_DELETE_WINDOW', lambda: None)
        center_window(self.root, 300, 420)
        self.pin = ['' for _ in range(6)]  # 用于存储输入的6位数字
        self.pin_display = tk.Label(self.root, text=' '.join(self.pin), font=('Arial', 24))
        self.pin_display.grid(row=0, column=0, columnspan=4)
        self.numbers = [str(i) for i in range(1, 10)] + ['0']  # 数字按钮
        self.buttons = [tk.Button(self.root, text=num, width=27, height=2, command=lambda n=num: self.add_to_pin(n)) for num in self.numbers]
        for i, button in enumerate(self.buttons):
            button.grid(row=i // 3 + 1, column=i % 3, sticky='nsew')
        self.delete_button = tk.Button(self.root, text='删除', width=3, height=2, command=self.delete_pin)
        self.delete_button.grid(row=4, column=1, columnspan=1, sticky='nsew')
        self.enter_button = tk.Button(self.root, text='确定', width=3, height=2, command=self.enter_pin)
        self.enter_button.grid(row=4, column=2, columnspan=1, sticky='nsew')
        self.back_button = tk.Button(self.root, text='退出', width=3, height=1, command=self.back_pin)
        self.back_button.place(x=0,y=0)
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)
    def add_to_pin(self, num):                                                                                   #将输入的数字添加至存储密码的列表中
        for i in range(6):
            if self.pin[i] == '':
                self.pin[i] = num
                break
        self.update_display()
    def delete_pin(self):                                                                                        #将存储密码的列表最后一个元素删除
        for i in range(5, -1, -1):
            if self.pin[i] != '':
                self.pin[i] = ''
                break
        self.update_display()
    def enter_pin(self):                                                                                            #密码输入六位，确认密码
        if self.title=='修改支付密码':                            #传入的密码页面作用为修改密码
            if self.pin[5]!='':
                option=messagebox.askquestion('提示','是否确认修改')
                if option=='yes':
                    for pi in self.pin:
                        self.password.append(pi)
                    self.destory()
                    self.root.quit()
                elif option=='no':
                    return
            else:
                messagebox.showinfo('提示','密码需要6位')
        elif self.title=='输入支付密码':                      #传入的密码页面作用为输入密码用于支付
            if self.pin[5]!='':
                option=messagebox.askquestion('提示','是否确认支付')
                if option=='yes':
                    for pi in self.pin:
                        self.password.append(pi)
                    self.destory()
                    self.root.quit()
                elif option=='no':
                    return
            else:
                messagebox.showinfo('提示','密码需要6位')
        elif self.title=='输入原密码':                    #传入的密码页面作用为输入密码确认原密码
            if self.pin[5]!='':
                for pi in self.pin:
                    self.password.append(pi)
                self.destory()
                self.root.quit()
            else:
                messagebox.showinfo('提示','密码需要6位')
    def back_pin(self):                                                                                              #返回键，破坏界面
        self.destory()
    def update_display(self):                                                                                        #更新展示密码的密码栏，实时显示
        self.pin_display.config(text=' '.join(self.pin))
    def destory(self):
        self.root.destroy()
class Window():        #界面框架 父类
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('校园卡管理系统')
        self.root.resizable(False, False)
        self.root.protocol('WM_DELETE_WINDOW', lambda: sys.exit())
        center_window(self.root, 512, 320)
        # 加载背景图片
        self.image = Image.open("images/bg.jpg")
        self.image = self.image.resize((512, 360))  # 调整背景图片大小
        self.photo = ImageTk.PhotoImage(self.image)  # 加载背景图片
class EditWindow(Window):                                                                           #编辑信息界面
    def __init__(self,index):
        super().__init__()
        self.index=index
        self.parse_data()
        self.my_photo=Image.open(self.my_data_list[7])
        self.my_photo=self.my_photo.resize((120,150))
        self.my_photo = ImageTk.PhotoImage(self.my_photo)
        self.display()
        self.root.mainloop()
    def parse_data(self):                                                                   #解析该用户所有信息存储至一个列表中
        self.my_data_list=list(db.get_row_info('students',self.index))
        self.my_data_list[7]=BytesIO(self.my_data_list[7])
    def display(self):
        def open_folder_and_select_image():                                                  #更换证件照，选择文件夹中图片，并更新存储信息的列表
            image_path = filedialog.askopenfilename(title="Select Image",filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
            if image_path:  # 如果用户选择了图片文件
                    self.my_new_image=Image.open(image_path)
                    self.my_new_image=self.my_new_image.resize((120,150))
                    self.my_new_photo=ImageTk.PhotoImage(self.my_new_image)
                    self.photo.config(image=self.my_new_photo)
                    self.my_data_list[7]=image_path
        def back():                                                                           #返回按键
            option=messagebox.askquestion('提示','是否保存')        #返回时，询问是否保存
            if option=='yes':     #对修改信息的检验:性别格式，姓名格式的检验
                if self.gender.get() == '男' or  self.gender.get()=='女':     #性别 男/女
                    self.my_data_list[6] = self.gender.get()
                else:
                    self.gender.set(self.my_data_list[6])
                    messagebox.showinfo('提示','性别格式错误')
                    return
                if len(self.name.get())<10 and all(c.isalpha() or c.isspace() for c in self.name.get()): #姓名为中文或者英文字母 且长度小于10
                    self.my_data_list[0] = self.name.get()
                else:
                    self.name.set(self.my_data_list[0])
                    messagebox.showinfo('提示','姓名格式错误')
                    return
                if float(self.lim.get())<=999.99:             #限额设置<=999.99
                    self.my_data_list[5] = float(self.lim.get())
                else:
                    self.lim.set(self.my_data_list[5])
                    messagebox.showinfo('提示','限额设置过大')
                    return
                image = Image.open(self.my_data_list[7])    #保存修改的证件照，需要将PIL型图片转化成二进制格式，才能写入数据库
                # 将图片转换为二进制数据
                image_byte_array = io.BytesIO()
                image.save(image_byte_array, format='JPEG')
                image_data = image_byte_array.getvalue()
                new_data = {'name': self.my_data_list[0], 'id': self.my_data_list[1], 'bin': self.my_data_list[2],
                            'balance': self.my_data_list[3], 'admission_data': self.my_data_list[4],
                            'limitation': self.my_data_list[5], 'gender': self.my_data_list[6], 'photo': image_data,
                            'pay_bin': self.my_data_list[8]}
                db.update_row_info('students',self.my_data_list[1],new_data) #更新数据库
                self.root.destroy()
                MangerWindow(self.index)  #返回至管理页面
            else:                         #不保存，不进行任何操作，直接返回至管理页面
                self.root.destroy()
                MangerWindow(self.index)
        def save():                                                                                     #保存操作
            option=messagebox.askquestion('提示','是否保存')    #询问是否对修改进行保存
            if option=='yes':         #对修改信息的检验:性别格式，姓名格式的检验
                if self.gender.get() == '男' or self.gender.get() == '女':                        #性别 男/女
                    self.my_data_list[6] = self.gender.get()
                else:
                    self.gender.set(self.my_data_list[6])
                    messagebox.showinfo('提示', '性别格式错误')
                    return
                if len(self.name.get()) < 10 and all(c.isalpha() or c.isspace() for c in self.name.get()): #姓名为中文或者英文字母 且长度小于10
                    self.my_data_list[0] = self.name.get()
                else:
                    self.name.set(self.my_data_list[0])
                    messagebox.showinfo('提示', '姓名格式错误')
                    return
                if float(self.lim.get()) <= 999.99: #限额设置<=999.99
                    self.my_data_list[5] = float(self.lim.get())
                else:
                    self.lim.set(self.my_data_list[5])
                    messagebox.showinfo('提示', '限额设置过大')
                    return
                image = Image.open(self.my_data_list[7])       #保存修改的证件照，需要将PIL型图片转化成二进制格式，才能写入数据库
                # 将图片转换为二进制数据
                image_byte_array = io.BytesIO()
                image.save(image_byte_array, format='JPEG')
                image_data = image_byte_array.getvalue()
                new_data = {'name': self.my_data_list[0], 'id': self.my_data_list[1], 'bin': self.my_data_list[2],
                            'balance': self.my_data_list[3], 'admission_data': self.my_data_list[4],
                            'limitation': self.my_data_list[5], 'gender': self.my_data_list[6], 'photo': image_data,'pay_bin':self.my_data_list[8]}
                db.update_row_info('students', self.my_data_list[1], new_data) #更新数据库
                self.root.destroy()
                MangerWindow(self.index)
            else:      #不保存，退出，继续进行修改
                return
        def change_bin():                                                           #更改密码按钮触发
            self.root.destroy()
            CBinWindow(self.index)
        def change_bill_bin():                                                     #更改支付密码按钮触发
            pin=PinEntry('输入原密码')
            pin.root.mainloop()
            if int(''.join(pin.password))==self.my_data_list[8]:       #得到输入的原密码与原密码核对是否正确
                messagebox.showinfo('提示','密码正确')
                new_pin=PinEntry('修改支付密码')          #正确，运行修改
                new_pin.root.mainloop()
                self.my_data_list[8]=int(''.join(new_pin.password))
            else:
                messagebox.showinfo('提示','密码错误')  #不正确，继续输入原密码
                change_bill_bin()
        #---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg = tk.Label(self.root, image=self.photo)
        self.bg.image = self.photo
        self.bg.pack()
        self.top_frame=tk.Frame(self.root).pack()
        self.top_label=tk.Label(self.top_frame,text='编辑信息',font='Arial,50',bg='steelblue').place(x=210,y=20)
        self.second_frame=tk.Frame(self.root,bg='steelblue',height=250,width=420).place(x=50,y=50)
        self.third_frame=tk.Frame(self.second_frame,bg='steelblue',height=26,width=420).place(x=51,y=50)
        self.label_name=tk.Label(self.third_frame,height=1,width=15,text=f'HI,{self.my_data_list[0]}',fg='red',font='Arail',bg='steelblue').place(x=50,y=50)
        self.button_edit = tk.Button(self.third_frame, height=1, width=8, text='保存', fg='black', bg='steelblue',relief='sunken', command=save).place(x=345, y=47)
        self.button_back = tk.Button(self.third_frame, height=1, width=8, text='退出', fg='black', bg='steelblue',relief='sunken', command=back).place(x=405, y=47)
        self.photo=tk.Label(self.second_frame,image=self.my_photo)
        self.photo.image=self.my_photo
        self.photo.place(x=70,y=100)
        self.change_photo=tk.Button(self.second_frame,height=1,width=10,text='更改证件照',command=open_folder_and_select_image,bg='royalblue').place(x=90,y=260)
        self.forth_frame=tk.Frame(self.second_frame,height=180,width=250).place(x=200,y=100)
        self.name_label=tk.Label(self.forth_frame,text=f'姓名:',font='Arial,8',anchor='w').place(x=210,y=110)
        self.gender_label=tk.Label(self.forth_frame,text=f'性别:',font='Arial,8',fg='black',anchor='w').place(x=340,y=110)
        self.name=tk.StringVar()
        tk.Entry(self.forth_frame,width=7,textvariable=self.name,font='Arail,8',fg='black').place(x=265,y=110)
        self.name.set(self.my_data_list[0])
        self.gender = tk.StringVar()
        tk.Entry(self.forth_frame, width=3, textvariable=self.gender, font='Arail,8', fg='black').place(x=395, y=110)
        self.gender.set(self.my_data_list[6])
        self.id_label=tk.Label(self.forth_frame,text=f'ID:',font='Arial,8',fg='black',anchor='w').place(x=210,y=140)
        self.id = tk.StringVar()
        tk.Entry(self.forth_frame, width=6, textvariable=self.id, font='Arail,8', fg='black',state='disabled').place(x=250, y=140)
        self.id.set(self.my_data_list[1])
        self.lim_label=tk.Label(self.forth_frame,text=f'每日限额:',font='Arial,8',fg='black',anchor='w').place(x=210,y=170)
        self.lim=tk.StringVar()
        tk.Entry(self.forth_frame,width=6,textvariable=self.lim,font='Arail,8',fg='black').place(x=310,y=170)
        self.lim.set(self.my_data_list[5])
        self.admis_label=tk.Label(self.forth_frame,text=f'入学时间:',font='Arial,8',fg='black',anchor='w').place(x=210,y=200)
        self.admin=tk.StringVar()
        tk.Entry(self.forth_frame,width=12,textvariable=self.admin,font='Arial,8',fg='black',state='disabled').place(x=310,y=200)
        self.admin.set(self.my_data_list[4])
        self.change_bin=tk.Button(self.forth_frame,width=7,height=1,bg='white',fg='black',command=change_bin,text='修改密码').place(x=220,y=230)
        self.change_bill_bin = tk.Button(self.forth_frame, width=10, height=1, bg='white', fg='black', command=change_bill_bin,text='修改支付密码').place(x=310, y=230)
class PayWindow(Window):                                                                 #支付页面
    def __init__(self,index):
        super().__init__()
        self.index = index
        self.parse_data()
        self.display()
        self.root.mainloop()
    def parse_data(self):        #解析数据，将用户的数据存储至一个列表里
        self.my_data_list = list(db.get_row_info('students', self.index))
        self.my_data_list[7] = BytesIO(self.my_data_list[7])
    def display(self):
        def pay():
            money=float(self.pay_money.get())  #读取输入框的数据
            bus_id=int(self.bus_id.get())
            if money > self.my_data_list[3]:     #设置出现余额不足，已达限额，金额为0的消息提示
                messagebox.showinfo('提示', '余额不足')
            elif money + self.my_data_list[9] > self.my_data_list[5]:
                messagebox.showinfo('提示', '已达限额')
            elif money==0:
                messagebox.showinfo('提示','金额不可以为0')
            else:
                if bus_id in range(45101,46000):                        #商家的id有一定设置要求，以45开头的五位数
                    pin=PinEntry('输入支付密码')           #进入输入密码的页面
                    pin.root.mainloop()
                    if int(''.join(pin.password))==self.my_data_list[8]:
                        self.my_data_list[3]=self.my_data_list[3]-money #更新消费后的余额，今日消费情况
                        self.my_data_list[9]=self.my_data_list[9]+money
                        db.update_row_col_info('students',self.my_data_list[1],'balance',self.my_data_list[3])
                        db.update_row_col_info('students', self.my_data_list[1], 'today_pay', self.my_data_list[9])
                        existing_values=db.get_column_values('bill','bill_id')
                        random_id = random.randint(341001, 350000)  # 生成一个1到100之间的随机数   #随机生成账单号
                        while random_id in existing_values:  # 如果随机数已经存在于已有值中，则重新生成
                            random_id = random.randint(3410001, 350000)
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_data={'bill_id':random_id,'a_id':self.my_data_list[1],'b_id':bus_id,'money':money,'bill_date':current_time} #更新消费后的数据库
                        db.add_new_row_top('bill',new_data)      #将最近一次消费的记录添加至账单数据库的顶行
                        messagebox.showinfo('提示','密码正确,已支付')
                        self.root.destroy()
                        MangerWindow(self.index)        #支付成功，返回至管理页面
                    else:
                        messagebox.showinfo('提示','密码错误,请重新输入')
                        pay()
                else:
                    messagebox.showinfo('提示','商家ID不存在')
                    return
        def back():       #返回按钮触发，进入管理页面
            self.root.destroy()
            MangerWindow(self.index)
        # ---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg = tk.Label(self.root, image=self.photo)
        self.bg.image = self.photo
        self.bg.pack()
        self.top_frame = tk.Frame(self.root).pack()
        self.top_label = tk.Label(self.top_frame, text='支付', font='Arial,50', bg='steelblue').place(x=235, y=20)
        self.second_frame = tk.Frame(self.root, bg='steelblue',height=200, width=200).place(x=160, y=55)
        self.bus_label=tk.Label(self.second_frame,text='商家ID:',font='Arail,8',fg='Black',bg='steelblue').place(x=160,y=80)
        self.bus_id=tk.StringVar()
        tk.Entry(self.second_frame,textvariable=self.bus_id,width=10,font='Arial,8',fg='black').place(x=255,y=80)
        self.pay_label = tk.Label(self.second_frame, text='支付金额:', font='Arail,8', fg='Black', bg='steelblue').place(x=160, y=120)
        self.pay_money = tk.StringVar()
        tk.Entry(self.second_frame, textvariable=self.pay_money, width=10, font='Arial,8', fg='black').place(x=255, y=120)
        self.pay_money.set(0.00)
        self.pay_button=tk.Button(self.second_frame,bg='royalblue',fg='black',font='Arial,8',text='确认支付',width=9,command=pay).place(x=210,y=160)
        self.back_button = tk.Button(self.second_frame, bg='royalblue', fg='black', font='Arial,8', text='取消支付',width=9, command=back).place(x=210, y=210)
class RechargeWindow(Window):                                                                       #充值页面
    def __init__(self,index):
        super().__init__()
        self.index = index
        self.parse_data()
        self.display()
        self.root.mainloop()
    def parse_data(self):         #解析数据，将用户的信息存储至列表
        self.my_data_list = list(db.get_row_info('students', self.index))
        self.my_data_list[7] = BytesIO(self.my_data_list[7])
    def display(self):
        def pay():
            money=float(self.pay_money.get())
            if money>999.99:        #设置单次充值限度
                messagebox.showinfo('提示','单次充值过多')
                self.pay_money.set(999.99)
            else:
                pin = PinEntry('输入支付密码')   #输入支付密码
                pin.root.mainloop()
                if int(''.join(pin.password)) == self.my_data_list[8]:
                    self.my_data_list[3] = self.my_data_list[3] + money     #记录充值
                    db.update_row_col_info('students', self.my_data_list[1], 'balance', self.my_data_list[3])  #更新充值之后的余额
                    existing_values = db.get_column_values('bill', 'bill_id')
                    random_id = random.randint(341001, 350000)  # 生成一个1到100之间的随机数   #随机生成账单号
                    while random_id in existing_values:  # 如果随机数已经存在于已有值中，则重新生成
                        random_id = random.randint(3410001, 350000)
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_data = {'bill_id': random_id,'a_id': self.my_data_list[1], 'b_id': '-充值-', 'money':money,  #更新账单数据库，且备注为充值
                                'bill_date': current_time}
                    db.add_new_row_top('bill', new_data)
                    messagebox.showinfo('提示', '密码正确,已支付')
                    self.root.destroy()
                    MangerWindow(self.index)
                else:
                    messagebox.showinfo('提示', '密码错误,请重新输入')
                    pay()
        def back():  #返回，不进行其他操作，进入管理页面
            self.root.destroy()
            MangerWindow(self.index)
         # ---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg = tk.Label(self.root, image=self.photo)
        self.bg.image = self.photo
        self.bg.pack()
        self.top_frame = tk.Frame(self.root).pack()
        self.top_label = tk.Label(self.top_frame, text='充值', font='Arial,50', bg='steelblue').place(x=235, y=20)
        self.second_frame = tk.Frame(self.root, bg='steelblue', height=200, width=200).place(x=160, y=55)
        self.bus_label = tk.Label(self.second_frame, text='我的ID:', font='Arail,8', fg='Black', bg='steelblue').place(x=160,y=80)
        self.bus_id = tk.StringVar()
        tk.Entry(self.second_frame, textvariable=self.bus_id, width=10, font='Arial,8', fg='black',state='disabled').place(x=255,y=80)
        self.bus_id.set(self.my_data_list[1])
        self.pay_label = tk.Label(self.second_frame, text='充值金额:', font='Arail,8', fg='Black',bg='steelblue').place(x=160, y=120)
        self.pay_money = tk.StringVar()
        tk.Entry(self.second_frame, textvariable=self.pay_money, width=10, font='Arial,8', fg='black').place(x=255,y=120)
        self.pay_money.set(0.00)
        self.pay_button = tk.Button(self.second_frame, bg='royalblue', fg='black', font='Arial,8', text='确认充值',width=9, command=pay).place(x=210, y=160)
        self.back_button = tk.Button(self.second_frame, bg='royalblue', fg='black', font='Arial,8', text='取消充值',width=9, command=back).place(x=210, y=210)
class MangerWindow(Window):                        #管理页面
    def __init__(self,index):
        super().__init__()
        self.index=index
        self.parse_data()
        self.my_photo=Image.open(self.my_data_list[7])
        self.my_photo=self.my_photo.resize((120,150))
        self.my_photo = ImageTk.PhotoImage(self.my_photo)  # 加载背景图片
        self.display()
        self.root.mainloop()
    def parse_data(self):
        self.my_data_list=list(db.get_row_info('students',self.index))
        self.my_data_list[7]=BytesIO(self.my_data_list[7])
    def display(self):
        def recharge():
            self.root.destroy()
            RechargeWindow(self.index)
        def edit():
            self.root.destroy()
            EditWindow(self.index)
        def back():
            option=messagebox.askquestion('提示','是否退出登录')
            if option=='yes':
                self.root.destroy()
                MainWindow()
        def pay():
            self.root.destroy()
            PayWindow(self.index)
        def bill():
            def back():
                self.root_bill.destroy()
            self.root_bill=tk.Tk()
            self.root_bill.title('账单')
            self.root_bill.resizable(False,False)
            self.root_bill.protocol('WM_DELETE_WINDOW', lambda:back())
            center_window(self.root_bill,310,400)
            bills = db.get_column_values_where_id('bill',self.my_data_list[1])
            self.back_button = tk.Button(self.root_bill, text='退出',relief='sunken',width=3, command=back).grid(row=0,column=0)
            self.amount_label = tk.Label(self.root_bill, text=f"金额",width=7,relief='sunken').grid(row=0,column=1)
            self.time_label = tk.Label(self.root_bill, text=f"-------消费时间-------", relief='sunken').grid(row=0,column=2)
            self.busi_id_label = tk.Label(self.root_bill, text=f"商家ID", relief='sunken').grid(row=0,column=3)
            self.merchant_id_label = tk.Label(self.root_bill, text=f"消费单号", relief='sunken').grid(row=0,column=4)
            for i, bill in enumerate(bills):
                self.bill_index=tk.Label(self.root_bill,text=f'{i+1}',width=3,relief='sunken').grid(row=i+1,column=0)
                if bill[2]=='-充值-':
                    self.amount = tk.Label(self.root_bill, text=f"+{bill[0]}", width=7, relief='sunken').grid(row=i + 1,column=1)
                else:
                    self.amount = tk.Label(self.root_bill, text=f"-{bill[0]}",width=7,relief='sunken').grid(row=i+1, column=1)
                self.time= tk.Label(self.root_bill, text=f"{bill[1]}",relief='sunken').grid(row=i+1, column=2)
                self.busi_id_ = tk.Label(self.root_bill, text=f" {bill[2]}", relief='sunken').grid(row=i+1, column=3)
                self.merchant_id = tk.Label(self.root_bill, text=f"{bill[3]}",relief='sunken').grid(row=i+1,column=4)
            self.root_bill.mainloop()
        # ---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg = tk.Label(self.root, image=self.photo)
        self.bg.image = self.photo
        self.bg.pack()
        self.top_frame=tk.Frame(self.root).pack()
        self.top_label=tk.Label(self.top_frame,text='个人信息',font='Arial,50',bg='steelblue').place(x=210,y=20)
        self.second_frame=tk.Frame(self.root,bg='steelblue',height=250,width=420).place(x=50,y=50)
        self.third_frame=tk.Frame(self.second_frame,bg='steelblue',height=26,width=420).place(x=50,y=50)
        self.label_name=tk.Label(self.third_frame,height=1,width=13,text=f'HI,{self.my_data_list[0]}',fg='red',font='Arail',bg='steelblue').place(x=50,y=50)
        self.button_recharge = tk.Button(self.third_frame, height=1, width=8, text='充值', fg='black', bg='steelblue',relief='sunken', command=recharge).place(x=165, y=47)
        self.button_pay=tk.Button(self.third_frame,height=1,width=8,text='支付',fg='black',bg='steelblue',relief='sunken',command=pay).place(x=225,y=47)
        self.button_bill=tk.Button(self.third_frame,height=1,width=8,text='账单',fg='black',bg='steelblue',relief='sunken',command=bill).place(x=285,y=47)
        self.button_edit=tk.Button(self.third_frame,height=1,width=8,text='编辑信息',fg='black',bg='steelblue',relief='sunken',command=edit).place(x=345,y=47)
        self.button_back=tk.Button(self.third_frame,height=1,width=8,text='退出登录',fg='black',bg='steelblue',relief='sunken',command=back).place(x=405,y=47)
        self.photo=tk.Label(self.second_frame,image=self.my_photo)
        self.photo.image=self.my_photo
        self.photo.place(x=70,y=100)
        self.forth_frame=tk.Frame(self.second_frame,height=180,width=250).place(x=200,y=100)
        self.name_label=tk.Label(self.forth_frame,text=f'姓名:{self.my_data_list[0]}  性别:{self.my_data_list[6]}',font='Arial,8',fg='black',anchor='w').place(x=210,y=110)
        self.id_label=tk.Label(self.forth_frame,text=f'ID:{self.my_data_list[1]} 余额:{self.my_data_list[3]}',font='Arial,8',fg='black',anchor='w').place(x=210,y=140)
        self.lim_label=tk.Label(self.forth_frame,text=f'每日限额:{self.my_data_list[5]}',font='Arial,8',fg='black',anchor='w').place(x=210,y=170)
        self.ex_label=tk.Label(self.forth_frame,text=f'({self.my_data_list[5]-self.my_data_list[9]})',font='Arial,8',fg='red',anchor='e').place(x=370,y=170)
        self.exp_label=tk.Label(self.forth_frame,text=f'今日消费:{self.my_data_list[9]}',font='Calibri,8',fg='black',anchor='w').place(x=210,y=200)
        self.admis_label=tk.Label(self.forth_frame,text=f'入学时间:{self.my_data_list[4]}',font='Arial,8',fg='black',anchor='w').place(x=210,y=230)
class CBinWindow(Window):
    def __init__(self,index):
        super().__init__()
        self.index = index
        self.parse_data()
        self.display()
        self.root.mainloop()
    def parse_data(self):
        self.my_data_list = list(db.get_row_info('students', self.index))
        self.my_data_list[7] = BytesIO(self.my_data_list[7])
    def display(self):
        def back():
            self.root.destroy()
            EditWindow(self.index)
        def register():
            bin=self.bin.get()
            bin_new=self.new_bin.get()
            bin_again=self.bin_again.get()
            if db.get_row_info('students',self.index)[2]==bin:
                if bin_new==bin_again:
                    messagebox.showinfo('提示', '修改成功,请重新登录')
                    db.update_row_col_info('students', self.my_data_list[1],'bin',bin_new)
                    self.root.destroy()
                    MainWindow()
            else:
                messagebox.showinfo('提示','密码错误')
        # ---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg = tk.Label(self.root, image=self.photo)
        self.bg.image=self.photo
        self.bg.pack()
        self.top_frame = tk.Frame(self.root).pack()
        self.top_label = tk.Label(self.top_frame, text='修改密码', font='Arial,50', bg='steelblue').place(x=250,y=40)
        self.second_frame = tk.Frame(self.root, bg='steelblue', height=180, width=300).place(x=126, y=75)
        self.label_bin = tk.Label(self.second_frame, width=9, bg='royalblue', text='原密码:', font='Arail,20',anchor='w').place(x=130, y=100)
        self.bin = tk.StringVar()
        tk.Entry(self.second_frame, width=17, font='Arial', textvariable=self.bin, show='*').place(x=230, y=100)
        self.label_bin = tk.Label(self.second_frame, width=9,bg='royalblue', text='新密码:', font='Arail,20',anchor='w').place(x=130, y=140)
        self.new_bin = tk.StringVar()
        tk.Entry(self.second_frame, width=17, font='Arial', textvariable=self.new_bin, show='*').place(x=230, y=140)
        self.label_bin = tk.Label(self.second_frame, width=9,bg='royalblue', text='确认密码:', font='Arail,10',anchor='w').place(x=130, y=180)
        self.bin_again = tk.StringVar()
        tk.Entry(self.second_frame, width=17, font='Arial', textvariable=self.bin_again, show='*').place(x=230, y=180)
        self.button_sign = tk.Button(self.second_frame, text='确认修改', font='Helvetica,8', width=8, height=1,bg='royalblue',command=register).place(x=240, y=215)
        self.back=tk.Button(self.second_frame,text='返回',width=3,bg='royalblue',command=back).place(x=390,y=220)
class MainWindow(Window):
    def __init__(self):
        super().__init__()
        self.display()
        self.root.mainloop()
    def display(self):
        def sign():                                    #登录按钮触发
            id=self.id.get()
            bin=self.bin.get()
            if id=='':
                my_data={'id':0,'bin':bin}
            else:
                my_data={'id':int(id),'bin':bin}
            data_ids=db.get_all_rows('students')
            for index, item in enumerate(data_ids):             #遍历数据库，判断输入的id与密码是否正确
                if item[1] == my_data['id'] and item[2] == my_data['bin']:
                    messagebox.showinfo('提示', '登录成功')
                    self.root.destroy()
                    MangerWindow(index) #密码正确进入管理页面
                    return
            messagebox.showinfo('提示', '账号或密码错误，请重新登录')
            self.root.destroy()
            MainWindow()
        # ---------------------------------------------------------------页面设计-----------------------------------------------------
        self.bg=tk.Label(self.root,image=self.photo).pack()
        self.top_frame=tk.Frame(self.root).pack()
        self.top_label=tk.Label(self.top_frame,text='校园卡管理系统',font='Arial,50',bg='steelblue').place(x=195,y=40)
        self.second_frame=tk.Frame(self.root,bg='steelblue',height=180,width=200).place(x=166,y=75)
        self.label_user=tk.Label(self.second_frame,bg='royalblue',text='账户:',font='Arial,20').place(x=170,y=110)
        self.id=tk.StringVar()
        tk.Entry(self.second_frame,width=12,font='Arial',textvariable=self.id).place(x=230,y=110)
        self.label_bin=tk.Label(self.second_frame,bg='royalblue',text='密码:',font='Arail,20').place(x=170,y=170)
        self.bin = tk.StringVar()
        tk.Entry(self.second_frame, width=12, font='Arial', textvariable=self.bin, show='*').place(x=230, y=170)
        self.button_sign=tk.Button(self.second_frame,text='登录',font='Helvetica,8',width=5,height=1,bg='royalblue',command=sign).place(x=240,y=208)
db = MyDatabase("card_id.db") #链接数据库
MainWindow()
db.close_connection()               #关闭连接