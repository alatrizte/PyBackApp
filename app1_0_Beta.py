#################################################################
#                                                               #
#        Py_BackUP - Programa para BackUps automáticos          #
#                   Creado por ISAAC RUPPEN                     #
#                           29/7/2021                           #
#                                                               #
#                      Versión 1.0 - Beta                       #
#                       LICENCIA GPLv3                          #
#                                                               #
#################################################################


from genericpath import isdir, isfile
import os
import shutil
#from pydoc import text
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import NO
#from typing import Text

from ttkwidgets import CheckboxTreeview

from datetime import datetime

select_path = []
seleccionados =[]
backupOnInit = ""

root=tk.Tk()
root.geometry('900x550')
root.title("Py_BackUp - 1.0 Beta")
ckeck = tk.BooleanVar()

def readConfig():
    global backupOnInit
    if os.path.exists('config.txt'):
        ConfigFile = open('config.txt','r')

        backupOnInit = ConfigFile.readline()[:-1]
        entry_directory["state"]='normal'
        entry_directory.insert(tk.END, ConfigFile.readline()[:-1])
        entry_directory["state"]='disabled'
        entry_directory_BU["state"]='normal'
        entry_directory_BU.insert(tk.END, ConfigFile.readline())
        entry_directory_BU["state"]='disabled'
        
        ckeck.set(backupOnInit)

        ConfigFile.close()
    else:
        ConfigFile = open('config.txt','w')
        ConfigFile.write(entry_directory.get() + '\n')
        ConfigFile.write(entry_directory_BU.get())
        ConfigFile.close()
    
    print("Read Config: OK")

def openConfig():
    def saveConfig():
        if ckeck.get() == True:
            el_check = "True"
        else:
            el_check = "False"

        ConfigFile = open('config.txt','w')
        ConfigFile.write(el_check + "\n")
        ConfigFile.write(entry_directory.get() + '\n')
        ConfigFile.write(entry_directory_BU.get())
        ConfigFile.close()
        configWindow.destroy()

    def cancelConfig():
        configWindow.withdraw()
        mensa = messagebox.askokcancel("Exit Configuration", "Do you want exit without saving changes?")
        if mensa == True:
            configWindow.destroy()
        else:
            configWindow.deiconify()
            return

    configWindow = tk.Toplevel(root, padx=50, pady=30)
    configWindow.title("Configuration")
    configWindow.geometry("600x230+500+200")
    
    lb_ORIGEN = tk.Label(configWindow, text="ORIGEN: ")
    entryOrigen = tk.Entry(configWindow, textvariable=directory, state='disabled', width=60)
    btnPathOrigen = tk.Button(configWindow, text="Browse...", command=add_origen_folder)
    lb_ORIGEN.grid(row=0, column=0, padx=5, pady=10)
    entryOrigen.grid(row=0, column=1, padx=5)
    btnPathOrigen.grid(row=0, column=2, padx=5)
    
    lb_DESTINO = tk.Label(configWindow, text="DESTINO: ")
    entryDestino = tk.Entry(configWindow, textvariable=directory_BU, state='disabled', width=60)
    btnPathDestino = tk.Button(configWindow, text="Browse...", command=add_destino_folder)
    lb_DESTINO.grid(row=1, column=0)
    entryDestino.grid(row=1, column=1)
    btnPathDestino.grid(row=1, column=2)

    lb_init = tk.Label(configWindow, text="Back Up al INICIO WINDOWS")
    
    check_init = tk.Checkbutton(configWindow, variable=ckeck)
    lb_init.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=20)
    check_init.grid(row=2, column=2, sticky=tk.W)

    btnSave = tk.Button(configWindow, text="Save", command=saveConfig)
    btnCancel = tk.Button(configWindow, text="Cancel", command=cancelConfig)
    btnSave.grid(row=3, column=1, sticky=tk.E, ipadx=12)
    btnCancel.grid(row=3, column=2, ipadx=5)

    
    configWindow.grab_set()
    
def update_BU_list(event):
    """Check or uncheck box when clicked."""
    x, y, widget = event.x, event.y, event.widget
    elem = widget.identify("element", x, y)
    id_elem = widget.identify('item', x, y)
    if "image" in elem:       
        writeOutputFile()

