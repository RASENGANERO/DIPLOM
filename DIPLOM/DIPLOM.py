#from PyQt5.QtGui import QDoubleValidator
#QGraphicsScene
#matplotlib
#pyqtgraph
#^ - начало строки
#[0-9]* - 0 и более цифр
#[.,] - точка или запятая ([,.]? - одна или ноль запятых или точек)
#[0-9]+ - 1 и более цифр
#$ - конец строки.
#*args - аргументы
#*kwargs - именованные аргументы
#[[номер строки,действие,[х старый,y старый],[х новый,y новый]],]




import sys
from PyQt5 import Qt
from decimal import *
from PyQt5.QtWidgets import (QWidget,QMessageBox,QGridLayout,QApplication,
							 QPushButton,QFileDialog,QTableWidgetItem,QAbstractItemView,QHeaderView,
							 QTableWidget,QLabel,QLineEdit,QVBoxLayout,QHBoxLayout,QMenu,QAction,QDialog,
							 QFormLayout,QDialogButtonBox,QComboBox,QRadioButton,QCompleter,
							 QTreeView,QListView,QFileSystemModel,QInputDialog,QMenuBar,QGraphicsSceneMouseEvent,
							 QTabWidget,QSpacerItem,QSizePolicy)
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5.QtGui import *
import os
import pyqtgraph.exporters
import re
import numpy
import sqlite3
import math
from math import *
import parser
import win32com.client as win32
import matplotlib.pyplot as plt

class MainMenu(QWidget,QObject):
	menu_value=pyqtSignal(int)
	def __init__(self):
		super().__init__()
		self.menu = QMenuBar()
		self.menu_file=self.menu.addMenu('Файл')
		self.menu_file_2=self.menu.addMenu('Справка')

		self.action_help = self.menu_file_2.addAction('О программе')
		self.action_help_file = self.menu_file_2.addAction('Руководство')		
		
		
		self.action_new = self.menu_file.addAction('Новый')
		
		self.action_open = self.menu_file.addAction('Открыть')
		self.action_save = self.menu_file.addAction('Сохранить')
		self.action_save_as = self.menu_file.addAction('Сохранить как...')
		
		self.action_exit = self.menu_file.addAction('Выход')


		
		self.action_new.triggered.connect(self.new)
		self.action_open.triggered.connect(self.open)
		self.action_save.triggered.connect(self.save)
		self.action_save_as.triggered.connect(self.save_as)
		self.action_help.triggered.connect(self.help)
		self.action_help_file.triggered.connect(self.help_file)
		self.action_exit.triggered.connect(self.exit)
		

		

	def new(self):
		self.menu_value.emit(4)

	def open(self):
		self.menu_value.emit(0)

	def save(self):
		self.menu_value.emit(1)

	def save_as(self):
		self.menu_value.emit(2)

	def help(self):
		QMessageBox.information(self,'Справка','Приложение: Дипломная работа\nТема: Цифровая технология задающего воздействия PID-регулятора\nСтудент:Артамонов Роман\nГруппа: 81-ИВТ\nГод: 2022')

	def help_file(self):
		word=win32.gencache.EnsureDispatch('Word.Application')
		word.Visible=True
		doc=word.Documents.Open(str(os.getcwd())+'\\1.doc')
		
	def exit(self):
		self.menu_value.emit(3)





class Regex:
	@staticmethod
	def set_validator(s,edit):
		regex=QRegExp(s)
		gen_regex1=QRegExpValidator(regex, edit)
		edit.setValidator(gen_regex1)
		return edit


class FocusEdit(QLineEdit,QObject):
	focused=pyqtSignal(int)
	def __init__(self,change):
		super().__init__()
		self.change=change
	def mouseReleaseEvent(self,event):
		self.focused.emit(self.change)







class Completer(QCompleter):
	def __init__(self, *args, **kwargs):
		super(Completer, self).__init__(*args, **kwargs)
		self.setCompletionMode(QCompleter.PopupCompletion) 
		self._le = args[-1]
		self._path = ''
		self._path_2 = ''
		self._all_path = ''
		self.lbl = QLabel(self._le)
		self.lbl.hide()
		
	def pathFromIndex(self, index):   
		rect = QRect(
			self._le.cursorRect().x(),
			self._le.cursorRect().y(),
			self._le.width(),
			self._le.completer().widget().height()
		) 
		self.lbl.move(self._le.cursorRect().x()+8, self._le.cursorRect().y())
		self.lbl.setText(index.data()[len(self._path_2):])
		self.lbl.adjustSize()
		self.lbl.show()

		self._all_path = index.data()
		return self._path


	def splitPath(self, path):
		self._path = self._le.text() 
		self._path_2 = path
		return [path]


class LineEdit(QLineEdit):
	def __init__(self): 
		super().__init__()  
		self._all_text = ''		
		self.multipleCompleter = None

	def keyPressEvent(self, event):
		super().keyPressEvent(event)
		
		if not self.multipleCompleter:
			return
		c = self.multipleCompleter
		
		if self.text() == ".": 
			return
		c.setCompletionPrefix(self.cursorWord(self.text()))	  
		
		if len(c.completionPrefix()) < 1:
			c.popup().hide()
			return
		c.complete()

	def cursorWord(self, sentence):
		p = sentence.rfind(".")
		if p == -1:
			return sentence
		return sentence[p + 1:]

	def insertCompletion(self, text):
		p = self.text().rfind(".")								
		text = self.multipleCompleter._all_path
		if p == -1:
			pass
		else:
			text = self.text()[:p+1] + self.multipleCompleter._all_path
		self.multipleCompleter.lbl.hide()
		QTimer.singleShot(10, lambda: self.allText(text))

	def allText(self, text):
		self.setText(text)
		self._all_text = text
		self.setFocus()
		self.update()

	def event(self, event):
		if self.multipleCompleter:
			if self.multipleCompleter.popup().currentIndex().row() == -1:
				self.multipleCompleter.lbl.hide()
			else:	
				if not self.multipleCompleter.popup().selectedIndexes():
					self.multipleCompleter.lbl.hide()
					QTimer.singleShot(10, lambda: self.allText(self.multipleCompleter._path))
		return super().event(event)

	def setMultipleCompleter(self, completer):
		self.multipleCompleter = completer
		self.multipleCompleter.setWidget(self)
		completer.activated.connect(self.insertCompletion)

