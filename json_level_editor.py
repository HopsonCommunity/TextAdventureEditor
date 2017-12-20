ROOMSIZE = 30
GAPSIZE = 30

rooms = []
selected = []

HELPTEXT = """
Help
----
Click + Drag : Select
X : Deselect
R : Add room
I : Show room info
M : Minimise room info
C : Clean workspace
O : Select all
WASD : Move selected tiles

"""

import tkinter# GUI Stuff
root = tkinter.Tk()
root.title("Story Editor")
root.tk_setPalette('#000000')
canvas = tkinter.Canvas(root,width=640,height=600,bg='#778888')
canvas.grid(row=0,column=0)
helpInfo = tkinter.Label(root,fg='#cccccc',font=('fixedsys',14),text=HELPTEXT,justify=tkinter.LEFT)
helpInfo.grid(row=0,column=1,sticky=tkinter.NW)

class Colour():
    def __init__(self,r,g,b):
        self.c=[r,g,b]
    def __str__(self):
        out='#'
        for c in self.c:
            if c < 0:
                c = 0
            if c > 255:
                c = 255
            out += ('0'+(hex(int(c))[2:]))[-2:]
        return out

def strFormat(json):
    out = ''
    jsonkeys = list(json.keys())
    jsonkeys.sort()
    for key in jsonkeys:
        out += str(key)+' : '+str(json[key])+'\n'
    return out

class GRoom():
    RID = 0
    def __init__(self,x,y):
        self.size = ROOMSIZE
        self.data = {'room_id':GRoom.RID}
        self.room_id = GRoom.RID
        self.state = 'min'
        GRoom.RID += 1
        self.cids = []
        self.x,self.y = x,y
        self.selected = False
    def draw(self):
        for i in range(len(self.cids)):
            canvas.delete(self.cids[0])
            del self.cids[0]
        col = Colour(20,20,30)
        if self.selected:
            col = Colour(255,100,0)
        self.cids.append(canvas.create_rectangle(self.x,self.y,self.x+self.size,self.y+self.size,fill='#ddeeff',outline=str(col),width=3))
        self.cids.append(canvas.create_text(self.x+self.size//2,self.y+self.size//2,text=str(self.room_id),fill=str(col),font=('fixedsys',20)))
        if self.state == 'max':
            out = strFormat(self.data)
            self.cids.append(canvas.create_rectangle(320,320,600,600,fill='#ddeeff',outline='#222233',width=3,tags='overlay'))
            self.cids.append(canvas.create_text(330,330,text=out,anchor=tkinter.NW,fill='#333344',font=('fixedsys',16),tags='overlay'))
    def clean(self):
        self.x = (self.room_id%10)*(ROOMSIZE+GAPSIZE) + GAPSIZE
        self.y = (self.room_id//10)*(ROOMSIZE+GAPSIZE) + GAPSIZE
    def minimise(self):
        self.state = 'min'
    def maximise(self):
        minimise_all_rooms()
        self.state = 'max'




def loop():
    global selcid
    move()
    if clean == True:
        for room in rooms:
            room.clean()
    for room in rooms:
        room.draw()
    if selcid != -1:
        canvas.delete(selcid)
    selcid = canvas.create_rectangle(selx,sely,selx2,sely2,fill='#ffff00',outline='#ffff00',width=2,stipple='gray50')
    canvas.lift('overlay')
    root.after(10,loop)

def addRoom(event):
    rooms.append(GRoom(event.x,event.y))
    rooms[-1].draw()

def minimise_all_rooms(event=''):
    for room in rooms:
        room.minimise()

def clean(event):
    for room in selected:
        room.clean()

selx,sely,selx2,sely2 = -1,-1,-1,-1
selcid = -1
selecting = False
def begin_select(event):
    global selx,sely,selx2,sely2
    global selected
    global selecting
    selecting = True
    for room in selected:
        room.selected = False
    selected = []
    selx,sely,selx2,sely2 = event.x,event.y,event.x,event.y

def cont_select(event):
    global selx,sely,selx2,sely2
    selx2,sely2 = event.x,event.y

def finish_select(event):
    global selx,sely,selx2,sely2
    cids = canvas.find_overlapping(selx,sely,selx2,sely2)
    for room in rooms:
        for cid in cids:
            if cid in room.cids and room not in selected:
                room.selected = True
                selected.append(room)
    selx,sely,selx2,sely2 = -1,-1,-1,-1
    selecting = False

def info(event):
    minimise_all_rooms()
    for room in selected:
        room.maximise()

def deselect_all(event=''):
    global selected
    for room in selected:
        room.selected = False
    selected = []

buttons = []
def pressButton(event):
    global buttons
    if event.keysym not in buttons:
        buttons.append(event.keysym)

def releaseButton(event):
    global buttons
    if event.keysym in buttons:
        buttons.remove(event.keysym)

def move():
    if 'w' in buttons:
        for room in selected:
            room.y -= 1
    if 's' in buttons:
        for room in selected:
            room.y += 1
    if 'a' in buttons:
        for room in selected:
            room.x -= 1
    if 'd' in buttons:
        for room in selected:
            room.x += 1

def selectAll(event):
    global selecting
    deselect_all()
    for room in rooms:
        room.selected = True
        selected.append(room)


root.bind('<Button-1>',begin_select)
root.bind('<B1-Motion>',cont_select)
root.bind('<ButtonRelease-1>',finish_select)
root.bind('m',minimise_all_rooms)
root.bind('x',deselect_all)
root.bind('r',addRoom)
root.bind('c',clean)
root.bind('i',info)
root.bind('o',selectAll)
root.bind('w',pressButton)
root.bind('a',pressButton)
root.bind('s',pressButton)
root.bind('d',pressButton)
root.bind('<KeyRelease-w>',releaseButton)
root.bind('<KeyRelease-a>',releaseButton)
root.bind('<KeyRelease-s>',releaseButton)
root.bind('<KeyRelease-d>',releaseButton)
root.after(1,loop)
root.mainloop()