def get_checked():
    """Return the list of checked items that do not have any child."""
    checked = []
    def get_checked_children(item):
        if not tree.tag_has("unchecked", item):
            ch = tree.get_children(item)
            if tree.tag_has("checked", item):
                checked.append(item)
                for c in ch:
                    get_checked_children(c)  
            else:
                for c in ch:
                    get_checked_children(c)

    ch = tree.get_children("")
    for c in ch:
        get_checked_children(c)
    return checked

def readOutputFile():
    '''
    Lee el archivo OUTPUT.TXT donde se almacenan los paths 
    de los archivos para copiar en el BACK_UPS
    '''
    select_path.clear()
    my_file = open('output.txt')
    lineText = my_file.readlines()
    for line in lineText:
        select_path.append(line[:-1])
    my_file.close()
    label_var.set("Numero de archivos: " + str(len(select_path))) 

    print("Read Output File: OK")        

def addToOutput(paths):
    MyFile = open('output.txt','w')
    for element in paths:
        MyFile.write(element)
        MyFile.write('\n')
    MyFile.close()
    readOutputFile()

def writeOutputFile():
    '''
    Genera un archivo .TXT con las direcciones de los archivos
    o carpetas seleccionados en el arbol.
    '''
    seleccion = get_checked()
    select_path.clear()
    for archivo in seleccion:
        if tree.item(archivo)["values"][1] == tree.item(archivo)["text"]:
            fileToCopy = tree.item(archivo)["values"][1]
        else:
            fileToCopy = tree.item(archivo)["values"][1] + "\\" + tree.item(archivo)["text"]
        select_path.append(fileToCopy)
    MyFile = open('output.txt','w')
    for element in select_path:
        MyFile.write(element)
        MyFile.write('\n')
    MyFile.close()
    readOutputFile()
    BU_tree.delete(*BU_tree.get_children())

    BU_tree_init() #hace una llamada para actualizar el arbol de BACK UP
    print("Write Output File: OK")

def reReadTreeSelect():
    '''
    Repasa los items seleccionados en el TREE
    '''
    seleccion = get_checked()

def copyFiles():
    '''
    Al presionar el botón PROCEED.
    Copia los archivos en la carpeta de BACK_UPS
    '''
    l = len(select_path)
    loadbar(0, l, prefix='Progress:', suffix='Complete', length=50)
    i = 0

    path_BU = os.path.abspath(entry_directory_BU.get())
    for source in select_path:
        loadbar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
        fecha_original = datetime.fromtimestamp(os.path.getmtime(source))
        destination = path_BU + source[2:]
        if os.path.exists(destination):
            fecha_copia = datetime.fromtimestamp(os.path.getmtime(destination)) 
            if fecha_original != fecha_copia and isfile(destination):
                print("copia el archivo "+ os.path.basename(destination))
                shutil.copy2(source, destination)
        else:
            if isfile(source):
                if os.path.exists(os.path.dirname(destination)) == False:
                    print("Crea el directorio " + os.path.dirname(destination))
                    os.makedirs(os.path.dirname(destination))
                    print("copia el archivo "+ os.path.basename(destination))
                    shutil.copy2(source, destination)
                else:
                    print("copia el archivo "+ os.path.basename(destination))
                    shutil.copy2(source, destination)
            else:
                print("Crea el directorio " + destination)
                os.makedirs(destination)
        i += 1
          
    writeOutputFile()
    create_reg_file()
    dataBU.set(datetime.fromtimestamp(os.path.getmtime("register.txt")))
    
def _change_state_ancestor(item):
    """
    Cambia el estado de los archivos copiados.
    Si existe la copia: TRUE 
    Si NO existe copia: FALSE
    """
    parent = BU_tree.parent(item)
    if parent:
        children = BU_tree.get_children(parent)
        b = ["True" in BU_tree.item(c)["values"][1] for c in children]
        if False in b:
            BU_tree.set(parent, column='estado', value="Semi")
            BU_tree.item(parent, image=get_icon(""))
            _change_state_ancestor(parent)   

def update_check():
    '''
    Comprueba que los hijos y los padres del SELECCIONADO
    tengan un checked o un tristate.
    '''
    print("Start Update_check")
    
    l = len(seleccionados)
    if l>0:
        loadbar(0, l, prefix='Progress:', suffix='Complete', length=50)
        i = 0
        for sel in seleccionados:
            loadbar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
            tree.change_state(sel, "checked")
            tree._check_ancestor(sel)
            tree._check_descendant(sel)
            i += 1

    print("Update Checks in ORIGEN Tree: OK")

