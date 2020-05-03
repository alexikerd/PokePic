import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import tkinter.font as tkFont
import os
from os import path
import cv2
import pickle
from PIL import Image, ImageTk, ImageChops

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors

import face_recognition as fr



knn = pickle.load(open("Models/knn.pkl",'rb'))
linreg = pickle.load(open("Models/linreg.pkl",'rb'))

WIN_HEIGHT = 600
WIN_WIDTH = 600
CURRENT_DIR = path.abspath(path.curdir)
GRAPHICS = '/Graphics/'
IMG_SIZE = 50
FILEPATH = os.environ['USERPROFILE'] + '/Desktop/'

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

class PokeApp(tk.Tk):

	def __init__(self,*args,**kwargs):

		tk.Tk.__init__(self, *args, **kwargs)

		self.geometry(f'{WIN_WIDTH}x{WIN_HEIGHT}')
		self.pokedex = pickle.load(open("Models/pokedf.pkl",'rb'))
		self.facelist = [face for face in iter(self.pokedex["face"])]
		self.avatar = Image.open(CURRENT_DIR + GRAPHICS + 'Avatar.png').resize((215,215))



		container = tk.Frame(self)
		container.pack(side="top",fill="both",expand=True)
		container.grid_rowconfigure(0,weight=1)
		container.grid_columnconfigure(0,weight=1)

		self.frames = {}

		for F in (StartPage,PokemonCaught,Pokedex):
			frame = F(container,self)
			self.frames[F] = frame
			frame.grid(row=0,column=0,sticky="nsew")




		self.show_frame(StartPage)

	def show_frame(self,cont):

		frame = self.frames[cont]
		frame.tkraise()



class StartPage(tk.Frame):

	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)

		self.controller = controller		
		canvas = Canvas(self,height=WIN_HEIGHT,width=WIN_WIDTH,bg='black')
		canvas.pack()

		frame_1 = tk.Frame(self,bg='red')
		frame_1.place(relwidth=0.95,relheight=0.495,relx=0.025,rely=0.025)

		frame_2 = tk.Frame(self)
		frame_2.place(relwidth=0.95,relheight=0.425,relx=0.025,rely=0.55)

		frame_3 = tk.Frame(self,bg='black')
		frame_3.place(relwidth=0.2,relheight=0.20,relx=0.4,rely=0.43)

		choose_photo = tk.Button(self,text='Choose Photo',padx=5,command=self.associate)
		choose_photo.configure(height=5,width=10,borderwidth=5, activebackground = "gray", relief = FLAT)
		choose_photo_window = canvas.create_window(0.5*WIN_WIDTH, 0.53*WIN_HEIGHT, anchor=CENTER, window=choose_photo)

		choose_photo = tk.Button(self,text='Pokédex',padx=5,command=self.show_pokedex)
		choose_photo.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		choose_photo_window = canvas.create_window(0.09*WIN_WIDTH, 0.06*WIN_HEIGHT, anchor=CENTER, window=choose_photo)



	def associate(self):

		filename = filedialog.askopenfile(initialdir=FILEPATH,defaultextension=".png")


		if filename==None:
			print('file not chosen')
		else:

			try:

				image = cv2.imread(filename.name)
				image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
				face_encodings = fr.face_encodings(image,num_jitters=1)
				face_locations = fr.face_locations(image)

				self.controller.frames[PokemonCaught].faces = []
				self.controller.frames[PokemonCaught].index_list = []


				if len(face_encodings)==0:
					print('either that was not a face or you are ugly')					
				else:
					for i in range(len(face_encodings)):
						encoding = linreg.predict(face_encodings[i].reshape(1,-1))
						distances, indices = knn.kneighbors(encoding)
						face = image[face_locations[i][0]:face_locations[i][2],face_locations[i][3]:face_locations[i][1]]

						self.controller.frames[PokemonCaught].faces.append(face)
						self.controller.frames[PokemonCaught].index_list.append(indices)


				self.controller.show_frame(PokemonCaught)


				self.controller.frames[PokemonCaught].update_display()

				
			except Exception as e:
				print(e)


	def show_pokedex(self):

		self.controller.show_frame(Pokedex)

		self.controller.frames[Pokedex].update_display()




