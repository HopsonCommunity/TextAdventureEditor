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
root.tk_setPalette('#000000')#Set window background colour
canvas = tkinter.Canvas(root,width=640,height=600,bg='#778888')#Create 640x600 canvas with background colour
canvas.grid(row=0,column=0)
helpInfo = tkinter.Label(root,fg='#cccccc',font=('fixedsys',14),text=HELPTEXT,justify=tkinter.LEFT)#Create label next to it
helpInfo.grid(row=0,column=1,sticky=tkinter.NW)

class Colour():#Simple class for colours str(Colour(r,g,b)) will return a string in the format tkinter uses
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

def strFormat(json):#For displaying "key":"value" pairs cleanly in string form
    out = ''
    jsonkeys = list(json.keys())
    jsonkeys.sort()
    for key in jsonkeys:
        out += str(key)+' : '+str(json[key])+'\n'
    return out

class GRoom():# A room, represented graphically
    RID = 0
    def __init__(self,x,y):
        self.size = ROOMSIZE# Refers to visual size in editor
        self.data = {'room_id':GRoom.RID}# Associated json data
        self.room_id = GRoom.RID# Room ID
        self.state = 'min'# state: 'min' or 'max', if max(imised): json info is displayed too
        GRoom.RID += 1# So each room has a unique ID
        self.cids = []# IDs of canvas objects it uses will be stored in this list
        self.x,self.y = x,y# X and Y in editor, editing these values will move the object
        self.selected = False# If selected is True, it will draw with slightly different colour scheme
    def draw(self):# Draw method, called every loop
        for i in range(len(self.cids)):# Delete old items by canvas id
            canvas.delete(self.cids[0])
            del self.cids[0]
        col = Colour(20,20,30)
        if self.selected:# If selected, outline colour will be set to orange
            col = Colour(255,100,0)
        # Create canvas ids and store in canvas id list
        self.cids.append(canvas.create_rectangle(self.x,self.y,self.x+self.size,self.y+self.size,fill='#ddeeff',outline=str(col),width=3))
        self.cids.append(canvas.create_text(self.x+self.size//2,self.y+self.size//2,text=str(self.room_id),fill=str(col),font=('fixedsys',20)))
        if self.state == 'max':# If maximised, draw json data to canvas in a box
            out = strFormat(self.data)
            self.cids.append(canvas.create_rectangle(320,320,600,600,fill='#ddeeff',outline='#222233',width=3,tags='overlay'))
            self.cids.append(canvas.create_text(330,330,text=out,anchor=tkinter.NW,fill='#333344',font=('fixedsys',16),tags='overlay'))
    def clean(self):# This will generate X and Y values and snap everything to a grid
        self.x = (self.room_id%10)*(ROOMSIZE+GAPSIZE) + GAPSIZE
        self.y = (self.room_id//10)*(ROOMSIZE+GAPSIZE) + GAPSIZE
    def minimise(self):# Set state to minimised
        self.state = 'min'
    def maximise(self):# Minimise other rooms, maximise this one
        minimise_all_rooms()
        self.state = 'max'




def loop():# Main loop
    global selcid
    move()# Moves selected rooms according to given keypresses
    for room in rooms:# Draw rooms
        room.draw()
    if selcid != -1:# Canvas ID of the selection box
        canvas.delete(selcid)# Delete old selection box (but only if present)
    selcid = canvas.create_rectangle(selx,sely,selx2,sely2,fill='#ffff00',outline='#ffff00',width=2,stipple='gray50')# Redraw (Stipple argument gives a dithered fill)
    canvas.lift('overlay')# Anything with the tag 'overlay' will be brought to the front
    root.after(10,loop)# Delay until next loop (1000 = 1 second)

def addRoom(event):# Add room
    rooms.append(GRoom(event.x,event.y))# Create new room at mouse-location
    rooms[-1].draw()

def minimise_all_rooms(event=''):# Making event an optional argument allows this to be called by keypress or from within the program
    for room in rooms:
        room.minimise()

def clean(event):# Arrange rooms in an invisible grid
    for room in selected:
        room.clean()

selx,sely,selx2,sely2 = -1,-1,-1,-1# Coordinates of the selection box, (moving these changes where the box is drawn)
selcid = -1# Canvas ID of selection box
selecting = False# True if currently making a selection ( to avoid unexpected behaviour with selectAll() )
def begin_select(event):# Initial click, begin drawing selection box
    global selx,sely,selx2,sely2
    global selected
    global selecting
    selecting = True# Set flag
    for room in selected:# First of all, deselect existing selection
        room.selected = False
    selected = []
    selx,sely,selx2,sely2 = event.x,event.y,event.x,event.y

def cont_select(event):# While mouse is being dragged around, change the coordinates of the other corner of the selection box
    global selx,sely,selx2,sely2
    selx2,sely2 = event.x,event.y

def finish_select(event):# When mouse is released, add rooms within box to selected[]
    global selx,sely,selx2,sely2
    cids = canvas.find_overlapping(selx,sely,selx2,sely2)# Finds canvas IDs of objects overlapping with coordinates of our selection box
    for room in rooms:# For every room
        for cid in cids:# For every detected canvas id
            if cid in room.cids and room not in selected:# If the canvas ID belongs to a room, and the room is not already selected
                room.selected = True# Select room
                selected.append(room)
    selx,sely,selx2,sely2 = -1,-1,-1,-1# Hide selection box again
    selecting = False# Set flag

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
def pressButton(event):# If a button of WASD is pressed, it is added to the list: buttons
    global buttons
    if event.keysym not in buttons:
        buttons.append(event.keysym)

def releaseButton(event):# If a button is released, it is removed from the list: buttons
    global buttons
    if event.keysym in buttons:
        buttons.remove(event.keysym)

def move():# Move selection according to keys currently pressed
    if 'w' in buttons:# If 'w' pressed ( case-sensitive )
        for room in selected:# Move selected rooms
            room.y -= 1# This is important: positive Y is down, negative Y is up
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


# Key bindings, when any of these keys are pressed, the corresponding functions
# are called with a single parameter: an event object
# Useful attributes:
# event.x, event.y = Coordinates of mouse cursor when key pressed
# event.keysym = Symbol of key that was pressed
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