def update():
    '''
    Actualiza los arboles de la aplicación al pulsar el botón UPDATE
    '''
    path = os.path.abspath(entry_directory.get())
    readOutputFile()
    seleccionados.clear()
    tree.delete(*tree.get_children())
    BU_tree.delete(*BU_tree.get_children())
    node = tree.insert('', 'end', text=path, values=(fecham, path), open=True)
    tree_init(node, path)
    BU_tree_init()
    update_check()
    writeOutputFile()
        
def get_icon(estado):
    if estado == True:
        return IM_DONE
    elif estado == False:
        return IM_UNDONE
    else:
        return IM_SEMIDONE

def tree_init(parent, path):
    for d in os.listdir(path):
        full_path = os.path.join(path, d)
        full_fecham = datetime.fromtimestamp(os.path.getmtime(full_path))
        isdir = os.path.isdir(full_path)
        id = tree.insert(parent, 'end', text=d, values=(full_fecham, path), open=False)
        if isdir:
            tree_init(id, full_path)
        for selec in select_path:
            if full_path == selec:
                seleccionados.append(id)

def BU_tree_init():
    print("Start BU_Tree Init")

    '''
    Lee la lista de los archivos para BackUp y crea un arbol.
    Si el archivo tiene la copia actualizada ESTADO: TRUE
    en caso negativo ESTADO: FALSE
    '''
    path_BU = os.path.abspath(entry_directory_BU.get())
    dicc_folders={} # Diccionario para direcciones [direccion: id]
    iid = 0 # id para el treeview 
    node_BU = BU_tree.insert('', 'end', id=str(iid), text=path_BU, values=(fecham, path_BU), open=True)

    # Primera entrada del diccionario que es la carpeta del BACKUP
    dicc_folders = { BU_tree.item(str(iid))["text"]: str(iid)} 

    l = len(select_path)
    if l > 0:
        loadbar(0, l, prefix='Progress:', suffix='Complete', length=50)
        i = 0

        # Se crea un arbol de los archivos a copiar      
        for archivo in select_path:
            loadbar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
            archivo_en_BU = path_BU + archivo[2:]
            estado = os.path.exists(archivo_en_BU)

            #Si el archivo ya existe en BACKUP compara fechas modificación.
            #Si las fechas no coinciden, el estado cambia a FALSE.
            if estado == True and isfile(archivo):  
                full_fecham = datetime.fromtimestamp(os.path.getmtime(archivo_en_BU))
                full_fecham_original = datetime.fromtimestamp(os.path.getmtime(archivo))
                if full_fecham_original != full_fecham:
                    estado = False

            directorios = archivo.split("\\")
            parent = node_BU
            #nombre="BACK_UPS"
            nombre = path_BU
            for n in directorios:
                # Damos un paso para que no cree en el arbol un nivel con el nombre de la unidad
                if n == "F:": # En este caso la unidad "F:"
                    continue
                nombre = nombre + n
                if nombre in dicc_folders.keys():  # Si el nombre del path existe en el diccionario
                    parent =  int(dicc_folders[nombre])
                else:
                    iid += 1
                    id = BU_tree.insert(parent, 'end', id=str(iid), image=get_icon(estado), text=n, values=(nombre, estado), open=False)
                    if estado == False:
                        _change_state_ancestor(iid)
                    parent = id
                    dicc_folders [BU_tree.item(str(iid))["values"][0]] = str(iid)    
            i += 1

def add_origen_folder():
    filename = tk.filedialog.askdirectory()
    entry_directory["state"]='normal'
    entry_directory.delete(0, tk.END)
    entry_directory.insert(tk.END,filename)
    entry_directory["state"]='disabled'
    update()

def add_destino_folder():
    filename = tk.filedialog.askdirectory()
    entry_directory_BU["state"]='normal'
    entry_directory_BU.delete(0, tk.END)
    entry_directory_BU.insert(tk.END,filename)
    entry_directory_BU["state"]='disabled'
    update()

def create_reg_file():
    RegFile = open('register.txt','w')
    RegFile.close()

def loadbar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='>'):
	percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration/float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
	if iteration == total:
		print()

