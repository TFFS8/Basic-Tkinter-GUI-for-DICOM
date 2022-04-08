# Silly Tkinter GUI implementation for reading DICOM data
import numpy as np
import dicom
import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from tkFileDialog import askopenfilename
import os

#GUI style and fonts
LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

#global variables. just for test implementation
global patient
patient = []
global df
df = []
global data_path
data_path='path'
global data_path2
data_path2='path'

# load DICOMs from path
def load_scan(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    return slices

# get pixels from Dicom images
def get_pixels_hu(scans, sim):
    image = np.stack([s.pixel_array for s in scans])
    image = image.astype(np.int16)

    image1 = []
    i = sim
    while i < len(scans):
        image1.append(image[i])
        i = i + 1
    return np.array(image1)

# Search Directories 1, 2 and 3
def askdirectory():
    global data_path
    dirname = askopenfilename()
    if dirname:
        data_path = os.path.split(dirname)[0]
        print data_path

def askdirectory2():
    global data_path2
    dirname = askopenfilename()
    if dirname:
        data_path2 = os.path.split(dirname)[0]
        print data_path2

def askdirectory3():
    dirname = askopenfilename()
    if dirname:
        data_path3 = os.path.split(dirname)[0]
        print data_path3

#Tkinter main function
class T1app(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #setup main frame...name, size,...
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tk.Tk.wm_title(self,"T1 GUI")
        tk.Tk.wm_geometry(self,"1200x900")

        self.frames = {}

        #number of pages
        for F in (StartPage, PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# landing page with button Viewer
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Menu", font=LARGE_FONT, bg='green')
        label.pack(pady=10, padx=10)

        button2 = tk.Button(self, text="Viewer",height=10,width=20,
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()

# page with what matters
class PageTwo(tk.Frame):

    def __init__(self, parent, controller):

        #set titles, buttons...set names, position and link
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="DICOM Viewer!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        rigth1 = tk.Frame(self)
        rigth1.pack(side=tk.RIGHT)

        button1 = tk.Button(self, text="Load DICOM 1",command = askdirectory)
        button1.pack(in_=rigth1,side=tk.TOP )

        button2 = tk.Button(self, text="Load DICOM 2",command= askdirectory2)
        button2.pack(in_=rigth1,side=tk.TOP )

        button3 = tk.Button(self, text="Segmentation",command=askdirectory3)
        button3.pack(in_=rigth1,side=tk.TOP )

        button4 = tk.Button(self, text="Results1",
                             command=lambda: controller.show_frame(StartPage))
        button4.pack(in_=rigth1,side=tk.TOP )

        button5 = tk.Button(self, text="Results2",
                             command=lambda: controller.show_frame(StartPage))
        button5.pack(in_=rigth1,side=tk.BOTTOM )

        # functions for controlling sliding bars
        def callback(d):
            instancenum = int(d)
            print int(bt.get())
            print d

            a.clear()
            a.imshow(df[instancenum], cmap='gray', vmin=0, vmax=2000)
            a.grid(False)
            f.canvas.draw()

        def callback2(d2):
            instancenum = int(d2)
            print int(bt1.get())
            print d2

            a2.clear()
            a2.imshow(df[instancenum], cmap='gray', vmin=0, vmax=2000)
            a2.grid(False)
            f2.canvas.draw()

        # create different frames for position better buttons.. this is complex, check Tkinter tutorials
        top1 = tk.Frame(self)
        bottom1 = tk.Frame(self)
        top1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        bottom1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # figure 1, size and position
        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(in_=top1,side=tk.LEFT,fill=tk.BOTH, expand=True)

        # figure 2, size and position
        f2 = Figure(figsize=(5, 5), dpi=100)
        a2 = f2.add_subplot(111)
        canvas = FigureCanvasTkAgg(f2, self)
        canvas.show()
        canvas.get_tk_widget().pack(in_=top1,side=tk.RIGHT,fill=tk.BOTH, expand=True)

        #enable matplotlib toolbar if required
        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # zip and sort images according to metadata
        global patient
        selectimag = 0
        global data_path
        patient = load_scan(data_path)
        global df
        df = get_pixels_hu(patient, selectimag)
        zipped = zip(patient, df)
        zipped_sorted = sorted(zipped, key=lambda l: l[0][0x0020, 0x0013].value)
        patient, df = map(list, zip(*zipped_sorted))

        # clear old image and show new
        a.clear()
        a.imshow(df[0], cmap='gray', vmin=0, vmax=2500)
        a.grid(False)

        a2.clear()
        a2.imshow(df[0], cmap='gray', vmin=0, vmax=2500)
        a2.grid(False)

        #sliding bars customization
        bt = tk.Scale(self, from_=0, to=len(patient)-1, orient=tk.HORIZONTAL,bd=4, length=500,command=callback)
        bt.pack(in_=bottom1,side=tk.LEFT,fill=tk.BOTH, expand=True)
        print (int(bt.get()))

        bt1 = tk.Scale(self, from_=0, to=len(patient) - 1, orient=tk.HORIZONTAL, bd=4, length=500, command=callback2)
        bt1.pack(in_=bottom1,side=tk.RIGHT,fill=tk.BOTH, expand=True)
        print (int(bt1.get()))

# end Tkinter main
app = T1app()
app.mainloop()