class SaveFile(QDialog):
	def __init__(self):
		super().__init__()
		
		self.setMinimumHeight(513)
		self.setMinimumWidth(962)
		self.setWindowTitle('Сохранить таблицу')
		self.change_close=True
		self.surnamed=''
		self.connectionbd=sqlite3.connect('surname_diplom_1.db')
		self.cursorbd=self.connectionbd.cursor()
		self.surname_list=self.get_surname()

		self.lay=QGridLayout()

		self.dirs=QTreeView()
		self.files=QListView()
		
		self.menu=QMenu()
		self.act1=QAction('Создать папку')
		self.act2=QAction('Удалить папку')
		self.menu.addActions([self.act1,self.act2])
		self.act1.triggered.connect(self.mkdir)
		self.act2.triggered.connect(self.rmdir)

		self.files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.files.customContextMenuRequested[QtCore.QPoint].connect(self.menus)

		self.dirs_model=QFileSystemModel()
		self.dirs_model.setFilter(Qt.QDir.NoDotAndDotDot |Qt.QDir.AllDirs)
		self.dirs_model.setRootPath(self.dirs_model.rootPath())
		self.dirs.setModel(self.dirs_model)
		self.dirs.clicked.connect(self.set_files)

		self.files_model=QFileSystemModel()
		self.files_model.setFilter(Qt.QDir.NoDotAndDotDot | Qt.QDir.AllDirs |Qt.QDir.Files)
		self.files_model.setRootPath(self.files_model.rootPath())
		self.files.setModel(self.files_model)
		self.files.clicked.connect(self.file_to_name)

		self.gridfiles=QHBoxLayout()
		self.gridfiles.addWidget(self.dirs)
		self.gridfiles.addWidget(self.files)
				
		self.gridsave=QHBoxLayout()
		self.gridcancel=QHBoxLayout()

		self.label_file=QLabel('Имя файла')

		self.filename = LineEdit()
		self.completer = Completer(self.surname_list, self.filename)
		
		self.filename.setCompleter(self.completer)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)  # без учета регистра
		self.filename.setMultipleCompleter(self.completer)
		
		self.filename=Regex.set_validator("[А-Яа-яA-Za-z0-9 _.]+$",self.filename)#^[-+]?[0-9]*[.,]?[0-9]+$    #[^A-Za-z0-9]

		self.save=QPushButton('Сохранить')
		self.cancel=QPushButton('Отмена')
		
		self.save.clicked.connect(self.saved)
		self.cancel.clicked.connect(self.canceled)
		
		self.gridsave.addWidget(self.label_file)
		self.gridsave.addWidget(self.filename)
		
		self.gridsave.addWidget(self.save)
		self.gridsave.addWidget(self.cancel)
		
		self.lay.addLayout(self.gridfiles,0,0)
		self.lay.addLayout(self.gridsave,1,0)
		self.setLayout(self.lay)
		

	def get_surname(self):
		self.surname_list=[]
		self.cursorbd.execute("""SELECT *FROM names WHERE id>0;""")
		query=self.cursorbd.fetchall()
		for v in range(len(query)):
			self.surname_list.append(str(query[v][1]))
		return self.surname_list

	def menus(self,pos):
		self.menu.popup(QCursor.pos())
		
	def set_files(self,index):
		path = self.dirs_model.fileInfo(index).absoluteFilePath()
		self.files.setRootIndex(self.files_model.setRootPath(path))
		
	def file_to_name(self,index):
		if self.files_model.isDir(index)!=True:
			self.filename.setText(self.files_model.fileName(index))
	
	def start_save(self):
		self.filename.setFocus()
		self.exec()
		
	def saved(self):
		self.change_close=False
		self.surnamed=str(self.files_model.rootPath())+'/'+str(self.filename.text())
		self.surnamed=str(self.surnamed).strip()
		self.surnamed=self.check_path()
		if self.surnamed!='':
			self.surnamed=self.check_exp()
			if self.surnamed!='':
				if self.surnamed!='':
					self.surnamed=self.check_exists()
		self.check_name()
		self.hide()

	def canceled(self):
		QMessageBox.information(self,"Внимание!","Вы отменили сохранение файла!")
		self.surnamed=''
		self.change_close=False
		self.hide()
		
	def get_name_path(self):
		return self.surnamed

	def rmdir(self):
		index=self.files.currentIndex()
		if self.files_model.fileInfo(index).isDir():
			if len(os.listdir(self.files_model.fileInfo(index).absoluteFilePath()+'/'))!=0:
				QMessageBox.information(self,'Внимание!','Папка не пуста!')
			else:
				self.files_model.rmdir(index)
		else:
			QMessageBox.information(self,'Внимание!','Вы не выбрали папку!')
		
	def mkdir(self):
		if str(self.files_model.rootPath()).find(':/')==-1:
			QMessageBox.information(self,'Внимание!','Не выбран путь!')
		else:
			name_dir=QInputDialog().getText(self, "Внимание!", "Введите имя папки")[0]
			if len(name_dir)!=0:
				if str(name_dir).endswith('/')==True:
					QMessageBox.information(self,'Внимание!','Неверный символ в имени папки!')
				else:
					self.files_model.mkdir(self.files_model.index(self.files_model.rootPath()),self.files_model.rootPath()+'/'+name_dir)
					self.files_model.setRootPath(self.files_model.rootPath())
			else:
				QMessageBox.information(self,'Внимание!','Имя папки не указано!')

	def check_name(self):
		sq=self.surnamed.split('.')[-1]
		self.cursorbd.execute("""SELECT *FROM names WHERE surname='"""+sq+"""';""")
		quer=self.cursorbd.fetchall()
		if len(quer)==0:
			sql=str(sq)
			countes = """SELECT COUNT(id) FROM names;"""
			self.cursorbd.execute(countes)
			query=self.cursorbd.fetchall()[0][0]
			sql="""'"""+str(query)+"""'"""+""","""+"""'"""+sql+"""'"""
			sqlite_insert_query = """INSERT INTO names(id, surname) VALUES("""+sql+""");"""
			self.cursorbd.execute(sqlite_insert_query)
			self.connectionbd.commit()
			
	def check_path(self):
		if str(self.surnamed).find(':/')==-1:
			QMessageBox.information(self,'Внимание!','Не выбран диск!')
			return ''
		else:
			return self.surnamed

	def check_exp(self):
		if self.surnamed.endswith('.')==True:
			QMessageBox.information(self,"Внимание!","Вы не указали расширение!")
			return ''
		else:
			return self.surnamed

	def check_exists(self):
		if os.path.exists(self.surnamed)==True:
			QMessageBox.information(self,"Внимание!","Такой файл существует! Он будет перезаписан!")
		return self.surnamed
		

	def closeEvent(self, event):
		if self.change_close==True:
			closed = QMessageBox.question(self,"Отмена","Отменить сохранение таблицы?",QMessageBox.Ok | QMessageBox.Cancel)
			if closed == QMessageBox.Ok:
				event.accept()
				self.change_close=False
			else:
				event.ignore()
				self.change_close=True
		

class ThreadFormul(QThread):
	formul_datas=pyqtSignal(list)
	def __init__(self,datas,form):
		super().__init__()
		self.datas=datas
		self.form=form
		self.errors=[]

	def run(self):
		self.datas=[float(a) for a in list(numpy.linspace(self.datas[0],self.datas[1],self.datas[2]))]
		for v in range(len(self.datas)):
			try:
				s=self.form.replace('t',str(float(self.datas[v]))).replace('^','**')
				y=eval(parser.expr(s).compile())
				self.formul_datas.emit([str(self.datas[v]),str(y)])
			except Exception:
				self.errors.append(s+'  Ошибка!')


class CheckTime(QThread):
	check_time=pyqtSignal(int)
	def __init__(self,data_tables):
		super().__init__()
		self.data_tables=data_tables
		self.delta_time=self.data_tables[1]-self.data_tables[0]
	
	def run(self):
		for v in range(len(self.data_tables)-1):
			if (self.data_tables[v]+self.delta_time)==self.data_tables[v+1]:
				self.check_time.emit(1)
				continue
			else:
				self.check_time.emit(0)
				break



class WidgetPID(QWidget):
	def __init__(self,main_table):
		super().__init__()
		self.grid_pid=QGridLayout()
		self.table_pid=QTableWidget()
		self.scene_pid=QLabel()
		self.setWindowTitle('График PID')
		
		self.m_n=main_table
		self.m_n.create_table(self.table_pid,7,['n','t','T','x','x0','Δx','U'])
		
	


		self.setLayout(self.grid_pid)
		self.grid_pid.addWidget(self.table_pid,0,0)
		self.grid_pid.addWidget(self.scene_pid,0,1)

		self.but_closed = QPushButton('ОК')
		self.but_closed.clicked.connect(self.closed_pid_widget)
		self.grid_pid.addWidget(self.but_closed,1,1)
		self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
		

	def setter_one_items(self,row,column,text):
		item=QTableWidgetItem(str(text))
		item.setFlags(QtCore.Qt.ItemIsEditable)
		item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
		self.table_pid.setItem(row,column,item)

	def get_data_column(self,column):
		lk=[]
		for v in range(0,self.table_pid.rowCount()):
			lk.append(float(self.table_pid.item(v,column).text()))
		return lk
	
	def save(self,sfiles):
		from xlsxwriter.workbook import Workbook
		filename=sfiles
		_list = []
		model = self.table_pid.model()
		for row in range(model.rowCount()):
			_r = []
			for column in range(model.columnCount()):
				_r.append(str(model.index(row, column).data()).replace('.',','))
			_list.append(_r)

		workbook = Workbook(filename)
		worksheet = workbook.add_worksheet() 

		for r, row in enumerate(_list):
			for c, col in enumerate(row):
				worksheet.write(r, c, col)        
		workbook.close()  


	def set_graph(self,color,column,lb):
		#self.graph_pid=GraphPID()
		self.table_pid.resizeColumnsToContents()
		data_graph=[self.get_data_column(1),self.get_data_column(column)]
		
		plt.plot(data_graph[0],data_graph[1],color,label=lb)
		plt.legend(shadow=True)
		plt.grid(True)
		x=data_graph[0]
		x=[int(a) for a in x]
		y=data_graph[1]
		y=[int(a) for a in y]
		y1=min(y)-3
		y2=max(y)+3
		try:
			plt.xlim([min(x),max(x)])
			plt.ylim([y1,y2])
		except Exception:
			pass
		plt.savefig('1.jpg')
		pixmap=QPixmap('1.jpg')
		self.scene_pid.setPixmap(pixmap)
		self.scene_pid.setAutoFillBackground(True)
		#plt.close()
		


	def closed_pid_widget(self):
		self.close()
		self.destroy()
		os.remove('1.jpg')



class ThreadPID(QThread):
	pid_datas=pyqtSignal(list)
	def __init__(self,datas,main_table,start_data):
		super().__init__()
		self.datas=datas
		self.row=main_table.rowCount()
		self.start_data=start_data
		self.datas=[float(a) for a in self.datas]
		self.datas[-1]=int(self.datas[-1])
		self.delt_x=None
		self.lkspis=[]
		self.m_n=main_table
		
		self.k_0=float(self.datas[0]+(self.datas[1]*self.datas[3])+(self.datas[2]/self.datas[3]))
		self.k_1=float(-(((2*self.datas[2])/self.datas[3])+self.datas[0]))
		self.k_2=float(self.datas[2]/self.datas[3])


		
		
		self.widget_pid=WidgetPID(self.m_n)
		
		self.widget_pid.table_pid.setRowCount(int(self.datas[-1]))
	

	def run(self):
		for v in range(0,self.row):
			self.pid_datas.emit([v,0,v])
			self.pid_datas.emit([v,1,self.start_data[0][v]])
			self.pid_datas.emit([v,2,self.datas[-2]])
			self.pid_datas.emit([v,4,self.start_data[1][v]])
		

		for v in range(0,self.row):
			if v==0:
				self.x=float(0)
				self.delt_x=float(Decimal(str(self.start_data[1][v]))-Decimal(str(self.x)))
				self.lkspis.append(self.delt_x)
				self.y=float(Decimal(str(self.datas[0]))*Decimal(str(self.start_data[1][0])))

				self.pid_datas.emit([v,3,str(self.x)])
				self.pid_datas.emit([v,5,str(self.delt_x)])
				self.pid_datas.emit([v,6,str(self.y)])


			if v==1:
				self.x=float((0.9*self.x)+(0.1*self.y))
				self.delt_x=float(Decimal(str(self.start_data[1][v]))-Decimal(str(self.x)))
				
				self.lkspis.append(self.delt_x)
				self.y=float(((self.datas[0]+(self.datas[1]*self.datas[3])+(self.datas[2]*(1/self.datas[3])))*self.start_data[1][v])-((self.datas[0]+(self.datas[1]*self.datas[3])+(self.datas[2]*(1/self.datas[3])))*self.x)-((self.datas[2]*(1/self.datas[3]))*self.start_data[1][v-1]))
				self.pid_datas.emit([v,3,str(self.x)])
				self.pid_datas.emit([v,5,str(self.delt_x)])
				self.pid_datas.emit([v,6,str(self.y)])


			if v>=2:
				self.x=float((0.9*self.x)+(0.1*self.y))
				self.delt_x=float(Decimal(str(self.start_data[1][v]))-Decimal(str(self.x)))
				
				self.y=float(Decimal(str(self.y))+Decimal(str(self.k_0))*(Decimal(str(self.delt_x)))+Decimal(str(self.k_1))*Decimal(str(self.lkspis[-1]))+Decimal(str(self.k_2))*Decimal(str(self.lkspis[-2])))
				self.pid_datas.emit([v,3,str(self.x)])
				self.pid_datas.emit([v,5,str(self.delt_x)])
				self.pid_datas.emit([v,6,str(self.y)])
				self.lkspis.append(self.delt_x)
				


		