def expand_BUTree():
    def openTree(id):
        BU_tree.item(id, open=True)
        if BU_tree.get_children(id):
            for nextLevel in BU_tree.get_children(id):
                openTree(nextLevel)

    for each in BU_tree.get_children():
        openTree(each)
                

frame = tk.Frame(root, pady=20)
lb_lastBU = tk.Label(frame, text="Last BackUp: ")
dataBU = tk.StringVar()
dataBU.set(datetime.fromtimestamp(os.path.getmtime("register.txt")))
Data_lastBU = tk.Label(frame, textvariable=dataBU)
b_update = tk.Button(frame, text="Update", command=update)

directory = tk.StringVar(frame, value='')
labelOrigen = tk.Label(frame, text='Path ORIGEN:')

entry_directory = tk.Entry(frame, textvariable=directory, state='disabled', width=80)
frame_trees = tk.Frame(frame, width=100, height=200, pady=20)
tree = CheckboxTreeview(frame_trees)
BU_tree = ttk.Treeview(frame_trees, show='tree headings', columns=('path', 'estado', 'fecha'))
BU_tree["displaycolumns"] = ()
ybar = tk.Scrollbar(frame_trees, orient=tk.VERTICAL, command=tree.yview)
ybar2 = tk.Scrollbar(frame_trees, orient=tk.VERTICAL, command=BU_tree.yview)

directory_BU = tk.StringVar(frame, value='')
labelDestino = tk.Label(frame, text='Path DESTINO:')
entry_directory_BU = tk.Entry(frame, textvariable=directory_BU, state='disabled', width=80) 

b_expand = tk.Button(frame_trees, text='Expand', command=expand_BUTree)
b_proceed = tk.Button(frame, text="PROCEED", command=copyFiles)
btn_config = tk.Button(frame, text="Config.", command=openConfig)

label_var = tk.StringVar()
label = tk.Label(frame, textvariable=label_var)

IM_DONE = tk.PhotoImage(file=r"icons/done.png")
IM_UNDONE = tk.PhotoImage(file=r"icons/undone.png")
IM_SEMIDONE = tk.PhotoImage(file=r"icons/semidone.png")

readConfig()

readOutputFile() 

tree.configure(yscroll=ybar.set)
BU_tree.configure(yscroll=ybar2.set)

tree.heading('#0', text='ORIGEN', anchor='w')
tree.column('#0', width=275)

#tree.heading('date', text='Fecha Modificacion', anchor='w')
BU_tree.heading('#0', text='DESTINO', anchor='w')
BU_tree.column('#0', width=375)
#BU_tree.heading('estado', text='Estado', anchor='w')
#tree.heading('time', text='Hora Modificacion', anchor='w')
path = os.path.abspath(entry_directory.get())
path_BU = os.path.abspath(entry_directory_BU.get())
fecham = datetime.fromtimestamp(os.path.getmtime(entry_directory.get()))
node = tree.insert('', 'end', text=path, values=(fecham, path), open=True)
            
tree_init(node, path)

tree.bind("<ButtonRelease-1>", update_BU_list) 

frame.pack()

lb_lastBU.grid(row=0, column=0, sticky=tk.E)
Data_lastBU.grid(row=0, column=1, sticky=tk.W)
b_update.grid(row=0, column=1, pady=20, sticky=tk.E, ipadx=5)
labelOrigen.grid(row=1, column=0, sticky=tk.E)
entry_directory.grid(row=1, column=1)

frame_trees.grid(row=2, column=0, columnspan=3)
ybar.pack(side=tk.LEFT, fill=tk.Y)
tree.pack(side=tk.LEFT, fill=tk.Y )
BU_tree.pack(side=tk.LEFT, fill=tk.Y)
ybar2.pack(side=tk.LEFT, fill=tk.Y)
b_expand.pack(side=tk.BOTTOM)

labelDestino.grid(row=3, column=0, sticky=tk.E)
entry_directory_BU.grid(row=3, column=1)

btn_config.grid(row=4, column=0, sticky=tk.W, ipadx=10)
b_proceed.grid(row=4, column=1, pady=20, sticky=tk.E, ipadx=5)

label.grid(row=5, column=0, columnspan=2)

update_check()

writeOutputFile()
'''
if backupOnInit == "True":
    copyFiles()
'''
root.mainloop()