class PokemonCaught(tk.Frame):
	
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)

		self.controller = controller
		self.index = 0
		self.index_list = []
		self.faces = []
		self.pokename = None
		self.font = tkFont.Font(family="Lucida Grande", size=75)

		self.canvas = Canvas(self,height=WIN_HEIGHT,width=WIN_WIDTH,bg="red",highlightthickness=15,highlightbackground="black")
		self.canvas.pack()

		self.border1 = self.canvas.create_rectangle(40,(WIN_HEIGHT-215)/2-10,60+215,(WIN_HEIGHT+215)/2+10,fill="white")
		self.border2 = self.canvas.create_rectangle(WIN_WIDTH-215-60,(WIN_HEIGHT-215)/2-10,WIN_WIDTH-40,(WIN_HEIGHT+215)/2+10,fill="black")

		self.label = Label(self.canvas, text=self.pokename,font=self.font,background="red")
		self.label.pack()
		self.canvas.create_window(WIN_WIDTH/2,50,anchor=N,window=self.label) 



		self.right = tk.Button(self.canvas,text='Right',padx=5,command=self.right) 
		self.right.configure(height=0,width=10,borderwidth=5, activebackground = "gray", relief = FLAT)
		self.right_window = self.canvas.create_window(WIN_WIDTH-60, 0.9*WIN_HEIGHT, anchor=E, window=self.right)

		self.left = tk.Button(self.canvas,text='Left',padx=5,command=self.left)
		self.left.configure(height=0,width=10,borderwidth=5, activebackground = "gray", relief = FLAT)
		self.left_window = self.canvas.create_window(60, 0.9*WIN_HEIGHT, anchor=W, window=self.left)

		self.add = tk.Button(self.canvas,text='Add',padx=5,command=self.add)
		self.add.configure(height=0,width=10,borderwidth=5,activebackground="gray",relief=FLAT)
		self.add_window = self.canvas.create_window(WIN_WIDTH/2,0.9*WIN_HEIGHT,anchor=CENTER,window=self.add)

		self.back = tk.Button(self,text='Back',padx=5,command=self.back)
		self.back.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		self.back_window = self.canvas.create_window(0.09*WIN_WIDTH, 0.06*WIN_HEIGHT, anchor=CENTER, window=self.back)



	def update_display(self):

		indices = self.index_list[self.index][0]

		self.pokepic = ImageTk.PhotoImage(image=trim(Image.fromarray(self.controller.pokedex["og_image"].iloc[indices[0]])).resize((215,215)))
		self.pokename = self.controller.pokedex["name"].iloc[indices[0]]
		self.personpic = ImageTk.PhotoImage(image=Image.fromarray(self.faces[self.index]).resize((215,215)))

		test1 = self.canvas.create_image(50,WIN_HEIGHT/2,anchor=W,image=self.pokepic)
		test2 = self.canvas.create_image(WIN_WIDTH-50,WIN_HEIGHT/2,anchor=E,image=self.personpic)
		self.label['text'] = self.pokename


	def right(self):

		if self.index<len(self.faces)-1:
			self.index += 1

			self.update_display()


	def left(self):

		if self.index>0:
			self.index -= 1

			self.update_display()


	def add(self):

		indices = self.index_list[self.index][0]


		if type(self.controller.facelist[indices[0]])==np.ndarray:
			
			self.popup_question(indices)

		else:
			
			self.controller.facelist[indices[0]] = self.faces[self.index]
			self.controller.pokedex["face"] = self.controller.facelist
			pickle.dump(self.controller.pokedex, open("Models/pokedf.pkl","wb"))

			self.popup_saved()



	def back(self):

		self.index = 0

		self.controller.show_frame(StartPage)

	def popup_saved(self):

		def leave():
			pop.destroy()

		pop = tk.Toplevel()
		pop.wm_title('!')
		pop.configure(bg='red')



		label = Label(pop,text='Face has been added to the pokedex',foreground='white',background='black')
		label.pack()

		button = tk.Button(pop,text='Ok',padx=5,command=leave)
		button.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		button.pack()

		pop.mainloop()

	def popup_question(self,indices):

		def leave():
			pop.destroy()

		def yes():

			self.controller.facelist[indices[0]] = self.faces[self.index]
			self.controller.pokedex["face"] = self.controller.facelist
			pickle.dump(self.controller.pokedex, open("Models/pokedf.pkl","wb"))
			
			pop.destroy()


		pop = tk.Toplevel()
		pop.wm_title('!')
		pop.configure(bg='red')

		label = Label(pop,text='There is already a face saved to this pokemon, do you want to overwrite it?',foreground='white',background='black')
		label.pack()

		pop.personpic = ImageTk.PhotoImage(image=Image.fromarray(self.controller.facelist[indices[0]]).resize((215,215)))
		picture = tk.Label(pop,image=pop.personpic,borderwidth=0)
		picture.pack()

		yes = tk.Button(pop,text='Yes',command=yes)
		yes.configure(width=7)
		yes.pack()

		no = tk.Button(pop,text='No',command=leave)
		no.configure(width=7)
		no.pack()

		pop.mainloop()