class Table(QTableWidget,QObject):
	del_and_change_signal=pyqtSignal(bool)
	colores=pyqtSignal(bool)
	focusable_edit=pyqtSignal(int)
	cleared=pyqtSignal(int)
	file_path=pyqtSignal(str)
	#back_forward_signal=pyqtSignal(bool)


	def __init__(self,**kwargs):
		super().__init__()
		self.UNIQUIE_X=[[],[],[],[]]#данные для структуры таблицы
		self.CHANGE_TABLE=[]#данные для запоминания изменения структуры таблицы

		self.click=False
		self.check_formulas_values=False
		self.layoutes1=QHBoxLayout()
		self.layoutes2=QHBoxLayout()
		self.lay_pid_1=QHBoxLayout()
		self.lay_pid_2=QHBoxLayout()
		


		self.menu_for_tabled=QMenu()
		self.act1=QAction('Удалить данные')
		self.act2=QAction('Распечатать данные')
		self.act3=QAction('Открыть')
		self.act4=QAction('Сохранить')
		self.act5=QAction('Сохранить как...')
		self.menu_for_tabled.addActions([self.act1,self.act2,self.act3,self.act4,self.act5])
		self.act1.triggered.connect(self.del_from_table)
		self.act2.triggered.connect(self.select_print_table)
		self.act3.triggered.connect(self.open_table)
		self.act4.triggered.connect(self.select_save_table)
		self.act5.triggered.connect(self.select_save_table_as)
		


		
		self.line1=QLabel('Введите t   ')
		self.line2=QLabel('Введите x0')

		self.create_table(self,4,['t','x0','points','NumRow'])
		self.hideColumn(3)



		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested[QtCore.QPoint].connect(self.menu_for_table)

		self.itemChanged.connect(self.edit_for_table)
		self.itemDoubleClicked.connect(self.click_for_item)
		self.prevt=str()
		self.nextt=str()



		self.but1=QPushButton('Вставить значения')
		self.but1.clicked.connect(self.insert_row_table)

		


		

		self.edit1=FocusEdit(1)
		self.edit2=FocusEdit(2)

		self.edit1=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",self.edit1)
		self.edit2=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",self.edit2)

		self.edit1.focused.connect(self.set_focuses)
		self.edit2.focused.connect(self.set_focuses)



		self.setMouseTracking(True)
		
		#self.cellChanged.connect(self.edit_for_table)
		#self.doubleClicked.connect(self.save_cell)
		#self.itemPressed.connect(self.prev_change) #changed!
		#self.itemChanged.connect(self.new_change)
		
		self.change=False
		
		


		self.index_change=-1
		self.but4=QPushButton('Назад')
		self.but4.clicked.connect(self.back)
		self.but5=QPushButton('Вперёд')
		self.but5.clicked.connect(self.forward)
		self.but4.setEnabled(False)
		self.but5.setEnabled(False)
		self.back_forward_change_list=False


		self.color1=QRadioButton('График c отрезками')
		self.color2=QRadioButton('График с точками')
		self.color2.setMinimumWidth(125)
		self.color1.toggled.connect(self.set_color_graph1)
		self.color2.toggled.connect(self.set_color_graph2)
		self.color1.setChecked(True)

		self.but_fx=QPushButton('Построить график')
		self.label_fx=QLabel('Введите формулу x0(t)')
		self.label_min_fx=QLabel('tmin')
		self.label_max_fx=QLabel('tmax')
		self.label_count_fx=QLabel('Кол-во точек')


		
		self.ed_max_fx=QLineEdit()
		self.ed_form_fx=QLineEdit()
		self.ed_min_fx=QLineEdit()
		self.ed_сount_fx=QLineEdit()
		
		self.but_fx.clicked.connect(self.set_graph_form)


		self.ed_min_fx=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",self.ed_min_fx)
		self.ed_max_fx=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",self.ed_max_fx)
		self.ed_сount_fx=Regex.set_validator("^((?!(0))[0-9]{0,10})$",self.ed_сount_fx)



		

		self.layoutes1.addWidget(self.label_fx)
		self.layoutes1.addWidget(self.label_min_fx)
		self.layoutes1.addWidget(self.label_max_fx)
		self.layoutes1.addWidget(self.label_count_fx)
		self.layoutes1.addSpacing(105)



		self.layoutes2.addWidget(self.ed_form_fx)
		self.layoutes2.addWidget(self.ed_min_fx)
		self.layoutes2.addWidget(self.ed_max_fx)
		self.layoutes2.addWidget(self.ed_сount_fx)
		self.layoutes2.addWidget(self.but_fx)
		self.insert_row=False
		self.insert_row_count=0
		self.setTabKeyNavigation(False)


		self.lb_pid_kp=QLabel('Kп')
		self.lb_pid_ki=QLabel('Kи')
		self.lb_pid_kd=QLabel('Кд')
		self.lb_pid_t=QLabel('T')
		self.lb_pid_n=QLabel('n')




		self.ed_pid_kp=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",QLineEdit())
		self.ed_pid_ki=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",QLineEdit())
		self.ed_pid_kd=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",QLineEdit())
		self.ed_pid_t=QLineEdit()
		self.ed_pid_n=QLineEdit()


		#self.ed_pid_kp.setText(str('10'))
		#self.ed_pid_ki.setText(str('5'))
		#self.ed_pid_kd.setText(str('3'))
		self.ed_pid_t.setReadOnly(True)
		self.ed_pid_n.setReadOnly(True)



		self.but_check_pid=QPushButton('Анализ х0(t)')
		self.but_check_pid.clicked.connect(self.check_pid_form)



		self.but_pid=QPushButton('Рассчитать PID')
		self.but_pid.clicked.connect(self.set_pid_form)
		self.pid_time=1




		self.lay_pid_1.addWidget(self.lb_pid_kp)
		self.lay_pid_1.addWidget(self.lb_pid_ki)
		self.lay_pid_1.addWidget(self.lb_pid_kd)
		self.lay_pid_1.addWidget(self.lb_pid_t)
		self.lay_pid_1.addWidget(self.lb_pid_n)
		self.lay_pid_1.addSpacing(130)

		self.lay_pid_2.addWidget(self.ed_pid_kp)
		self.lay_pid_2.addWidget(self.ed_pid_ki)
		self.lay_pid_2.addWidget(self.ed_pid_kd)
		self.lay_pid_2.addWidget(self.ed_pid_t)
		self.lay_pid_2.addWidget(self.ed_pid_n)
		self.lay_pid_2.addWidget(self.but_check_pid)
		self.lay_pid_2.addWidget(self.but_pid)
		self.but_pid.setEnabled(False)
		self.check_file_save=False
		self.save_open_file_path=''
		self.check_starts_of_pid=False


	def mouseReleaseEvent(self,event):
		if self.insert_row==True:
			self.final_insert_row()


	def get_sort(self,s):
		s=self.UNIQUIE_X[0].index(s)
		return [self.UNIQUIE_X[0][s],self.UNIQUIE_X[1][s],
		  list(self.UNIQUIE_X[2][s].keys())[0],self.UNIQUIE_X[3][s]]


	def sorting_table(self):
		#self.blockSignals(True)
		self.UNIQUIE_X=self.get_values_table()
		s=sorted(self.UNIQUIE_X[0])
		vr_sp=[[],[],[],[]]
		for v in range(len(s)):
			p=self.get_sort(s[v])
			for q in range(len(p)):
				vr_sp[q].append(p[q])
		self.setRowCount(0)
		for v in range(len(vr_sp[0])):
			row=self.rowCount()
			self.insertRow(row)
			self.setter_items(str(vr_sp[0][v]),self.rowCount()-1,0,self)
			self.setter_items(str(vr_sp[1][v]),self.rowCount()-1,1,self)
			self.setter_items(str(vr_sp[2][v]),self.rowCount()-1,2,self)
			self.setter_items(str(vr_sp[3][v]),self.rowCount()-1,3,self)
		self.UNIQUIE_X=self.get_values_table()
		#self.blockSignals(False)


	def keyPressEvent(self, event):
		QtWidgets.QTableWidget.keyPressEvent(self, event)
		if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and self.insert_row==True:
			if self.insert_row_count<2:
				curr = self.currentIndex()
				next = curr.sibling(curr.row(), curr.column()+1)
				if next.isValid():
					self.setCurrentIndex(next)
					self.edit(next)
				self.insert_row_count+=1
			else:
				self.final_insert_row()
		if event.key()==QtCore.Qt.Key_Delete:
			self.del_from_table()


	
	def insert_row_table(self):
		
		self.blockSignals(True)
		if len(self.selectionModel().selectedRows())==0:
			QMessageBox.information(self,'Внимание!','Не одна строка не выбрана!')
		else:
			self.row_inserts=max([a.row() for a in self.selectionModel().selectedRows()])+1
			self.insertRow(self.row_inserts)
			self.selectRow(self.row_inserts)
			self.setter_items('A'+str(self.rowCount()),self.row_inserts,2,self)
			self.setter_items(str(self.rowCount()-1),self.row_inserts,3,self)

			self.insert_row=True
			self.insert_row_count=1
			self.edit(self.model().index(self.row_inserts,0))
			

	def error_insert(self,s):
		QMessageBox.information(self,'Внимание!',s)
		self.insert_row=False
		self.removeRow(self.row_inserts)
		self.blockSignals(False)

	def update_changes(self):
		index_vr=self.CHANGE_TABLE[-1]
		number_index_vr=index_vr['number'][0]
		del self.CHANGE_TABLE[-1]
		for v in range(len(self.CHANGE_TABLE)):
			s=self.CHANGE_TABLE[v]['number']
			for q in range(len(s)):
				if s[q]>=number_index_vr:
					s[q]+=1
			self.CHANGE_TABLE[v]['number']=s
		self.CHANGE_TABLE.append(index_vr)


	def final_insert_row(self):
		#print('finish!')
		lk=self.index_change
		self.selectRow(self.row_inserts)
		sq_tb=list(filter(None,[self.model().index(self.row_inserts,a).data() for a in range(0,self.columnCount())]))
		if len(sq_tb)<4:
			self.error_insert('Одно из значений не введено!')
		else:
			if str(sq_tb[0]).isdigit()!=True:
				self.error_insert('Значение t не корректно!')
			else:
				if str(sq_tb[0]).isdigit()!=True:
					self.error_insert('Значение x0 не корректно!')
				else:
					for q in range(len(sq_tb)-2):sq_tb[q]=float(sq_tb[q])
					if sq_tb[0] in self.UNIQUIE_X[0]:
						self.error_insert('Данные t должны быть уникальными!')
					else:
						for v in range(len(sq_tb)):
							self.setter_items(sq_tb[v],self.row_inserts,v,self)
						self.updates_keys_for_table()
						self.UNIQUIE_X=self.get_values_table()
						self.CHANGE_TABLE.append({'number':[max(self.UNIQUIE_X[3])],'action':0,'data':[[[None,None,None,None],[sq_tb[0],sq_tb[1],'A'+str(self.rowCount()),max(self.UNIQUIE_X[3])]]]})					
						self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
						self.change=False
						self.update_changes()
						if self.back_forward_change_list==True:self.set_change_back_forward(lk)

		self.row_inserts=None
		self.insert_row=False
		self.blockSignals(False)
		self.check_file_save=True
		self.del_and_change_signal.emit(True)
		
		



	def set_focuses(self,var):
		self.focusable_edit.emit(var)



	def set_graph_form(self):
		self.blockSignals(True)
		xmin=str(self.ed_min_fx.text()).replace(',','.').strip()
		xmax=str(self.ed_max_fx.text()).replace(',','.').strip()
		form=str(self.ed_form_fx.text()).strip()
		count=str(self.ed_сount_fx.text()).strip()
		if form=='':
			QMessageBox.information(self,'Внимание!','Формула не введена!')
		else:
			if xmin==None or xmax==None or count==None:
				QMessageBox.information(self,'Внимание!','Одно из значений диапазона не введено!')
			else:
				if float(xmin)>float(xmax):
					QMessageBox.information(self,'Внимание!','Минимальное значение не может быть больше максимального!')
				else:
					if float(xmin)==float(xmax):
						QMessageBox.information(self,'Внимание!','Минимальное и максимальное значение не могут совпадать!')
					else:
						if str(form).count('(')!=str(form).count(')'):
							QMessageBox.information(self,'Внимание!','В формуле не совпадает количество скобок!')
						else:
							if self.rowCount()>0:
								self.setRowCount(0)
								self.UNIQUIE_X=[[],[],[],[]]
								self.CHANGE_TABLE=[]
							self.check_formulas_values=True
							spform=[float(xmin), float(xmax), int(count)]
							self.vf = ThreadFormul(spform,str(form))
							self.vf.finished.connect(self.set_vf_finish)
							self.vf.formul_datas.connect(self.set_vf_data)
							self.vf.start()
							self.check_file_save=True
					

	def set_vf_data(self,dat):
		self.edit1.setText(str(dat[0]))
		self.edit2.setText(str(dat[1]))
		self.add_to_table(1)


	def set_vf_finish(self):
		self.clear_edit1_edit2()
		self.del_and_change_signal.emit(True)
		self.check_formulas_values=False
		if self.rowCount()==0:
			QMessageBox.information(self,'Внимание!','Данная формула не корректна!')
			self.clear_all()
		else:
			if len(self.vf.errors)!=0:
				QMessageBox.information(self,'Внимание!','Данные построены, однако следующие данные при расчётах не корректны :  \n'+'\n'.join(self.vf.errors))
				self.vf.errors=[]
			else:
				QMessageBox.information(self,'Внимание!','Данные по формуле построены!')
		del self.vf




	
	def clear_all(self):
		self.cleared.emit(1)
		
	def debuging(self):
		self.pid_lk=[self.ed_pid_kp.text(),self.ed_pid_ki.text(),
			   self.ed_pid_kd.text()]
		if len(list(filter(None,self.pid_lk)))!=3:
			QMessageBox.information(self,'Внимание!','Одно из данных не указано!')
			self.pid_lk=[]
			return 0
		else:
			if self.rowCount()<2:
				QMessageBox.information(self,'Внимание!','Для построения PID должно быть не менее двух значений!')
				self.pid_lk=[]
				return 0
			else:
				if float(self.UNIQUIE_X[0][0])!=0:
					QMessageBox.information(self,'Внимание!','Первое значение t не начинается с 0!')
					self.pid_lk=[]
					return 0
				else:
					if '.' in self.pid_lk:
						QMessageBox.information(self,'Внимание!','Одно из значений не должно начинаться с точки!')
						self.pid_lk=[]
						return 0
					else:
						return 1



	def check_pid_form(self):
		if self.debuging()==1:
			self.timing=CheckTime(self.UNIQUIE_X[0])
			self.timing.finished.connect(self.check_pid_finish)
			self.timing.check_time.connect(self.check_pid_data)
			self.timing.start()

		
	def check_pid_data(self,s):
		self.pid_time*=s


	def check_pid_finish(self):
		if self.pid_time==0:
			self.ed_pid_t.clear()
			self.ed_pid_n.clear()
			QMessageBox.information(self,'Внимание!','Значения таблицы не находятся на равных промежутках!')
			self.pid_time=1
		else:
			self.ed_pid_t.setText(str(self.UNIQUIE_X[0][1]-self.UNIQUIE_X[0][0]))
			self.ed_pid_n.setText(str(self.rowCount()))
			self.but_pid.setEnabled(True)
			self.but_check_pid.setEnabled(False)
			
			QMessageBox.information(self,'Внимание!','Анализ таблицы завершён!')
			




	def set_pid_form(self):
		
		if self.debuging()==1:
			self.pid_lk.append(float(self.ed_pid_t.text()))
			self.pid_lk.append(int(self.ed_pid_n.text()))
			self.pid_data = ThreadPID(self.pid_lk,self,self.UNIQUIE_X)
			self.pid_data.pid_datas.connect(self.set_pid_data)
			self.pid_data.finished.connect(self.set_pid_finish)
			self.pid_data.start()	
		
			
		

	def set_pid_data(self,dat):
		self.pid_data.widget_pid.setter_one_items(dat[0],dat[1],dat[2])
		

	def set_pid_finish(self):
		self.pid_data.widget_pid.set_graph('red',3,'x(t)')
		self.pid_data.widget_pid.set_graph('blue',4,'x0(t)')
		plt.close()
		self.pid_data.widget_pid.save("D:/1_PID.xlsx")		
		
		self.pid_data.widget_pid.showMaximized()
		self.but_pid.setEnabled(False)
		self.but_check_pid.setEnabled(True)
		self.ed_pid_t.clear()
		self.ed_pid_n.clear()
		self.pid_data.widget_pid.show()
		
		

	def set_color_graph1(self):
		if self.color1.isChecked():
			self.colores.emit(True)



	def set_color_graph2(self):
		if self.color2.isChecked():
			self.colores.emit(False)






	def back_forward_remove(self,remove_rows):
		self.blockSignals(True)
		if len(remove_rows)==1:
			remove_rows=self.UNIQUIE_X[3].index(max(remove_rows))
			self.removeRow(remove_rows)
		else:
			remove_rows.sort()
			remove_rows.reverse()
			[self.removeRow(a) for a in remove_rows]
		self.blockSignals(False)




	def back_forward_save(self,state_param):
		
		lk=dict()
		print(state_param['number'])
		s=state_param['number']
		for v in range(len(state_param['number'])):
			lk.update({state_param['number'][v]:state_param['data'][v]})
		
		state_param['number'].sort()
		#state_param['number'].reverse()
		print(state_param['number'],lk)
		for v in range(len(state_param['number'])):
			state_param['data'][v]=lk[state_param['number'][v]]
		print(state_param['data'])



		for v in range(len(state_param['number'])):
			self.insertRow(state_param['number'][v])
			if state_param['data'][v][0][0]==None:
				state_param['data'][v].reverse()
			for q in range(len(state_param['data'][v][0])):
				self.setter_items(state_param['data'][v][0][q],state_param['number'][v],q,self)


		state_param['number']=s
		state_param['number'].reverse()
		for v in range(len(state_param['number'])):
			state_param['data'][v]=lk[state_param['number'][v]]
		
		#self.updates_keys_for_table()



	def back_forward_change(self,state_change):
		print(state_change['number'])
		state_change['data'][0].reverse()
		for v in range(len(state_change['data'][0][1])):
			self.setter_items(state_change['data'][0][1][v],state_change['number'][0],v,self)
		#self.updates_keys_for_table()


	def back_forward_table(self,state):
		
		if state['action']==0:#ADD
			print('Del')
			self.back_forward_remove(state['number'])
			return 1

		if state['action']==1:#DEL
			print('Add')
			self.back_forward_save(state)
			print(state)
			return 0
				
		if state['action']==2:#CHANGE
			print('Change')
			self.back_forward_change(state)
			return 2

		#функция для обработки откатов
		
	

	def back(self):
		self.blockSignals(True)
		
		self.back_forward_change_list=True


		self.but5.setEnabled(True)
		
		print(self.index_change)
		print(self.CHANGE_TABLE[self.index_change])

		self.CHANGE_TABLE[self.index_change]['action']=self.back_forward_table(self.CHANGE_TABLE[self.index_change])
		self.index_change-=1


		if self.index_change<self.CHANGE_TABLE.index(self.CHANGE_TABLE[0]):
			self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[0])
			self.but4.setEnabled(False)
		

		#if len(self.CHANGE_TABLE[self.index_change]['number'])>1:
		#	self.index_change-=1
		

		print(self.index_change)
		self.blockSignals(False)
		self.del_and_change_signal.emit(True)
		self.clear_edit1_edit2()
		self.updates_keys_for_table()
		self.check_file_save=True


	def forward(self):
		self.blockSignals(True)
		self.back_forward_change_list=True


		self.but4.setEnabled(True)

		print(self.index_change)		
		#	self.but5.setEnabled(False)
		#else:
		#	self.but4.setEnabled(True)
		self.index_change+=1

		if self.rowCount()==0:self.index_change-=1
		

		print(self.index_change,len(self.CHANGE_TABLE))

		if self.index_change==self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1]):
			self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
			self.but5.setEnabled(False)
		#if len(self.CHANGE_TABLE[self.index_change]['number'])>1:
		#	self.CHANGE_TABLE[self.index_change]['action']=0
		self.CHANGE_TABLE[self.index_change]['action']=self.back_forward_table(self.CHANGE_TABLE[self.index_change])
		#self.index_change+=1
		print(self.index_change)
		self.sorting_table()
		self.blockSignals(False)
		self.del_and_change_signal.emit(True)
		self.updates_keys_for_table()
		self.clear_edit1_edit2()
		self.check_file_save=True


	def set_change_back_forward(self,data):
		vr_change=self.CHANGE_TABLE[-1]
		del self.CHANGE_TABLE[data+1::]
		self.CHANGE_TABLE.append(vr_change)
		self.back_forward_change_list=False
		self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
		self.but5.setEnabled(False)
		if self.rowCount()==1:self.but4.setEnabled(True)
		self.updates_keys_for_table()
		self.clear_edit1_edit2()
		

	def add_to_table(self,k=None):
		#global UNIQUIE_X
		self.clearSelection()
		lk=self.index_change
		self.blockSignals(True)
		first_symbol=['+','-']

		if len(self.edit1.text())==0 or len(self.edit2.text())==0:
			QMessageBox.information(self,"Внимание!","Некорректные данные!")
		else:
			if str(self.edit1.text())=='+' or str(self.edit1.text())=='-' or str(self.edit1.text()).endswith('.')==True:
				QMessageBox.information(self,"Внимание!","Некорректные данные t!")
			else:
				if str(self.edit2.text())=='+' or str(self.edit2.text())=='-' or str(self.edit2.text()).endswith('.')==True:
					QMessageBox.information(self,"Внимание!","Некорректные данные x0!")
			
				else:
					x=float(self.edit1.text().replace(',','.').replace('+',''))
					y=float(self.edit2.text().replace(',','.').replace('+',''))
					rowPosition=int(0)
					if x in self.UNIQUIE_X[0] and self.check_formulas_values==False:
						QMessageBox.information(self,"Внимание!","Данные t должны быть уникальными!")
					else:
						rowPosition = self.rowCount()
						self.insertRow(rowPosition)
						self.setter_items(x,self.rowCount()-1,0,self)
						self.setter_items(y,self.rowCount()-1,1,self)
						self.setter_items('A'+str(self.rowCount()),self.rowCount()-1,2,self)
						self.setter_items(rowPosition,self.rowCount()-1,3,self)
						self.UNIQUIE_X=self.get_values_table()
				
						if self.index_change==0:self.but4.setEnabled(True)
						self.clear_edit1_edit2()
						self.edit1.setFocus()


					self.blockSignals(False)
					self.sorting_table()
					self.UNIQUIE_X=self.get_values_table()
					self.CHANGE_TABLE.append({'number':[max(self.UNIQUIE_X[3])],'action':0,'data':[[[None,None,None,None],[x,y,'A'+str(self.rowCount()),max(self.UNIQUIE_X[3])]]]})
					self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
					if k!=1:self.del_and_change_signal.emit(True)
					if self.back_forward_change_list==True:self.set_change_back_forward(lk)
					self.check_file_save=True



	def get_values_table(self):#++++++
		col_value=[[],[],[],[]]
		self.updates_keys_for_table()
		for column in range(self.columnCount()):
			for row in range(self.rowCount()):
				s=self.item(row, column).text()
				if column<2:
					col_value[column].append(float(s))
				elif column==2:
					col_value[column].append({str(s):pyqtgraph.TextItem(str(s),color=(0, 0, 0))})
				else:
					col_value[column].append(int(s))
		return col_value











	

	def click_for_item(self):#УБРАТЬ
		self.but1.setEnabled(False)
		self.change=True
		#print(self.currentItem().text(),'red',self.currentItem().row(),self.currentItem().column())
		self.prevt=float(self.currentItem().text())
		print(self.prevt)



	def edit_for_table(self):
		lk=self.index_change
		if len(self.selectionModel().selectedRows())!=0:
			self.nextt=self.currentItem().text()
			print(self.nextt)
			self.blockSignals(True)
			if self.check_float(str(self.nextt))==False:
				QMessageBox.information(self,"Внимание!","Будет установлено предыдущее значение! Введённое значение не корректно!")
				self.nextt=float(self.prevt)
			else:
				if self.currentItem().column()==0 and float(self.nextt) in self.UNIQUIE_X[0]:
					QMessageBox.information(self,"Внимание!","Будет установлено предыдущее значение! Значения х должны быть уникальны!")
					self.nextt=float(self.prevt)
				
				else:
					self.nextt=float(self.nextt)
					if self.change==True:
						self.CHANGE_TABLE.append({'number':[self.currentRow()],'action':2,'data':[[[self.item(self.currentRow(),a).text() for a in range(0,self.columnCount()) if a!=self.currentColumn()],[self.item(self.currentRow(),a).text() for a in range(0,self.columnCount()) if a!=self.currentColumn()]]]})
						prev_next=[self.prevt,self.nextt]
						for v in range(len(prev_next)):self.CHANGE_TABLE[-1]['data'][0][v].insert(self.currentItem().column(),prev_next[v])
						self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])



			if self.back_forward_change_list==True:self.set_change_back_forward(lk)
			self.change=False


			self.clearSelection()
			self.setter_items(self.nextt,self.currentItem().row(),self.currentItem().column(),self)
			self.blockSignals(False)
			
			self.check_file_save=True
			self.del_and_change_signal.emit(True)
			
			




















			







	def setter_items(self,text,r,c,tbl):
		if c<2:
			text=float(text)
		if c==2:
			text=str(text)
		if c==3:
			text=int(text)
		it = QTableWidgetItem(str(text))
		if c>=2:
			it.setFlags(it.flags()^QtCore.Qt.ItemIsEditable)
			it.setToolTip('Эта ячейка доступна только для чтения!')
		it.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
		tbl.setItem(r,c,it)



	def set_table(self,x):
		for column in range(len(x)):
			for row in range(len(x[column])):
				if column==2:
					self.setter_items(str(list(x[column][row].keys())[0]),row,column,self)
				if column<2 or column==len(x)-1:
					self.setter_items(str(x[column][row]),row,column,self)
				



	def printed(self,k):
		self.print_tb.close()
		printer = Qt.QPrinter()
		dlg=Qt.QPrintDialog(printer)
		if dlg.exec() == Qt.QDialog.Accepted:
			painter1=QPainter()
			painter1.begin(printer)
			k.render(painter1)
			painter1.end()
		else:
			QMessageBox.information(self,"Внимание!","Печать таблицы отменена!")
	

	def get_h_w(self,k):
		w = int(0)
		h = int(0)
		for v in range(0,k.columnCount()):
			w += k.columnWidth(v)
		for v in range(0,k.rowCount()):
			h += k.rowHeight(v)
		return [w,h+k.horizontalHeader().height()]


	def dialog_print_close(self):
		self.print_tb.close()
		self.print_tb.destroy()

	#def dialog_print_close_2(self):
	#	self.print_tb1.close()
	#	self.print_tb.show()	

	def dialog_print_all(self):
		lkst=list()
		for v in range(self.rowCount()):lkst.append(v)
		self.set_print_table(lkst)




	def set_print_table(self,k):
		self.table_pr=QTableWidget()
		self.create_table(self.table_pr,3,['x','y','points'])
		self.table_pr.resize(self.width(), self.height())
		self.table_pr.setRowCount(self.rowCount())
		self.table_pr.setColumnCount(self.columnCount()-1)
		for q in range(0,self.table_pr.columnCount()):
			for v in range(0,self.table_pr.rowCount()):
				if int(v) in k:
					self.setter_items(str(self.item(v,q).text()),v,q,self.table_pr)
		
		sq_rem=list()
		for v in range(0,self.table_pr.rowCount()):
			item1=QTableWidgetItem(self.table_pr.item(v,0))
			if len(item1.text())==0:
				print(v)
				sq_rem.append(v)
				


		if len(sq_rem)!=0:
			#print(sq_rem)
			sq_rem.sort()
			#print(sq_rem)
			sq_rem.reverse()
			#print(sq_rem)
			print(self.table_pr.rowCount())
			for v in range(len(sq_rem)):self.table_pr.removeRow(sq_rem[v])
			print(self.table_pr.rowCount())
		
		self.table_pr.resizeRowsToContents()
		self.table_pr.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.table_pr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.table_pr.resizeRowsToContents()
		gethw=self.get_h_w(self.table_pr)
		self.table_pr.resize(gethw[0],gethw[1])
		self.printed(self.table_pr)



	def dialog_print_range(self):
		lkst=self.selectionModel().selectedRows()
		self.clearSelection()
		if len(lkst)==0:
			QMessageBox.information(self,"Внимание!","Данные не выделены!")
		else:
			for v in range(len(lkst)): lkst[v]=int(lkst[v].row())
			lkst.sort()
			self.set_print_table(lkst)
			
		

	def select_print_table(self):
		self.print_tb=QDialog()
		self.print_tb.setMinimumWidth(250)
		layout = QFormLayout()
		first=QPushButton('Распечать все данные')
		second=QPushButton('Распечать выделенные данные')
		first.clicked.connect(self.dialog_print_all)
		second.clicked.connect(self.dialog_print_range)
		buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel , self)
		buttonBox.rejected.connect(self.dialog_print_close)
		self.print_tb.setWindowTitle('Печать данных')
		layout.addRow(first)
		layout.addRow(second)
		layout.addWidget(buttonBox)
		self.print_tb.setLayout(layout)
		if self.rowCount()==0:
			QMessageBox.information(self,"Внимание!","Таблица пуста!")
			self.dialog_print_close()
		else:
			self.print_tb.exec_()

	def select_save_table_as(self):
		self.save_table(1)

	def select_save_table(self):
		self.save_table(2)

	def check_param(self,s):
		if s is not None:
			return True
		else:
			return False

	def set_params_pid(self,s):
		for v in range(len(s)):
			if s[v].startswith('Кп')==True:
				q=str(str(s[v]).split(' ')[1])
				self.ed_pid_kp.setText(q)
			if s[v].startswith('Ки')==True:
				q=str(str(s[v]).split(' ')[1])
				self.ed_pid_ki.setText(q)
			if s[v].startswith('Кд')==True:
				q=str(str(s[v]).split(' ')[1])
				self.ed_pid_kd.setText(q)
		

	def write_table(self,s):
		lkst=list()
		for v in range(0,self.rowCount()):
			lst_vr=list()
			for q in range(0,self.columnCount()-1):
				lst_vr.append(str(self.item(v,q).text()))
			lkst.append(' '.join(lst_vr))
		f=open(s,'w')
		parameters=[str(self.ed_pid_kp.text()),str(self.ed_pid_ki.text()),str(self.ed_pid_kd.text())]
		key_parameters=[str('Кп'),str('Ки'),str('Кд')]
		
		for v in range(len(parameters)):
			if self.check_param(str(parameters[v]))==True:
				lkst.append(' '.join([str(key_parameters[v]),str(parameters[v])]))

		for v in range(len(lkst)):
			f.write(str(lkst[v])+'\n')
		f.close()
		self.file_path.emit(s)




	def save_table(self,change):
		if self.rowCount()<0:
			QMessageBox.information(self,"Внимание!","Таблица пуста!")
		else:
			if change==1:
				save=SaveFile()
				save.start_save()
				save_tb=save.get_name_path()
				save.close()
				if len(save_tb)!=0:
					self.write_table(save_tb)
				self.save_open_file_path=save_tb
			if change==2:
				s=None
				if self.save_open_file_path=='':
					s=str(str(os.path.abspath(os.curdir)).split('\'')[0]).replace('\\','/')+'/1.Иванов'
				else:
					s=self.save_open_file_path
				self.write_table(s)
				QMessageBox.information(self,'Внимание!','Файл сохранён по пути: '+s)
			self.check_file_save=False


	def del_from_table(self):
		
		
		index_for_table=list()
		index_save_change=list()
		
		
		lk=self.index_change

		for ind in self.selectionModel().selectedRows():
			indexed=QtCore.QPersistentModelIndex(ind)
			index_for_table.append(indexed)
		if len(index_for_table)==0:
			QMessageBox.information(self,"Внимание!","Ни одна строка не выбрана!")
		else:


			#print(index_for_table)
			for idx in index_for_table:
				index_save_change.append({idx.row():[[self.item(idx.row(),a).text() for a in range(0,self.columnCount())],[None,None,None]]})
				
			#[[[None,None,None],[x,y,'A'+str(self.rowCount())]]]
			for idx in index_for_table:
				self.removeRow(idx.row())
			self.CHANGE_TABLE.append({'number':[list(a.keys())[0] for a in index_save_change],'action':1,'data':[list(a.values())[0] for a in index_save_change]})
			self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
			
			self.UNIQUIE_X=self.get_values_table()
			self.blockSignals(True)
			self.updates_keys_for_table()
			self.set_table(self.UNIQUIE_X)
			self.blockSignals(False)
			self.del_and_change_signal.emit(True)
			
			self.check_file_save=True
			if self.back_forward_change_list==True:self.set_change_back_forward(lk)
		
		self.edit1.setFocus()
			




	
	def updates_keys_for_table(self):
		for v in range(self.rowCount()):
			self.setter_items('A'+str(v+1),v,2,self)
		#self.UNIQUIE_X=self.get_values_table()


	def menu_for_table(self,pos):
		self.menu_for_tabled.popup(QCursor.pos())
		self.clear_edit1_edit2()


	def create_table(self,tables,k,s):
		tables.setColumnCount(k)
		tables.setHorizontalHeaderLabels(s)
		tables.setSelectionBehavior(QAbstractItemView.SelectRows)
		tables.verticalHeader().setVisible(False)
		tables.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
	








	def change_value_by_mouse_move(self,value):#добавление изменений после перемещения мышью

		lk=self.index_change
		lk_value=[]
		
		for v in range(len(self.CHANGE_TABLE)):
			if self.CHANGE_TABLE[v]['number'][0]==value:# and self.CHANGE_TABLE[v]['action']==2:
				lk_value.append(self.CHANGE_TABLE[v])
		lk_value=lk_value[-1]
		
		self.CHANGE_TABLE.append({'number': [value], 'action': 2, 'data': [[lk_value['data'][0][1], [self.UNIQUIE_X[0][value], self.UNIQUIE_X[1][value], lk_value['data'][0][1][2],lk_value['data'][0][1][3]]]]})
		self.index_change=self.CHANGE_TABLE.index(self.CHANGE_TABLE[-1])
		if self.back_forward_change_list==True:self.set_change_back_forward(lk)

	




	def clear_data_table(self):
		self.setRowCount(0)
		self.UNIQUIE_X=[[],[],[],[]]
		self.CHANGE_TABLE=[]
			

	def clear_edit1_edit2(self):
		self.edit1.clear()
		self.edit2.clear()
	

	def check_file(self,s):
		s1=s.split('.')[-1]
		if re.search(r'[а-яА-Я]',s1):
			return 1
		else:
			return 0
		


	def open_table(self):
		if self.check_file_save==True:
			self.what_save()
		save_tb=str(QFileDialog().getOpenFileName(self,"Открыть файл данных",QDir().currentPath(),"All Files (*.*)")[0])
		if len(save_tb)==0:
			QMessageBox.information(self,"Внимание!","Файл не выбран!")
		else:
			if self.check_file(save_tb)==0:
				QMessageBox.information(self,"Внимание!","В расширении файла должны быть только русские буквы!")
			else:
				
				self.setRowCount(0)
				self.UNIQUIE_X=[[],[],[]]
				self.CHANGE_TABLE=[]

				f=open(save_tb,'r')
				lsfill=f.read().splitlines()
				f.close()

				lk_parametr=[]
				for v in range(len(lsfill)):
					if lsfill[v].startswith('Кп')==True or lsfill[v].startswith('Ки')==True or lsfill[v].startswith('Кд')==True:
						lk_parametr.append(lsfill[v])
						lsfill[v]=None
				lsfill=list(filter(None,lsfill))


				for v in range(len(lsfill)):
					lsfill[v]=str(lsfill[v]).split(' ')
					if len(lsfill[v])!=3:lsfill[v]=None

				lsfill=list(filter(None,lsfill))
				ls_chek_unique_vr=[]
				ls_chek_unique=[]

				for v in range(len(lsfill)):
					if lsfill[v][0] not in ls_chek_unique_vr:
						ls_chek_unique.append(lsfill[v])
						ls_chek_unique_vr.append(lsfill[v][0])
				lsfill=ls_chek_unique

				if len(lk_parametr)!=0:
					self.set_params_pid(lk_parametr)

				for v in range(len(lsfill)):
					self.edit1.setText(str(lsfill[v][0]))
					self.edit2.setText(str(lsfill[v][1]))
					self.add_to_table(1)
				self.del_and_change_signal.emit(True)
				self.clear_edit1_edit2()
				self.check_file_save=False
				self.save_open_file_path=save_tb
				self.file_path.emit(str(self.save_open_file_path))


	def check_float(self,s):
		s=s.replace('-','').replace(',','').strip()
		if str(s).strip().isdigit()==True or str(s).strip().isnumeric()==True:
			return True
		else:
			return False
		

	def what_save(self):
		saved=QMessageBox()
		saved.setWindowTitle('Внимание!')
		saved.setText('Вы хотите сохранить последние изменения?')
		saved.addButton(QPushButton('Сохранить'), QtGui.QMessageBox.YesRole)
		saved.addButton(QPushButton('Не сохранять'), QtGui.QMessageBox.NoRole)
		#saved.addButton(QPushButton('Отмена'), QtGui.QMessageBox.RejectRole)
		s=saved.exec()
		if s==0:
			self.save_table(2)
		if s==1:
			self.check_file_save=False
			
	
