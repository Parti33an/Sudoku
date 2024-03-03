'''
Программа решения классического Судоку.
Управление:
перемещение курсора по полю стрелками,
ввод числа - клавишами от 1 до 9,
стирание - пробел.
Решение судоку - рекурсивным поиском заполнения по графу
с отбором самого частого значения при неоднозначно возможном значении в ячейке.
Лучшее решение алгоритмом X Кнута - см. https://habr.com/ru/articles/462411/
'''
VERSION_INFO = "Версия 1.0\n (C)&(P) Ванюков Е.Е.\n\t 2024"

from PIL import ImageGrab
from tkinter import filedialog, messagebox, colorchooser, font
from tkinter.ttk import Combobox
from tkinter import *
import json
from pathlib import *
import copy

#Системные параметры
ICON_NAME = 'sudoku_logo.ico'
INI_FILE = 'sudoku.ini'
F_EXT = "sud"
SOL_EXT = "jpg"
DEFAULT_NAME = '' #'noname.' + F_EXT
PROGRAM_NAME = ' Решатель СУДОКУ'

# Меню
M_NEW_GAME = 'Игра'
M_CREATE = 'Новая игра'
M_OPEN = 'Открыть...'
M_SAVE = 'Сохранить'
M_SAVE_AS = 'Сохранить как...'
M_SAVE_SOLUTION = 'Сохранить решение'
M_QUIT = "Выйти"
M_SOLVE = "Решить"
M_OPTIONS = "Настройки"
M_COLORS = "Цвета"
M_FONT = "Шрифт"
M_HELP = "Помощь"
M_ABOUT = 'О программе'
M_VERSION = "Версия"
BASE_MENU = {M_NEW_GAME: [M_CREATE, M_OPEN, M_SAVE, M_SAVE_AS, M_SAVE_SOLUTION, M_QUIT],
                M_SOLVE : [], 
                M_OPTIONS: [M_COLORS, M_FONT],
                M_HELP: [M_ABOUT, M_VERSION],
                }
# Цвета
C_EMPTY_CELL = "Поле"
С_DATA_CELL = "Значение"
С_CURSOR_CELL = "Курсор"

def RGB(red,green,blue): return '#%02x%02x%02x' % (int(red), int(green) , int(blue))

class Excel():
    ''' класс для хранения данных ячайки таблицы '''
    
    def __init__(self, number, constant = False):
        self.number = number
        self.constant = constant
        self.possible=[]
    
    def __repr__(self):
        return str(self.number)