class Pokedex(tk.Frame):
	
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)

		self.controller = controller

		self.tempdex = self.controller.pokedex
		self.tempfacelist = self.controller.facelist

		self.index = 0
		self.personpic = None
		self.pokepic = None
		self.pokename = 'Bulbasaur'
		self.font = tkFont.Font(family="Lucida Grande", size=40)


		self.canvas = Canvas(self,height=WIN_HEIGHT,width=WIN_WIDTH,bg="red",highlightthickness=15,highlightbackground="black")
		self.canvas.pack()

		self.border1 = self.canvas.create_rectangle(40,(WIN_HEIGHT-215)/2-10,60+215,(WIN_HEIGHT+215)/2+10,fill="white")
		self.border2 = self.canvas.create_rectangle(WIN_WIDTH-215-60,(WIN_HEIGHT-215)/2-10,WIN_WIDTH-40,(WIN_HEIGHT+215)/2+10,fill="black")

		self.back = tk.Button(self,text='Back',padx=5,command=self.back)
		self.back.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		self.back_window = self.canvas.create_window(0.09*WIN_WIDTH, 0.06*WIN_HEIGHT, anchor=CENTER, window=self.back)


		self.down = tk.Button(self,text='Down',padx=5,command=self.down)
		self.down.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		self.down_window = self.canvas.create_window(0.5*WIN_WIDTH, 0.9*WIN_HEIGHT, anchor=N, window=self.down)

		self.up = tk.Button(self,text='Up',padx=5,command=self.up)
		self.up.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		self.up_window = self.canvas.create_window(0.5*WIN_WIDTH, 0.85*WIN_HEIGHT, anchor=S, window=self.up)


		self.reset = tk.Button(self,text='Reset Pokedex',padx=5,command=self.popup)
		self.reset.configure(height=0,width=10,activebackground = "gray", relief = FLAT)
		self.reset_window = self.canvas.create_window(0.89*WIN_WIDTH, 0.06*WIN_HEIGHT, anchor=CENTER, window=self.reset)

		self.entry = tk.Entry(self,font=64)
		self.entry.configure()
		self.entry_window = self.canvas.create_window(0.45*WIN_WIDTH, 0.25*WIN_HEIGHT, anchor=CENTER,window=self.entry)


		self.search = tk.Button(self,text='Search',padx=5,command=lambda: self.query(self.entry.get()))
		self.search.configure(height=0,width=7,activebackground = "gray", relief = FLAT)
		self.search_window = self.canvas.create_window(0.65*WIN_WIDTH, 0.25*WIN_HEIGHT, anchor=W, window=self.search)

		self.label = Label(self.canvas, text=f'#{self.index+1} {self.pokename}',font=self.font,background="red")
		self.label.pack()
		self.canvas.create_window(WIN_WIDTH/2,50,anchor=N,window=self.label) 



	def back(self):

		self.index = 0
		self.tempdex = self.controller.pokedex
		self.tempfacelist = self.controller.facelist

		self.controller.show_frame(StartPage)


	def popup(self):

		def leave():
			pop.destroy()

		def reset():

			self.controller.facelist = [np.nan for i in self.controller.facelist]
			self.controller.pokedex["face"] = self.controller.facelist
			pickle.dump(self.controller.pokedex, open("Models/pokedf.pkl","wb"))

			self.update_display()
			
			pop.destroy()


		pop = tk.Toplevel()
		pop.wm_title('!')
		pop.configure(bg='red')

		label = Label(pop,text='This will delete all save photos associated with pokemon.  Are you sure you want to do this?',foreground='white',background='black')
		label.pack()

		yes = tk.Button(pop,text='Yes',command=reset)
		yes.configure(width=7)
		yes.pack()

		no = tk.Button(pop,text='No',command=leave)
		no.configure(width=7)
		no.pack()

		pop.mainloop()



	def query(self,text):

		self.tempdex = self.controller.pokedex
		self.tempfacelist = self.controller.facelist

		if text=='':

			self.index = 0
			self.tempdex = self.controller.pokedex

			self.update_display

		try:
			temp_index = int(text)

			if 1<=temp_index<len(self.controller.facelist)+1:

				self.index = temp_index - 1

				self.update_display()


		except:

			try: 

				self.tempdex = self.tempdex[self.tempdex["name"].str.contains(text,case=False)]
				self.tempfacelist = [face for face in iter(self.tempdex["face"])]
				self.index = 0

				self.update_display()



			except Exception as e:
				print(e)


	def up(self):

		if self.index>0:

			self.index -= 1

		self.update_display()


	def down(self):

		if self.index<len(self.tempfacelist)-1:

			self.index += 1

		self.update_display()


	def update_display(self):

		if type(self.tempfacelist[self.index])==np.ndarray:
			self.personpic = ImageTk.PhotoImage(image=Image.fromarray(self.controller.facelist[self.index]).resize((215,215)))
		
		else:
			self.personpic = ImageTk.PhotoImage(image=self.controller.avatar)

		test2 = self.canvas.create_image(WIN_WIDTH-50,WIN_HEIGHT/2,anchor=E,image=self.personpic)

		self.pokepic = ImageTk.PhotoImage(image=trim(Image.fromarray(self.tempdex["og_image"].iloc[self.index])).resize((215,215)))
		test1 = self.canvas.create_image(50,WIN_HEIGHT/2,anchor=W,image=self.pokepic)

		self.label["text"] = f'#{self.tempdex.index[self.index]} {self.tempdex["name"].iloc[self.index]}'




app = PokeApp()
app.mainloop()