class Graph(pyqtgraph.GraphItem,QObject):
	coord_point = pyqtSignal(float,float,int)

	def __init__(self):
		self.dragPoint = None
		self.dragOffset = None
		pyqtgraph.GraphItem.__init__(self)
		
		

	def setData(self, **kwds):
		self.data = kwds
		
		
		if 'pos' in self.data:
			npts = self.data['pos'].shape[0]
			
			self.data['adj'] = numpy.column_stack(
				(numpy.arange(0, npts-1), numpy.arange(1, npts))
			)
			self.data['data'] = numpy.empty(npts, dtype=[('index', int)])
			self.data['data']['index'] = numpy.arange(npts)
		self.updateGraph()

	def updateGraph(self):
		pyqtgraph.GraphItem.setData(self, **self.data)
	

	def mouseDragEvent(self, event):
		if event.button() != QtCore.Qt.LeftButton:
			event.ignore()
			return

		if event.isStart():
			pos = event.buttonDownPos()
			print(event)
			pts = self.scatter.pointsAt(pos)
			if len(pts) == 0:
				event.ignore()
				return
				
			self.dragPoint = pts[0]
			ind = pts[0].data()[0]
			self.dragOffset = self.data['pos'][ind][1] - pos[1]

		elif event.isFinish():
			self.dragPoint = None	
			return
		else:
			if self.dragPoint is None:
				event.ignore()
				return
		ind = self.dragPoint.data()[0]
		self.data['pos'][ind][1] = event.pos()[1] + self.dragOffset
		self.data['pos'][ind][0] = event.pos()[0] + self.dragOffset
		self.updateGraph()
		event.accept()
		self.coord_point.emit(event.pos().x(),event.pos().y(),self.dragPoint.data()[0])