class Sudoku():
    #значения
    BASESET = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    PUSTO = '0'

    def __init__(self):
        self.table = list(list(Excel(Sudoku.PUSTO) for i in range(9)) for l in range(9))
        self.counter = 0

    @staticmethod
    def list_wo_repeats(a):
        # проверка отсутствия повторений в списке
        b = set(a)
        if len(a) != len(b):
            return False
        else:
            return True

    @staticmethod
    def getrowlist(table, i): 
        #получение списка значений в строке
        return [table[i][j].number for j in range(9) if table[i][j].number != Sudoku.PUSTO]

    @staticmethod
    def getcolumnlist(table, j):
        #получение списка значений в столбце
        return [table[i][j].number for i in range(9) if table[i][j].number != Sudoku.PUSTO]

    @staticmethod
    def getsquarelist(table, row, column):
        #получение списка значений в подквадрате 3x3, где row и column от 0 до 2
        a=[]
        for n in range(3):
            for k in range(3):
                if table[row*3+n][column*3+k].number != Sudoku.PUSTO:
                    a.append(table[row*3+n][column*3+k].number)
        return a

    @staticmethod
    def data_consistency(table): 
        # проверка согласованности данных
        # проверка по строкам
        for i in range(9):
            a = Sudoku.getrowlist(table, i)
            if  not Sudoku.list_wo_repeats(a):
                return False
        # проверка по столбцам
        for j in range(9):
            a = Sudoku.getcolumnlist(table, j)
            if not Sudoku.list_wo_repeats(a):
                return False
        # проверка по квадратам 3x3
        for i in range(3):
            for j in range(3):
                a = Sudoku.getsquarelist(table, i, j)
                if not Sudoku.list_wo_repeats(a):
                    return False
        return True
    
    @staticmethod
    def getfreecells(table):
        # получения списка пустых ячеек в таблице
        freecells=[]
        for i in range(9):
            for j in range(9):
                if table[i][j].number == Sudoku.PUSTO:
                    freecells.append((i, j))
        return freecells
    
    def solve_sudoku(self, table): #рекурсивная функция поиска решения по графу заполнения
        def get_multivalue_cell(table, cellvalues):
            # поиск ячейки и сортировка значений возможных по убыванию частоты
            for multichoice in range(2, 10):
                if len(cellvalues[multichoice]) > 0:
                    break
            all_values = []
            # создаем список всех возможных значений
            for cell in cellvalues[multichoice]:
                all_values.extend(table[cell[0]][cell[1]].possible)
            frequency=dict()
            # cловарь частотного появления
            for i in Sudoku.BASESET: #range(1,10):
                frequency[i] = all_values.count(i)
            i = 0
            max_frequency_value = sorted(frequency, key = frequency.get)[-1]  # самое частое значение среди возможных
                    #находим ячейку с самым частым значением и сортируем возможные значения в порядке убывания частоты
            for cell in cellvalues[multichoice]:
                pointer = table[cell[0]][cell[1]]
                if max_frequency_value in pointer.possible:
                    pointer.possible = sorted(pointer.possible, key=lambda v: frequency[v], reverse=True)
                    return cell
        self.counter +=1
    
        cur_table=copy.deepcopy(table)
        cur_freecells = self.getfreecells(cur_table)
        cellvalues = {i:[] for i in range(10)}
        for cell in cur_freecells:
            pointer = cur_table[cell[0]][cell[1]]
            pointer.possible = list(self.BASESET - set(self.getrowlist(cur_table, cell[0])) \
                                    - set(self.getcolumnlist(cur_table, cell[1])) \
                                    - set(self.getsquarelist(cur_table, cell[0]//3, cell[1]//3)))
            cellvalues[len(pointer.possible)].append(cell)
    
        if len(cur_freecells) == 0:
            return cur_table
        else:
            if len(cellvalues[0]) > 0:
                # нет решения!
                return False
            if len(cellvalues[1]) > 0:
                for cell in cellvalues[1]:
                    pointer = cur_table[cell[0]][cell[1]]
                    pointer.number = list(pointer.possible)[0]
                    pointer.possible = []
                if(not self.data_consistency(cur_table)):
                    return False
                else:
                    return self.solve_sudoku(cur_table)
            else:
                '''
                # старый алгоритм выбора значения без учета частоты числа в ячейках многозначных одного ранга
                multiplychoice=False 
                while(not multiplychoice):
                    for i in range(2, 10):
                        if len(cellvalues[i]) > 0:
                            multiplychoice = i
                            break
                multivalue_cell = cellvalues[i][0]
                '''
                multivalue_cell = get_multivalue_cell(cur_table, cellvalues) #c учетом частоты
                possible_values = cur_table[multivalue_cell[0]][multivalue_cell[1]].possible.copy()
                for number in possible_values:
                    cur_table[multivalue_cell[0]][multivalue_cell[1]].number = number
                    res = self.solve_sudoku(cur_table)
                    if (res):
                        return res

    def open(self, filename):
        counter = 0
        try:
            with open(filename,'r') as f:
                for line in f:
                    data = line.split()
                    if len(data) == 9:
                        if counter<9:
                            for i in range(9):
                                if (data[i] in Sudoku.BASESET) or (data[i]  == Sudoku.PUSTO): 
                                    self.table[counter][i]=Excel(data[i], True)
                                else:
                                    return "Неверные значения! Исправьте данные!"
                            counter += 1
                        else:
                            return "Неверное количестов строк! Исправьте данные!"
                    else:
                        return "Неверный размер строки! Исправьте данные!"
        except:
            return "Ошибка чтения файла! Неверный формат или файл не существует!"
        
    def save(self, filename):
        try:
            with open(filename,'w') as f:
                for i in range(9):
                    for j in range(9):
                        f.write(f"{self.table[i][j].number} ")
                #f.write("test")
                    f.write("\n")
        except:
            return "Ошибка записи файла!"
    
class ResizingCanvas(Canvas):
    # Перестройка основного окна при изменении размера
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.parent = parent
        self.x0 = 0
        self.y0 = 0

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height

        self.width = event.width 
        self.height = event.height 

        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        # self.scale("all",0,0,wscale,hscale)
        self.parent.get_scale()
        self.set_center()
        self.parent.draw_table()
    
    def get_center(self):
        return self.width/2 + self.x0, self.height/2 - self.y0
    
    def set_center(self, *args):
        if args == ():
            self.x0 = 0
            self.y0 = 0
        else:
            self.x0 = args[0]
            self.y0 = args[1]

class App(Tk):
    global parameters
    menuitem={}

    def __init__(self):
        super().__init__()
        self.bind('<KeyPress>', self.key_pressed)
        self.configure(bg='blue')
        self.title( PROGRAM_NAME + " - " + DEFAULT_NAME)
        if (Path(ICON_NAME).exists()):
            #print(ICON_NAME)
            #self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=ICON_NAME))
            #self.iconphoto(False, PhotoImage(file = "reactor360.png"))
            self.iconbitmap(ICON_NAME)
        else:
            print("No icon")
            pass
        screen_height=int(self.wm_maxsize()[1])  # получаем размер экрана и вычисляем размер окна приложения
        self.start_position_askdialog="+{}+{}".format(int(screen_height/3), int(screen_height/3))
        self.geometry('{}x{}+{}+{}'.format(int(screen_height*0.9), int(screen_height*0.9), 0, 0))
        self.state("zoomed") #- окно на весь экран над панелью задач
        self.minsize(400, 400)
        self.sudoku = Sudoku()
        self.solution_table = None
        self.scale = screen_height / 11
        self.colors = {C_EMPTY_CELL:"White",
                        С_DATA_CELL:"Light Sky Blue", #Yellow
                        С_CURSOR_CELL:"Green"}
        self.font_list = [f for f in font.families()]
        self.font = "Lucida Console" #"Impact" "Lucida Console" "Times New Roman"
        self.filename = ''
        self.status = "  Новая игра"
        self.cursor_position = [0,0]
        self.last_dir = Path.cwd()
        self.menu_ = BASE_MENU
        
        self.screen = ResizingCanvas(self, bg='white')
        self.statusbar = Label(self, text="  No data", bd=3, relief=SUNKEN, anchor=W, font="Arial 10")
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.screen.pack(fill="both", expand=True)
        self.load_ini()
        # create menu
        self.mainmenu = Menu(self, bd=3)
        
        for key in self.menu_:
            App.menuitem[key] = Menu(self.mainmenu, tearoff=0, bd=1)
            if key!=M_SOLVE:
                for tag in self.menu_[key]:
                    App.menuitem[key].add_command(label=tag, command=lambda x=tag: self.callback(x)) #https://webdevblog.ru/kak-ispolzovat-v-python-lyambda-funkcii/ - почему lambda надо писать так
                self.mainmenu.add_cascade(label=key, menu=App.menuitem[key])
            else:
                self.mainmenu.add_command(label=M_SOLVE, command=lambda x=M_SOLVE: self.callback(x))
        self.config(menu=self.mainmenu)
    
    def reset_data(self):
        self.sudoku = Sudoku()
        self.solution_table = None
        self.cursor_position = [0,0]
        self.status = "  Новая игра"
        self.filename = ''

    def update(self):
        titlename = PROGRAM_NAME + " - " + self.filename
        self.title(titlename)
        self.statusbar['text'] = self.status
        
    def load_ini(self):
        try:
            with open(INI_FILE,'r') as f:
                self.last_dir = f.readline().rstrip()
                self.colors = json.loads(f.readline())
        except:
            print("Ошибка чтения ini файла")
        
    def save_ini(self):
        try:
            with open(INI_FILE,'w') as f:
                f.write("{}\n".format(self.last_dir))
                f.write("{}".format(json.dumps(self.colors)))
        except:
            pass
        
    def key_pressed(self, event):
        old_position = self.cursor_position.copy()
        #messagebox.showinfo('Нажато Enter',
        #                f"Тип события {type(event)} \
        #                событие {event} \
        #                время события {event.time} \
        #                координаты события {event.x_root, event.y_root}")
        if event.keycode == 39:  # <Right> key
            if old_position[0] < 8:
                self.cursor_position[0] += 1
        if event.keycode == 37:  # <Left> key
            if old_position[0] > 0:
                self.cursor_position[0] -= 1
        if event.keycode == 38:  # <Up> key
            if old_position[1] > 0:
                self.cursor_position[1] -= 1
        if event.keycode == 40:  # <Down> key
            if old_position[1] < 8:
                self.cursor_position[1] += 1
        if event.char in Sudoku.BASESET: # pressed digits from '1'to '9'
            self.sudoku.table[self.cursor_position[0]][self.cursor_position[1]].number = event.char
        if event.keycode == 32: # keycode of space
            self.sudoku.table[self.cursor_position[0]][self.cursor_position[1]].number = Sudoku.PUSTO
        self.draw_cell(*old_position)
        self.draw_cell(*self.cursor_position, cursor=True)
      
    def draw_cell(self, i, j, cursor = False):
        # рисование ячейки выделенным цветом, если это исходное значение или с цветом курсора
        color = self.colors[C_EMPTY_CELL]
        if cursor:
            color = self.colors[С_CURSOR_CELL]
        else:
            if self.sudoku.table[i][j].number != Sudoku.PUSTO:
                color = self.colors[С_DATA_CELL]
        number = None
        if self.sudoku.table[i][j].number != Sudoku.PUSTO:
            number = self.sudoku.table[i][j].number
        else:
            if self.solution_table:
                number = self.solution_table[i][j].number
        scale = self.scale
        screen = self.screen
        x0, y0 = screen.get_center()
        left_x = x0 - 4.5*scale
        left_y = y0 - 4.5*scale
        screen.create_rectangle( left_x + i*scale, left_y + j*scale,
                                    left_x + (i+1)*scale, left_y + (j+1)*scale,
            fill = color,
            outline = 'black', width = 1)
        if number:
            screen.create_text(left_x + (i+0.5)*scale, left_y + (j+0.5)*scale,
                            text= str(number), font = (self.font, int(self.scale/2))) 
                            
    def draw_table(self, table = None):
        scale = self.scale
        screen = self.screen
        screen.delete("all")            #очистить экран
        x0, y0 = screen.get_center()
        left_x = x0 - 4.5*scale
        left_y = y0 - 4.5*scale
        screen.create_rectangle(left_x , left_y,
                                        left_x + 9*scale, left_y + 9*scale,
                                        fill = 'white',
                                        outline = 'black', width=5)
        for i in range(9):
            for j in range(9):
                self.draw_cell(i, j)
        self.draw_cell(*self.cursor_position, cursor=True) # рисуем ячейку с курсором
    
    def get_scale(self):
        self.scale = min(self.screen.width, self.screen.height) / 11

    def create(self):
        #messagebox.showinfo(M_CREATE, "Создать новую игру!")
        self.reset_data()
        self.draw_table()
    
    def open_file(self):
        filename =  filedialog.askopenfilename(initialdir = self.last_dir, title = "Выберите файл",filetypes = (("sudoku files","*.{}".format(F_EXT)),("all files","*.*")))
        
        if(filename):
            self.reset_data()
            error_message_opening_file = self.sudoku.open(filename)
            if error_message_opening_file:
                messagebox.showinfo(M_OPEN, error_message_opening_file)
                self.reset_data()
            else:
                self.filename = filename
                self.status = "  Задача загружена"
                self.last_dir = Path(self.filename).parent  #https://python-scripts.com/pathlib
                self.draw_table()

    def save(self):
        #messagebox.showinfo(title = M_SAVE, message = "Cохранение!") 
        if self.filename:
            error_message_saving_file = self.sudoku.save(self.filename)
            if error_message_saving_file:
                messagebox.showinfo(M_SAVE, error_message_saving_file)
            else:
                self.status = "  Задача сохранена"
        else:
            self.save_as_file()

    def save_as_file(self):
        filename =  filedialog.asksaveasfilename(initialdir = self.last_dir, title = "Выберите файл",
                                                        filetypes = (("sudoku files","*.{}".format(F_EXT)),("all files","*.*")))
        if filename:
            if ".{}".format(F_EXT) not in filename:
                filename +=".{}".format(F_EXT)
            self.last_dir = Path(filename).parent
            self.filename = filename
            self.save()

    def save_solution(self):
        # messagebox.showinfo(title = M_SAVE_SOLUTION, message = "Cохранение решения!")
        if not self.filename:
            self.save_as_file()
        solution_name = self.filename.split(".")[0] + "." + SOL_EXT
        # сохранение картинкой - https://translated.turbopages.org/proxy_u/en-ru.ru.d720c34b-65cd08bb-7088ba48-74722d776562/https/stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
        x=self.winfo_rootx()+self.screen.winfo_x()
        y=self.winfo_rooty()+self.screen.winfo_y()
        x1=x+self.screen.winfo_width()
        y1=y+self.screen.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(solution_name)
        #
        self.status = f"  Решение сохранено картинкой в формате {SOL_EXT}"

    def quit(self):
        answer = True
        #if (self.arrange != None):
        answer = messagebox.askokcancel("Выйти", "Вы точно хотите закончить работу программы?")
        if answer:
            self.save_ini()
            self.destroy()

    def solve(self):
        if not self.sudoku.data_consistency(self.sudoku.table):
            messagebox.showinfo(title = M_SOLVE, message = "Несогласованные данные! Есть повторения в строках, столбцах или квадратах!")
            self.status = "  Введены некорректные данные! Повторите ввод..."  
        else:
            #self.solution_table = None
            self.solution_table = self.sudoku.solve_sudoku(self.sudoku.table)
            if self.solution_table:
                self.draw_table()
                self.status = f"  Судоку решена за {self.sudoku.counter} итераций"
            else:
                messagebox.showerror(title = M_SOLVE, message = "Судоку не имеет решения!!!")

    def choose_colors(self):
        def get_choice(event):
            chosen = combo_choice.get()
            #num = int(tvel_type[len(M_TVEL):])
            color_tvel.config(bg=self.colors[chosen])
            
        def change_color():
            chosen = combo_choice.get()
            #num = int(tvel_type[len(M_TVEL):])
            (rgb, hx) = colorchooser.askcolor(title = "Выберите цвет")
            # print(rgb) 
            if rgb != None:
                self.colors[chosen] = RGB(*rgb)
            color_tvel.config(bg=self.colors[chosen])
            self.draw_table()
        
        def close(*args):
            dialog.destroy()
            #self.draw_arrange()

        colors = list(self.colors.keys())

        dialog = Toplevel(self, bd = 3 ) 
        dialog.geometry('280x100'+self.start_position_askdialog)
        dialog.title("Выбрать цвета")
        dialog.focus_set()
        if (Path(ICON_NAME).exists()):
            dialog.iconbitmap(ICON_NAME)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.resizable(width = False, height= False)
        color_tvel=Button(dialog, width = 1, height= 1, bg = self.colors[C_EMPTY_CELL], command = change_color)
        color_tvel.place(relx=0.8, rely=0.18)
        Button(dialog, text = "Ок", width= 10, command = close).place(relx=0.35, rely=0.65)
        combo_choice = Combobox(dialog, values = colors, state = 'readonly')
        combo_choice.current(0)
        combo_choice.place(relx=0.1, rely=0.23)
        combo_choice.bind("<<ComboboxSelected>>", get_choice)
        dialog.bind("<Escape>", close)

    def set_font(self):
        def get_choice(event):
            self.font = combo_choice.get()
            self.draw_table()
        
        def close(*args):
            dialog.destroy()
            #self.draw_arrange()
            
        dialog = Toplevel(self, bd = 3 ) 
        dialog.geometry('280x100'+self.start_position_askdialog)
        dialog.title("Выбрать шрифт")
        dialog.focus_set()
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.resizable(width = False, height= False)
        Button(dialog, text = "Ок", width= 10, command = close).place(relx=0.35, rely=0.65)        # https://question-it.com/questions/2758962/kak-sdelat-dialog-shrifta-v-tkinter
        combo_choice = Combobox(dialog, values = self.font_list, state = 'readonly')
        combo_choice.current(self.font_list.index(self.font))
        combo_choice.place(relx=0.23, rely=0.23)
        combo_choice.bind("<<ComboboxSelected>>", get_choice)
        dialog.bind("<Escape>", close)               
       
    def show_version(self):
        messagebox.showinfo(title = PROGRAM_NAME, message = VERSION_INFO)       
    
    def show_about(self):
        messagebox.showinfo(title = PROGRAM_NAME, message = __doc__)       
   
    def callback(self, tag):
        if tag == M_CREATE:
            self.create()
        if tag == M_OPEN:
            self.open_file()
        if tag == M_SAVE:
            self.save()
        if tag == M_SAVE_AS:
            self.save_as_file()
        if tag == M_SAVE_SOLUTION:
            self.save_solution()
        if tag == M_QUIT:
            return self.quit() # return, чтобы после уничтожения окна не вызывался self.update
        if tag == M_SOLVE:
            self.solve()
        if tag == M_COLORS:
            self.choose_colors()
        if tag == M_FONT:
            self.set_font()
        if tag == M_VERSION:
            self.show_version()
        if tag == M_ABOUT:
            self.show_about()
        self.update()


if (__name__ == "__main__"):
    app=App()
    app.protocol('WM_DELETE_WINDOW', app.quit)
    app.mainloop()