class Scaled(QWidget,QObject):
	set_scale=pyqtSignal(int)

	def __init__(self,*args):
		super().__init__()


		self.scale_name=[QLabel('tmin'),QLabel('tmax'),QLabel('x0min'),QLabel('x0max')]#,]


		self.scale_value=[QLineEdit(),QLineEdit(),QLineEdit(),QLineEdit()]

		self.scale_button=[QPushButton('Установить масштаб'),QPushButton('Сбросить масштаб')]
		self.scale_button[0].clicked.connect(self.set_scaled)
		self.scale_button[-1].clicked.connect(self.set_scaled_cls)
		self.layout_1=QHBoxLayout()
		self.layout_2=QHBoxLayout()
		self.set_to_layout(self.layout_1,self.scale_name,1)
		self.set_to_layout(self.layout_2,self.scale_button,2)



	def set_scaled(self):
		self.set_scale.emit(1)
		
	def set_scaled_cls(self):
		self.set_scale.emit(2)
		

	def set_to_layout(self,lay,sp,key):
		for v in range(len(sp)):
			if key==1:
				self.scale_value[v]=Regex.set_validator("^[-+]?[0-9]*[.,]?[0-9]+$",self.scale_value[v])
				lay.addWidget(sp[v])
				lay.addWidget(self.scale_value[v])
			else:
				lay.addWidget(sp[v])



	def set_scale_values(self,min,max,object1,s1,s2,key):
		if min!='' and max!='':
			if min<max and min!=max:
				if key==1:object1.setXRange(int(min),int(max))
				if key==2:object1.setYRange(int(min),int(max))
			else:
				QMessageBox.information(self,"Внимание!",s1)
		else:
			QMessageBox.information(self,"Внимание!",s2)
				




class Graphic(pyqtgraph.PlotWidget,pyqtgraph.GraphicsWindow,QObject):#,pyqtgraph.QGraphicsItems):
	final_drag = pyqtSignal(bool)
	check=pyqtSignal(int,list)
	graph_print=pyqtSignal(int)
	add_point_scene=pyqtSignal(list)

	def __init__(self):
		pyqtgraph.setConfigOption('background', 'w')
		pyqtgraph.setConfigOption('foreground', 'k')

		pyqtgraph.setConfigOptions(antialias=True)

		super().__init__()
		self.check_control=False
		#self.check_control_lk=[]
		self.setLabel('left', 'x0')#, units='V')
		self.setLabel('bottom', 't')#, units='s')
		self.setMenuGraph()
		self.setMenuEnabled(False)
		self.setMouseTracking(True)
		self.scene().sigMouseMoved.connect(self.onMove)
		self.i=int(0)
		self.combobox=QComboBox()
		self.combobox.addItem('Координаты мыши')
		self.combobox.addItem('Координаты точек')
		self.combobox.currentIndexChanged.connect(self.checkbox_clicked)
		self.checked_point=True

		self.lb_x=QLabel('t')
		self.lb_y=QLabel('x0')
		
		self.edit_x=QLineEdit()
		self.edit_y=QLineEdit()
		self.edit_x.setReadOnly(True)
		self.edit_y.setReadOnly(True)
		

		self.layout=QHBoxLayout()
		self.layout.addWidget(self.combobox)
		self.layout.addWidget(self.lb_x)
		self.layout.addWidget(self.edit_x)
		self.layout.addWidget(self.lb_y)
		self.layout.addWidget(self.edit_y)


	def checkbox_clicked(self,val):
		if val==1:
			self.checked_point=False
			self.check.emit(1,[None,None])
			self.final_drag.emit(True)
		if val==0:
			self.checked_point=True
			self.check.emit(0,[None,None])
			self.final_drag.emit(True)
		


	def setMenuGraph(self):
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested[QtCore.QPoint].connect(self.menu_for_graph)
		self.menu_for_graphed=QMenu()
		self.act1=QAction('Распечатать график')
		self.act2=QAction('Сохранить график')
		self.menu_for_graphed.addActions([self.act1,self.act2])
		self.act1.triggered.connect(self.print_graph_signal)
		self.act2.triggered.connect(self.save_graph_signal)


	def menu_for_graph(self):
		self.menu_for_graphed.popup(QCursor.pos())


	def print_graph_signal(self):
		self.graph_print.emit(1)

	def save_graph_signal(self):
		self.graph_print.emit(2)
	

	def print_graph(self):
		size=QRectF(self.boundingRect()).getCoords()
		im_scene=QImage(size[-2],size[-1],QtGui.QImage.Format.Format_ARGB32)
		im_scene.fill(0)
		painter=QPainter()
		painter.begin(im_scene)
		self.render(painter)
		painter.end()
		printer = Qt.QPrinter()
		dlg=Qt.QPrintDialog(printer)
		if dlg.exec() == Qt.QDialog.Accepted:
			img=QImage(im_scene)
			painter1=QPainter(printer)
			painter1.drawImage(0,0,img)
			painter1.end()
		else:
			QMessageBox.information(self,"Внимание!","Печать графика отменена!")


	def save_graph(self):
		path_for_save_graph = str(QFileDialog().getSaveFileName(self,"Сохранить график",QDir().currentPath(),"Изображения (*.jpg);;Изображения (*.png)")[0])
		width_and_height=QRectF(self.boundingRect()).getCoords()
		if len(path_for_save_graph)==0:
			QMessageBox.information(self,"Внимание!","Имя файла не указано!")
		else:
			plt=self
			exporter = pyqtgraph.exporters.ImageExporter(plt.plotItem)
			exporter.params.param('width').setValue(width_and_height[-2]) 
			exporter.params.param('height').setValue(width_and_height[-1]) # save to file 
			exporter.export(path_for_save_graph)




	def onMove(self,event):
		if self.checked_point==True:
			self.check.emit(0,[self.getPlotItem().vb.mapSceneToView(QPointF(event.x(),event.y())).x(),
				self.getPlotItem().vb.mapSceneToView(QPointF(event.x(),event.y())).y()])
		
		
	def leaveEvent(self,event):
		self.check.emit(2,[None,None])


	def mouseReleaseEvent(self,event):
		print('Вы отпустили кнопку со сцены')
		if self.check_control==False:
			self.final_drag.emit(False)
	

class ComponentsLocation(QWidget):
	def __init__(self,*args):
		super().__init__()
		self.grides=QGridLayout()
		self.setMaximumHeight(100)
		self.setLayout(self.grides)



class Diplom(QWidget):
	
	def __init__(self,*args):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.grid=QGridLayout()
		self.men=QVBoxLayout()
		self.setAcceptDrops(True)
		self.text_point=[]
		self.men1=QHBoxLayout()
		self.men2=QHBoxLayout()
		self.men4=QHBoxLayout()
		self.setWindowTitle('Новый   '+'Цифровая технология задающего воздействия PID регулятора')
		self.setGeometry(120,120,1750,550)
		self.setLayout(self.grid)
		self.graph=Graph()
		self.view=Graphic()
	
		self.table=Table()
		self.table.file_path.connect(self.set_title)
		self.menus=MainMenu()
		self.menus.menu_value.connect(self.state_main_menu)
		self.scale=Scaled()
		self.view.add_point_scene.connect(self.new_point)





		self.tab1=QTabWidget()
		self.tab2=QTabWidget()
		self.tab1.setMaximumHeight(90)
		self.tab2.setMaximumHeight(90)
		
		
		self.widg1=ComponentsLocation()
		self.widg2=ComponentsLocation()
		self.widg3=ComponentsLocation()
		self.widg4=ComponentsLocation()
		self.widg5=ComponentsLocation()
		
		self.tab1.addTab(self.widg1,"Моделирование x0(t)")
		self.tab1.addTab(self.widg2,"Добавление точек")
		self.tab1.addTab(self.widg3,"Моделирование PID регулирования")
		self.tab2.addTab(self.widg4,"Редактирование графика")
		self.tab2.addTab(self.widg5,"Масштабирование графика")
		self.tab1.currentChanged.connect(self.changed_tab_one)
		self.tab2.currentChanged.connect(self.changed_tab_two)


		self.but2=QPushButton('Очистить')
		self.but2.clicked.connect(self.clear_all)
		self.table.cleared.connect(self.clear_all)

		self.men4.addWidget(self.table.but1)
		self.men4.addWidget(self.but2)
		self.men4.addWidget(self.table.but4)
		self.men4.addWidget(self.table.but5)
		

		self.men1.addWidget(self.table.line1)
		self.men1.addWidget(self.table.edit1)
		self.men1.addSpacing(270)
		self.men2.addWidget(self.table.line2)
		self.men2.addWidget(self.table.edit2)
		self.men2.addSpacing(270)


		#self.men3.addWidget(self.table.color1)
		#self.men3.addWidget(self.table.color2)
		#self.men3.addSpacing(270)



		self.widg1.grides.addLayout(self.table.layoutes1,0,0)
		self.widg1.grides.addLayout(self.table.layoutes2,1,0)
		


		self.widg2.grides.addLayout(self.men1,0,0)
		self.widg2.grides.addLayout(self.men2,1,0)
		
		
		self.widg3.grides.addLayout(self.table.lay_pid_1,0,0)
		self.widg3.grides.addLayout(self.table.lay_pid_2,1,0)
		


		self.widg4.grides.addLayout(self.view.layout,0,0)
		self.widg4.grides.addWidget(self.table.color1,0,1)
		self.widg4.grides.addLayout(self.men4,1,0)
		self.widg4.grides.addWidget(self.table.color2,1,1)
		

		self.widg5.grides.addLayout(self.scale.layout_1,0,0)
		self.widg5.grides.addLayout(self.scale.layout_2,1,0)
		





		

		



		self.colored=True
		self.table.colores.connect(self.set_color)

		self.view.plotItem.showGrid(alpha=23)


		
		
		self.view.setMouseTracking(True)
		

		

		self.grid.setMenuBar(self.menus.menu)
		self.grid.addWidget(self.table,1,0)
		self.grid.addWidget(self.view,1,1)


		self.grid.addWidget(self.tab1,0,0)
		self.grid.addWidget(self.tab2,0,1)
		
		self.graph.coord_point.connect(self.start_thread)
		self.table.del_and_change_signal.connect(self.set_finish_table)
		self.view.check.connect(self.check_coordinates)
		self.view.graph_print.connect(self.exec_graph)
		self.scale.set_scale.connect(self.check_scale)


		self.point_to_change=None
		self.point_flag=False
		self.sheck_false=int()
		self.cord=list()
		self.set_scale_change=int(2)
		self.key=1
		self.set_color(True)
		self.table.edit1.setFocus()#table.ed_form_fx	
		self.table.focusable_edit.connect(self.on_focus)
		self.show()
	

	def set_title(self,s):
		self.setWindowTitle(s+'   '+'Цифровая технология задающего воздействия PID регулятора')
		
	def changed_tab_two(self):
		self.key=1

	def changed_tab_one(self,x):
		self.key=1
		if x==1:
			self.table.edit1.setFocus()



	def state_main_menu(self,value):
		if value==0:
			self.table.open_table()
		if value==1:
			self.table.select_save_table()
		if value==2:
			self.table.select_save_table_as()
		if value==3:
			self.close()
		if value==4:
			self.clear_all()


	def new_point(self,par1):
		self.table.edit1.setText(str(float(par1[0]))[0::])
		self.table.edit2.setText(str(float(par1[1]))[0::])
		self.table.add_to_table()
		
		
	def exec_graph(self,state):
		if state==1:self.view.print_graph()
		if state==2:self.view.save_graph()
			

	def on_focus(self,var):
		self.key=var
		

	def keyPressEvent(self,event):
		if event.key()==QtCore.Qt.Key_Return:
			if self.tab1.currentIndex()==1:
				if self.key==0:
					self.table.edit1.setFocus()
				if self.key==1:
					self.table.edit2.setFocus()
				if self.key==2:
					self.table.add_to_table()
					self.key=0
				self.key+=1
			else:
				self.key=1





	def set_color(self,s):
		self.colored=s
		if self.table.rowCount()>0:self.set_graph()


	def check_scale(self,k):
		self.set_scale_change=k
		if k==1:
			self.view.autoRange(False)
			vr_scal=[a.text() for a in self.scale.scale_value]
			if len(list(filter(None,vr_scal)))==0:
				QMessageBox.information(self,"Внимание!","Все данные пусты!")
				self.view.autoRange(True)
			else:
				self.scale.set_scale_values(vr_scal[0],vr_scal[1],self.view,"Некорректные данные t!","Данные t не указаны!",1)
				self.scale.set_scale_values(vr_scal[2],vr_scal[3],self.view,"Некорректные данные x0!","Данные x0 не указаны!",2)
		if k==2:
			self.view.autoRange(True)


	def check_coordinates(self,stat,coor):
		if stat==0:
			self.sheck_false=stat
			if coor[0]!=None:
				self.cord=coor
				self.view.edit_x.setText(str(coor[0]))
				self.view.edit_y.setText(str(coor[1]))
			
		if stat==2:
			self.sheck_false=stat
			self.view.edit_x.clear()
			self.view.edit_y.clear()

		if stat==1:
			self.sheck_false=stat
			self.view.edit_x.clear()
			self.view.edit_y.clear()
		



	def clear_all(self):
		if self.table.check_file_save==True:
			self.table.what_save()
		
		self.table.clear_data_table()
		self.view.clear()
		self.table.clear_edit1_edit2()
		self.set_graph_to_scene()
		self.table.but4.setEnabled(False)
		self.table.but5.setEnabled(False)
		self.view.edit_x.clear()
		self.view.edit_y.clear()
		self.table.ed_max_fx.clear()
		self.table.ed_form_fx.clear()
		self.table.ed_min_fx.clear()
		self.table.ed_сount_fx.clear()
		self.table.ed_pid_kp.clear()
		self.table.ed_pid_ki.clear()
		self.table.ed_pid_kd.clear()
		self.table.ed_pid_t.clear()
		self.table.ed_pid_n.clear()
		[a.clear() for a in self.scale.scale_value]
		self.check_file_save=False
		self.save_open_file_path=''



		


	def set_graph_to_scene(self):
		s_combo=self.view.combobox.currentIndex()
		self.view=Graphic()
		self.view.add_point_scene.connect(self.new_point)
		self.view.check.connect(self.check_coordinates)
		self.view.graph_print.connect(self.exec_graph)
		self.view.combobox.setCurrentIndex(s_combo)
		self.grid.addWidget(self.view,1,1)
		

		self.widg4.grides.addLayout(self.view.layout,0,0)
		
		self.view.lb_x.clear()
		self.view.lb_y.clear()
		self.cord=[]

		



	def start_thread(self,value_x,value_y,point):#НАЧАЛО ОБРАБОТКИ ПОТОКА
		self.table.blockSignals(True)
		self.table.clear_edit1_edit2()
		self.point_to_change=point
		self.point_flag=True
		self.table.UNIQUIE_X[0][point]=value_x
		self.table.UNIQUIE_X[1][point]=value_y
		self.table.UNIQUIE_X[2][point][str(list(self.table.UNIQUIE_X[2][point].keys())[0])].setPos(value_x,value_y)
		self.table.set_table(self.table.UNIQUIE_X)
		self.table.selectRow(point)
		self.table.setStyleSheet("QTableView {selection-background-color:#FFF000; selection-color:#000FFF;}")



	def set_finish_table(self,sec):
		self.table.blockSignals(False)
		#print(self.point_to_change)
		print('Конец перетаскивания!')#КОНЕЦ ОБРАБОТКИ ПОТОКА
		if self.point_flag==True:
			self.table.change_value_by_mouse_move(self.point_to_change)
			self.point_flag=False

		#print(self.table.CHANGE_TABLE[-1])
		self.table.clearSelection()
		self.set_graph()


	def mousePressEvent(self, event):
		self.table.setDisabled(True)
		self.table.setDisabled(False)
		self.table.clearSelection()
		self.table.clear_edit1_edit2()
		

	def set_graph(self):
		self.sheck_false=self.sheck_false
		#else:
		#self.view.clear()
		self.table.setStyleSheet("QTableView {selection-background-color:#1E90FF; selection-color:#ffffff;}")
		
		self.table.UNIQUIE_X=self.table.get_values_table()
		
		self.set_graph_to_scene()
		pos = numpy.column_stack((self.table.UNIQUIE_X[0], self.table.UNIQUIE_X[1]))
		
		
		if self.colored==True:
			self.graph.setData(pos=pos, size=10, pxMode=True,pen=pyqtgraph.mkPen((1,2),width=3))
		else:
			self.graph.setData(pos=pos, size=10, pxMode=True,pen=pyqtgraph.mkPen('w',width=3))

		self.view.addItem(self.graph)
		self.view.final_drag.connect(self.set_finish_table)
		

		for i,j,k,p in zip(*self.table.UNIQUIE_X):
			k[str(list(k.keys())[0])].setPos(i, j)
			if self.sheck_false==1:
				k[str(list(k.keys())[0])].setToolTip('t='+str(i)+','+'x0='+str(j))
			self.view.addItem(k[str(list(k.keys())[0])])
		
		if self.table.rowCount()==1:
			self.table.but4.setEnabled(True)

		self.table.but1.setEnabled(True)
		self.check_scale(self.set_scale_change)
		self.table.edit1.setFocus()
		self.key=1
		self.table.clear_edit1_edit2()


	

	def closeEvent(self,event):
		if self.table.check_file_save==True:
			self.table.what_save()
		closed = QMessageBox.question(self,"Выход","Вы хотите выйти?",QMessageBox.Ok|QMessageBox.Cancel)
		if closed == QMessageBox.Ok:
			event.accept()
		else:
			event.ignore()


if __name__=='__main__':
	app=QApplication(sys.argv)
	exe=Diplom()
	sys.exit(app.exec_())