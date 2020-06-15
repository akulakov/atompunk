#!/usr/bin/env python
from bearlibterminal import terminal as blt
import os
import sys
import math
from random import choice, randrange, random
from collections import defaultdict
from textwrap import wrap
from time import sleep
import string
import shelve
from copy import copy  #, deepcopy
from enum import Enum, auto

"""
HoS
"""

HEIGHT = 16
WIDTH = 38
AUTO_BATTLE = 11
END_MOVE=900
SIZE = 24

SLP = 0.01
SEQ_TYPES = (list, tuple)
debug_log = open('debug', 'w')
board_grid = []

keymap = dict(
    [
    [ blt.TK_ESCAPE, 'ESCAPE' ],
    [ blt.TK_RETURN, 'ENTER' ],
    [ blt.TK_PERIOD, "." ],
    [ blt.TK_SHIFT, 'SHIFT' ],
    [ blt.TK_UP, "UP" ],
    [ blt.TK_DOWN, "DOWN" ],
    [ blt.TK_RIGHT, "RIGHT" ],
    [ blt.TK_LEFT, "LEFT" ],

    [ blt.TK_MOUSE_LEFT, "CLICK" ],

    [ blt.TK_Q, 'q' ],
    [ blt.TK_W, 'w' ],
    [ blt.TK_E, 'e' ],
    [ blt.TK_R, 'r' ],
    [ blt.TK_T, 't' ],
    [ blt.TK_Y, 'y' ],
    [ blt.TK_U, 'u' ],
    [ blt.TK_I, 'i' ],
    [ blt.TK_O, 'o' ],
    [ blt.TK_P, 'p' ],
    [ blt.TK_A, 'a' ],
    [ blt.TK_S, 's' ],
    [ blt.TK_D, 'd' ],
    [ blt.TK_F, 'f' ],
    [ blt.TK_G, 'g' ],
    [ blt.TK_H, 'h' ],
    [ blt.TK_J, 'j' ],
    [ blt.TK_K, 'k' ],
    [ blt.TK_L, 'l' ],
    [ blt.TK_Z, 'z' ],
    [ blt.TK_X, 'x' ],
    [ blt.TK_C, 'c' ],
    [ blt.TK_V, 'v' ],
    [ blt.TK_B, 'b' ],
    [ blt.TK_N, 'n' ],
    [ blt.TK_M, 'm' ],

    [ blt.TK_1, '1' ],
    [ blt.TK_2, '2' ],
    [ blt.TK_3, '3' ],
    [ blt.TK_4, '4' ],
    [ blt.TK_5, '5' ],
    [ blt.TK_6, '6' ],
    [ blt.TK_7, '7' ],
    [ blt.TK_8, '8' ],
    [ blt.TK_9, '9' ],
    [ blt.TK_0, '0' ],

    [ blt.TK_COMMA, ',' ],
    [ blt.TK_SPACE, ' ' ],
    [ blt.TK_MINUS, '-' ],
    [ blt.TK_EQUALS, '=' ],
    [ blt.TK_SLASH, '/' ],
    ]
    )

class ObjectsClass:
    def __init__(self):
        self.objects = {}

    def __setitem__(self, k, v):
        self.objects[k] = v

    def __getitem__(self, k):
        return self.objects.get(k)

    def __getattr__(self, k):
        return self.objects[getattr(ID, k)]

    def get(self, k, default=None):
        return self.objects.get(k, default)

Objects = ObjectsClass()

class ID(Enum):
    player = auto()
    elder = auto()


class Type(Enum):
    door1 = auto()
    container = auto()
    blocking = auto()
    player = auto()
    knife = auto()
    vault13_flask = auto()
    pistol = auto()
    cap = auto()

conv_str = {
    ID.elder:
    {
    1: "Congratulations on your victory in the Temple of Trials! Please take some caps and a flask for Vault 13, that should help you in your journey.",
    2: "There's more I would like to know.",
    3: "Tell me more about the GECK.",
    4: "It's a Garden creation kit, it will make our land more fruitful, just as it was before the Cataclysm",
    5: "Where is Klamath?",
    6: "It should be marked on your map",
    7: "Where is Vault 13?",
    8: "Somewhere in the Wastes.. beyond that, none of the tribesmen know.",
    }
}

conversations = {
    ID.elder:
        [
            1, 2,
            [
                [3,4],
                [5,6],
                [7,8],
            ],
        ],
    }

class Talk:
    def __init__(self, B, being, id=None):
        self.B = B
        id = id or being.id
        self.conv_str, self.conversations = conv_str[id], conversations[id]
        self.loc = being.loc
        self.ind = 0
        self.current = self.conversations
        self.choice_stack = []

    def choose(self, txt):
        multichoice = len(txt)
        lst = []
        for n, t in enumerate(txt):
            lst.append(f'{n+1}) {self.conv_str[t[0]]}')
        txt = '\n'.join(lst)
        self.display(txt, False)
        for _ in range(3):
            k = get_and_parse_key()
            try:
                k=int(k)
            except ValueError:
                k = 0
            if k in range(1, multichoice+1):
                return k-1

    def talk(self):
        try: conv = self.current[self.ind]
        except Exception as e:
            print("talk(), e", e)
            return None
        if isinstance(conv, SEQ_TYPES):
            self.choice_stack.append(conv)
            i = self.choose(conv)
            if i:
                self.current = conv[i]
            self.ind = 1
        else:
            rv = self.display(self.conv_str[conv])
            if not rv: return None
            self.ind += 1
        rv = self.talk()
        if not rv: return None

    def display(self, txt, wait=True):
        print ("in def display()", txt)
        self.B.draw()
        x = min(self.loc.x, 60)

        lst = []
        x = min(40, x)
        w = 78 - x
        lines = (len(txt) // w) + 4
        txt_lines = wrap(txt, w)
        txt = '\n'.join(txt_lines)
        offset_y = lines if self.loc.y<8 else -lines

        y = max(0, self.loc.y+offset_y)
        W = max(len(l) for l in txt_lines)
        blt.clear_area(x+1, y+1, W, len(txt_lines))
        puts(x+1,y+1, txt)
        refresh()
        k = None
        while wait and k not in (' ', 'LEFT', 'ESCAPE'):
            k = get_and_parse_key()
        if k=='ESCAPE':
            return
        if k=='LEFT':
            self.ind = -1
            self.current = [self.choice_stack.pop()]
        if wait:
            self.B.draw()
        return True


class Blocks:
    """All game tiles."""
    blank = '.'
    rock3 = '░'
    large_circle = '\u20dd'
    bricks = '\u2687'
    rock = '\u2588'
    door = '\u26bd'
    water = '\u224b'
    tree1 = '\u2689'
    tree2 = '\u268a'
    rock2 = '\u2337'
    player_f = '\u26d5'
    player_l = '\u26d6'
    player_r = '\u26d7'
    player_b = '\u26d8'
    rubbish = '\u26c1'
    circle3 = '\u25cc'  # dotted
    woman = '\u2700'
    knife = '\u26e0'
    cupboard = '\u269a'
    house_c1 = '\u250c'
    house_c2 = '\u2518'
    hex = '\u26e2'
    roof = hex
    door = '+'


BLOCKING = [Blocks.rock, Type.door1, Type.blocking]

class Misc:
    status = []
    current_unit = None
    player = None

def mkcell():
    return [Blocks.blank]

def mkrow():
    return [mkcell() for _ in range(WIDTH)]

def first(x):
    x=tuple(x)
    return x[0] if x else None
def last(x):
    x=tuple(x)
    return x[-1] if x else None

def chk_oob(loc, x=0, y=0):
    return _chk_oob(loc,x,y)[0]

def _chk_oob(loc, x=0, y=0):
    """Returns OOB, and also which axis is OOB (returns False for OOB, True for ok)."""
    Y, X = (0 <= loc.y+y <= HEIGHT-1,
            0 <= loc.x+x <= WIDTH-1)
    return X and Y, X, Y

def chk_b_oob(loc, x=0, y=0):
    h = len(board_grid)
    w = len(board_grid[0])
    newx, newy = loc.x+x, loc.y+y
    return 0 <= newy <= h-1 and 0 <= newx <= w-1

def debug(*args):
    debug_log.write(str(args) + '\n')
    debug_log.flush()
print=debug

def blt_put_obj(obj, loc=None):
    x,y=loc or obj.loc
    x = x*2 +(0 if y%2==0 else 1)
    blt.clear_area(x,y,1,1)
    puts(x, y, obj)
    refresh()

def dist(a,b):
    a = getattr(a,'loc',a)
    b = getattr(b,'loc',b)
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.x-b.x)*(a.y-b.y))

def getitem(it, ind=0, default=None):
    try: return it[ind]
    except IndexError: return default

def puts(x, y, text):
    _puts(x, y, text)

def puts2(x, y, text):
    _puts(x, y+HEIGHT, text)

def _puts(x,y,a):
    if isinstance(a,str):
        blt.puts(x,y,a)
    else:
        if a.color:
            a = f'[color={a.color}]{a}[/color]'
        blt.puts(x,y,str(a))

def refresh():
    blt.refresh()

def get_and_parse_key():
    while 1:
        k = parsekey(blt.read())
        if k!='SHIFT':
            return k

def parsekey(k):
    b=blt
    valid = (b.TK_RETURN, b.TK_SHIFT, b.TK_ESCAPE, b.TK_UP, b.TK_DOWN, b.TK_RIGHT, b.TK_LEFT, b.TK_MOUSE_LEFT)
    if k and blt.check(blt.TK_WCHAR) or k in valid:
        k = keymap.get(k)
        if k and blt.state(blt.TK_SHIFT):
            k = k.upper()
            if k=='-': k = '_'
            if k=='/': k = '?'
            if k=='=': k = '+'
        return k

def get_mouse_pos():
    return blt.state(blt.TK_MOUSE_X), blt.state(blt.TK_MOUSE_Y)

def board_setup():
    Boards.b_1 = Board(Loc(0,0), '1')
    Boards.b_1.board_1()
    # Boards.b_2 = Board(Loc(1,0), '2')
    # Boards.b_2.board_2()

    # Boards.b_3 = Board(Loc(0,1), '3')
    # Boards.b_3.board_3()
    # Boards.b_4 = Board(Loc(1,1), '4')
    # Boards.b_4.board_4()

    board_grid[:] = [
        ['1', '2', None],
        # ['3', '4', None],
    ]
    Misc.B = Boards.b_1



def stats(castle=None, battle=False):
    pl = Misc.player
    if not pl: return
    move_str = ''
    if battle and Misc.current_unit:
        u = Misc.current_unit
        move, n_moves = u.cur_move, u.n_moves
        move_str = f' | Move {move}/{n_moves}'
    s=''
    st = s + f'[Caps:{pl.caps}] {move_str} | {Misc.B._map}'
    x = len(st)+2
    puts2(1, 0, blt_esc(st))
    y = 1
    refresh()

def status(msg):
    Misc.status.append(msg)

def blt_esc(txt):
    return txt.replace('[','[[').replace(']',']]')

def prompt():
    mp = ''
    status('> ')
    blt.refresh()
    while 1:
        k = get_and_parse_key()
        if not k: continue
        if k=='ENTER':
            return mp
        mp += k
        status('> '+mp)
        blt.refresh()

class Loc:
    def __init__(self, x, y):
        self.y, self.x = y, x

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, i):
        return (self.x, self.y)[i]

    def __repr__(self):
        return str((self.x, self.y))

    def __eq__(self, l):
        if isinstance(l, Loc):
            return (self.x, self.y) == (l.x, l.y)

    def __hash__(self):
        return hash(tuple(self))

    def mod(self, x=0, y=0):
        new = copy(self)
        new.y += y
        new.x += x
        return new

    def mod_r(self, n=1):
        return self.mod(n, 0)

    def mod_l(self, n=1):
        return self.mod(-n, 0)

    def mod_d(self, n=1):
        return self.mod(0, n)

    def mod_u(self, n=1):
        return self.mod(0, -n)

def rand_color(r, g, b):
    r = (r,r+1) if isinstance(r,int) else r
    g = (g,g+1) if isinstance(g,int) else g
    b = (b,b+1) if isinstance(b,int) else b
    return '#ff%s%s%s' % (
        hex(randrange(*r))[2:],
        hex(randrange(*g))[2:],
        hex(randrange(*b))[2:],
    )


class Board:
    """Game board (single screen)."""
    def __init__(self, loc, _map):
        self.clear()
        self.labels = []
        self.loc = loc
        self._map = str(_map)

    def __repr__(self):
        return f'<B: {self._map}>'

    def __getitem__(self, loc):
        o = self.B[loc.y][loc.x][-1]
        if isinstance(o,int):
            o = Objects[o]
        return o

    def __iter__(self):
        for y, row in enumerate(self.B):
            for x, cell in enumerate(row):
                yield Loc(x,y), cell

    def display(self, txt):
        w = max(len(l) for l in txt) + 1
        X,Y = 5, 2
        for y, ln in enumerate(txt):
            blt.clear_area(X, Y+y+1, w+3, 1)
            puts(X, Y+y+1, ' ' + ln)
        refresh()
        blt.read()

    def get_ids(self, loc):
        if isinstance(loc, Loc):
            loc = [loc]
        lst = []
        for l in loc:
            lst.extend(self.get_all(l))
        lst = [getattr(x, 'id', None) or x for x in lst]
        return lst

    def gen_graph(self, tgt):
        self.g = {}
        for loc, _ in self:
            if not self.is_blocked(loc):
                self.g[loc] = [n for n in self.neighbours(loc)
                               if (not self.is_blocked(n) and not self.get_being(n))
                                   or n==tgt
                              ]

    def next_move_to(self, src, tgt):
        p = self.find_path(src, tgt)
        return first(p)

    def find_path(self, src, tgt):
        """Greedy"""
        self.gen_graph(tgt)
        cur = src
        path = []
        visited = set([src])
        while 1:
            nbr = [n for n in self.g[cur] if n not in visited]
            next = first(sorted([(dist(n,tgt), id(n), n) for n in nbr]))
            if not next:
                break
            next = next[2]
            path.append(next)
            visited.add(next)
            cur = next
            if cur == tgt:
                return path
        return []


    def random_empty(self):
        while 1:
            loc = choice(list(self))[0]
            if self[loc] is Blocks.blank:
                return loc

    def random_rocks(self, n=1):
        for _ in range(n):
            BlockingItem(Blocks.rock, '', self.random_empty(), self._map)

    def clear(self):
        self.B = [mkrow() for _ in range(HEIGHT)]

    def found_type_at(self, type, loc):
        def get_obj(x):
            return Objects.get_by_id(x) or x
        return any(
            get_obj(x).type==type for x in self.get_all_obj(loc)
        )

    def get_all(self, loc):
        return [n for n in self.B[loc.y][loc.x]
                if n!=Blocks.blank
               ]

    def remove(self, obj, loc=None):
        loc = loc or obj.loc
        cell = self.B[loc.y][loc.x]
        cell.remove(obj if obj in cell else obj.id)

    def get_all_obj(self, loc):
        return [Objects[n] or n for n in self.B[loc.y][loc.x]
                if not isinstance(n, str)
               ]

    def get_being(self, loc):
        return first(o for o in self.get_all_obj(loc) if isinstance(o, Being) and o.alive)

    def load_map(self, map_num, for_editor=0, castle=None):
        _map = open(f'maps/{map_num}.map').readlines()
        self.containers = containers = []
        self.doors = doors = []
        self.specials = specials = defaultdict(list)
        self.buildings = []
        BL=Blocks
        roofs = []

        for y in range(HEIGHT):
            for x in range(WIDTH):
                char = _map[y][x*2 + (0 if y%2==0 else 1)]
                loc = Loc(x,y)
                if char != BL.blank:
                    if char==BL.rock:
                        BlockingItem(Blocks.rock, '', loc, self._map)

                    elif char==Blocks.door:
                        d = Item(Blocks.door, 'door', loc, self._map)
                        doors.append(d)

                    elif char==Blocks.rock3:
                        BlockingItem(Blocks.rock3, 'rock', loc, board_map=self._map)

                    elif char==Blocks.water:
                        Item(Blocks.water, 'water', loc, type=Type.water, board_map=self._map)

                    elif char==Blocks.roof:
                        Item(Blocks.roof, '', loc, self._map)
                        roofs.append(loc)

                    elif char in (Blocks.tree1, Blocks.tree2):
                        col = rand_color(33, (60,255), (10,140))
                        BlockingItem(char, 'tree', loc, self._map, color=col)

                    elif char == Blocks.bricks:
                        BlockingItem(char, '', loc, self._map, color=col)

                    elif char==Blocks.rock2:
                        Item(char, '', loc, self._map)

                    elif char in '0123456789':
                        specials[int(char)] = loc
                        if for_editor:
                            self.put(char, loc)

        self.handle_buildings(roofs)
        return containers, doors, specials

    def handle_buildings(self, roofs):
        g = defaultdict(list)
        for loc in roofs:
            for nloc in self.neighbours(loc):
                if B[nloc] == Blocks.roof:
                    g[loc].append(nloc)
        bld = []
        for loc, nbr in g.items():
            for b in bld:
                if


    def rect(self, a, b):
        lst = []
        for x in range(a.x, b.x+1):
            lst.extend( Loc(a.x, y) for y in range(a.y, b.y+1) )
        return lst


    def line(self, a, b):
        if a.x==b.x:
            return [Loc(a.x, y) for y in range(a.y, b.y+1)]
        elif a.y==b.y:
            return [Loc(x, a.y) for x in range(a.x, b.x+1)]

    def board_1(self):
        self.load_map('1')
        Elder(self.specials[2], '1')

    def screen_loc_to_map(self, loc):
        x,y=loc
        if y%2==1:
            x-=1
        x = int(round(x/2))
        return Loc(x,y)

    def draw(self, battle=False, castle=None):
        blt.clear()
        blt.color("white")
        for y, row in enumerate(self.B):
            for x, cell in enumerate(row):
                # tricky bug: if an 'invisible' item put somewhere, then a being moves on top of it, it's drawn, but
                # when it's moved out, the invisible item is drawn, but being an empty string, it doesn't draw over the
                # being's char, so the 'image' of the being remains there, even after being moved away.
                cell = [c for c in cell if getattr(c,'char',None)!='']
                a = last(cell)
                x*=2
                if y%2==1:
                    x+=1
                # if isinstance(a, str):
                    # puts(x,y,a)
                if isinstance(a, ID):
                    a = Objects[a]
                puts(x,y,a)

        for bld in self.buildings:
            if Misc.player.loc not in set(bld):
                for loc in bld:
                    puts(loc.x, loc.y, Blocks.rock)

        for y,x,txt in self.labels:
            puts(x,y,txt)
        stats()
        for n, msg in enumerate(Misc.status):
            puts2(1, 2+n, msg)
            Misc.status = []
        refresh()

    def neighbours(self, loc):
        l = [loc.mod_r(), loc.mod_l(), loc.mod_u(), loc.mod_d()]
        if loc.y%2==0:
            l.extend([loc.mod_u().mod_l(), loc.mod_d().mod_l()])
        else:
            l.extend([loc.mod_u().mod_r(), loc.mod_d().mod_r()])
        return [loc for loc in l if chk_oob(loc)]

    def put(self, obj, loc=None):
        """
        If loc is not given, try to use obj's own location attr.
        If loc IS given, update obj's own location attr if possible.
        """
        loc = loc or obj.loc
        if not isinstance(obj, (int, str)):
            obj.board_map = self._map
            obj.loc = loc
        try:
            self.B[loc.y][loc.x].append(getattr(obj, 'id', None) or obj)
        except Exception as e:
            sys.stdout.write(str(loc))
            raise

    def is_blocked(self, loc):
        for x in self.get_all(loc):
            if isinstance(x, int):
                x = Objects.get_by_id(x)
            if x in BLOCKING or getattr(x, 'type', None) in BLOCKING:
                return True
        return False


class HandleRoof:
    def __init__(self, B):
        self.B = B

    def find_connected_roof(self, loc, bld=None, seen=None):
        seen = seen or set([loc])
        bld = bld or set([loc])
        B = self.B
        for loc in B.neighbours(loc):
            if loc in seen:
                continue
            if B[loc] in (Blocks.roof, Blocks.door):
                bld.add(loc)
                find_connected_roof(B, loc, bld, seen)
            seen.add(loc)
        return bld

    def find_inner(self, bld, seen=None):
        min_x, max_x = min(l.x for l in bld), max(l.x for l in bld)
        min_y, max_y = min(l.y for l in bld), max(l.y for l in bld)
        for l in bld:
            nbr = self.B.neighbours(l)
            for n in nbr:
                if min_x<n.x<max_x or min_y<n.y<max_y:
                    break
            return n

    def fill_roof(self, loc, bld, fill=None, seen=None):
        B = self.B
        seen = seen or set([loc])
        fill = fill or set([loc])
        for loc in B.neighbours(loc):
            if loc in seen:
                continue
            if B[loc] not in (Blocks.roof, Blocks.door):
                fill.add(loc)
                fill_roof(B, loc, bld, fill, seen)
            seen.add(loc)
        return fill


class Boards:
    @staticmethod
    def get_by_map(map):
        return getattr(Boards, 'b_'+map)

    @staticmethod
    def get_by_loc(loc):
        return board_grid[loc.y][loc.x]

class BeingItemBase:
    is_player = 0
    player = None
    state = 0
    color = None
    _str = None
    id = None

    def __init__(self, char, name, loc=None, board_map=None, put=True, id=None, type=None, color=None, n=0):
        self.char, self.name, self.loc, self.board_map, self.id, self.type, self.color, self.n = \
                char, name, loc, board_map, id, type, color, n
        if id:
            Objects[id] = self
        if board_map and put:
            self.B.put(self)

    def __str__(self):
        # c=self.char
        # if isinstance(c, int):
        #     c = '[U+{}]'.format(hex(c)[2:])
        # return c
        return self.char

    def tele(self, loc):
        self.B.remove(self)
        self.put(loc)

    def put(self, loc):
        self.loc = loc
        B=self.B
        B.put(self)

    def has(self, id):
        return self.inv.get(id)

    def remove1(self, id):
        self.inv[id] -= 1

    def add1(self, id, n=1):
        self.inv[id] += n

    def move_to_board(self, _map, specials_ind=None, loc=None):
        to_B = getattr(Boards, 'b_'+_map)
        if specials_ind is not None:
            loc = to_B.specials[specials_ind]
        self.B.remove(self)
        self.loc = loc
        to_B.put(self)
        self.board_map = to_B._map
        return to_B

    @property
    def B(self):
        if self.board_map:
            return getattr(Boards, 'b_'+self.board_map)


class Item(BeingItemBase):
    board_map = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inv = defaultdict(int)

    def __str__(self):
        print('in Item.__str__, self.char=', self.char)
        return super().__str__()

    def __repr__(self):
        return f'<I: {self.char}>'

    def move(self, dir, n=1):
        my,mx = dict(h=(0,-1), l=(0,1), y=(-1,-1), u=(-1,1), b=(1,-1), n=(1,1))[dir]
        if mx==1 and my and self.loc.y%2==0:
            mx=0
        if mx==-1 and my and self.loc.y%2==1:
            mx=0
        m = my,mx
        for _ in range(n):
            new = self.loc.mod(m[1],m[0])
            self.B.remove(self)
            self.loc = new
            self.B.put(self)

class Knife(Item):
    char = Blocks.knife
    type = Type.knife

class BlockingItem(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Type.blocking

class PartyMixin:
    def total_strength(self):
        return sum(u.hp for u in self.live_party())

    def live_party(self):
        return list(u for u in filter(None, self.party) if u.alive)


class BattleUI:
    def __init__(self, B):
        self.B=B

    def auto_battle(self, a, b):
        a_str = a.total_strength()
        b_str = b.total_strength()
        winner, loser, hp = (a,b,b_str) if a_str>b_str else (b,a,a_str)
        if winner.is_player:
            winner.xp += loser.total_strength()//2
        for u in winner.live_party():
            u.hp = u.max_hp
        loser.party = pad_none([], 6)

    def go(self, a, b):
        self._go(a,b)
        Misc.B = self.B

    def _go(self, a, b):
        a._strength = a.total_strength()
        b._strength = b.total_strength()
        B = Misc.B = Boards.b_battle = Board(None, 'battle')
        B.load_map('battle')

        loc = B.specials[1]
        for u in a.live_party():
            B.put(u, loc)
            loc = loc.mod_d(2)
        loc = B.specials[2]
        for u in b.live_party():
            B.put(u, loc)
            loc = loc.mod_d(2)

        B.random_rocks(20)
        B.draw(battle=1)
        while 1:
            B.draw(battle=1)
            for u in a.live_party():
                rv = self.handle_unit_turn(B, a, b, u)
                if rv==AUTO_BATTLE:
                    break
            if self.check_for_win(a,b):
                break
            for u in b.live_party():
                rv = self.handle_unit_turn(B, b, a, u)
                if rv==AUTO_BATTLE:
                    break
            if self.check_for_win(a,b):
                break

    def handle_unit_turn(self, B, a, b, unit):
        h,u = a, unit
        Misc.current_unit = u   # for stats()
        while 1:
            if not u.alive:
                break
            if not h.is_ai():
                u.color = 'lighter blue'
                blt_put_obj(u)
                ok = handle_ui(u, hero=h)
                u.color = None
                if not ok:
                    return
                if ok==END_MOVE:
                    u.cur_move = u.speed
                    u.color=None
                    blt_put_obj(u)
                    break
                if ok==AUTO_BATTLE:
                    self.auto_battle(a, b)
                    return AUTO_BATTLE
            else:
                tgt = u.closest(b.live_party())

                if tgt:
                    u.color = 'lighter blue'
                    blt_put_obj(u)
                    sleep(0.25)
                    path = u.path.get(tgt) or B.find_path(u.loc, tgt.loc)
                    if len(path)==1:
                        u.hit(tgt)
                    elif path:
                        u.move(loc=first(path))
                        u.path[tgt] = path[1:]
                    else:
                        return

                    B.draw(battle=1)
                    if u.cur_move==0:
                        u.cur_move = u.speed
                        u.color=None
                        blt_put_obj(u)
                        break


class Skills(Enum):
    small_guns = auto()
    big_guns = auto()
    energy_weapons = auto()
    melee_weapons = auto()
    unarmed = auto()
    throwing = auto()
    first_aid = auto()
    doctor = auto()
    sneak = auto()
    lockpick = auto()
    steal = auto()
    traps = auto()
    science = auto()
    repair = auto()
    speech = auto()
    barter = auto()
    gambling = auto()
    outdoorsman = auto()

class LoadBoard:
    def __init__(self, new, b_new):
        self.new, self.b_new = new, b_new

class Being(BeingItemBase):
    hp = 1
    max_hp = 1
    is_being = 1
    type = None
    char = None
    n_moves = None
    path = None
    caps = 0

    strength = 5
    perception = 5
    endurance = 5
    charisma = 5
    intelligence = 5
    agility = 5
    luck = 5
    armor_class = 10
    action_points = 7
    melee_attack = 1
    damage_resistance = 0
    poison_resistance = 0
    radiation_resistance = 0
    healing_rate = 1
    critical_chance = 1

    def __init__(self, loc=None, board_map=None, put=True, id=None, name=None, state=0, char='?',
                 color=None):
        self.loc, self.board_map, self._name, self.state, self.color  = \
                loc, board_map, name, state, color
        self.char = self.char or char
        self.inv = defaultdict(int)
        self.cur_move = self.n_moves
        if id:
            self.id = id
        if self.id:
            Objects[self.id] = self
        if board_map and put:
            self.B.put(self)
        self.max_health = self.hp
        self.path = {}
        self.skills = defaultdict(int)
        self.traits = []

    def __str__(self):
        return super().__str__() if self.hp>0 else Blocks.rubbish

    @property
    def name(self):
        return self._name or self.__class__.__name__

    def talk(self, being, yesno=False, resp=False):
        """Messages, dialogs, yes/no, prompt for response, multiple choice replies."""
        if isinstance(being, int):
            being = Objects.get(being)
        print('talk to', being)
        if not yesno and not resp:
            Talk(self.B, being).talk()
            return

        loc = being.loc
        conv = conv_str[being.id]
        tree = conversations[being.id]
        if isinstance(dialog, str):
            dialog = [dialog]
        x = min(loc.x, 60)
        multichoice = 0

        for m, txt in enumerate(dialog):
            lst = []
            if isinstance(txt, (list,tuple)):
                multichoice = len(txt)
                for n, t in enumerate(txt):
                    lst.append(f'{n+1}) {t}')
                txt = '\n'.join(lst)
            x = min(40, x)
            w = 78 - x
            if yesno:
                txt += ' [[Y/N]]'
            lines = (len(txt) // w) + 4
            txt_lines = wrap(txt, w)
            txt = '\n'.join(txt_lines)
            offset_y = lines if loc.y<8 else -lines

            y = max(0, loc.y+offset_y)
            W = max(len(l) for l in txt_lines)
            blt.clear_area(x+1, y+1, W, len(txt_lines))
            puts(x+1,y+1, txt)
            refresh()

            if yesno:
                # TODO in some one-time dialogs, may need to detect 'no' explicitly
                k = get_and_parse_key()
                return k in 'Yy'

            elif multichoice:
                for _ in range(2):
                    k = get_and_parse_key()
                    try:
                        k=int(k)
                    except ValueError:
                        k = 0
                    if k in range(1, multichoice+1):
                        return k

            if resp and m==len(dialog)-1:
                i=''
                puts(0,1, '> ')
                refresh()
                for _ in range(10):
                    k = get_and_parse_key()
                    if k==' ': break
                    i+=k
                    puts(0,1, '> '+i)
                    refresh()
                return i

            refresh()
            k=None
            while k!=' ':
                k = get_and_parse_key()
            self.B.draw()


    def _move(self, dir):
        my,mx = dict(h=(0,-1), l=(0,1), y=(-1,-1), u=(-1,1), b=(1,-1), n=(1,1), H=(0,-1), L=(0,1))[dir]
        if mx==1 and my and self.loc.y%2==0:
            mx=0
        if mx==-1 and my and self.loc.y%2==1:
            mx=0
        m = mx,my

        # Here if for example we're going in down-right dir, and we're OOB in downwards direction, we want to switch to
        # the board below; if going in the same dir but we're OOB only in rightward dir, we want to switch to the board
        # to the right. If OOB in both dirs, go to the board to the down-right dir.
        ok, keepX, keepY = _chk_oob(self.loc, *m)
        if ok:
            return True, self.loc.mod(*m)
        else:
            if keepX: mx = 0
            if keepY: my = 0
            if chk_b_oob(self.B.loc, mx, my):
                x, y = self.loc.mod(mx, my)
                if keepY:
                    x = 0 if mx==1 else (WIDTH-1)
                if keepX:
                    y = 0 if my==1 else (HEIGHT-1)

                return LoadBoard(Loc(x,y), self.B.loc.mod(mx,my))
        return 0, 0

    def move(self, dir=None, attack=True, loc=None):
        if self.cur_move==0: return None, None
        B = self.B
        if dir:
            rv = self._move(dir)
            if isinstance(rv, LoadBoard):
                return rv
            new = rv[1]
        else:
            new = loc

        if new:
            being = B.get_being(new)
            if being and being.alive:
                if not attack:
                    return None

                self.handle_directional_turn(dir, new)
                if self.player != being.player:
                    self.attack(being)
                if self.cur_move:
                    self.cur_move -= 1
                return True, True

        if new and B.is_blocked(new):
            new = None

        if new:
            B.remove(self)
            if new[0] is None:
                return new
            self.handle_directional_turn(dir, new)
            self.loc = new
            self.put(new)
            refresh()
            if self.cur_move:
                self.cur_move -= 1
            if self.player and not self.player.is_ai:
                self.handle_player_move(new)
            return True, True
        return None, None

    def handle_directional_turn(self, dir, loc):
        """Turn char based on which way it's facing."""
        name = self.__class__.__name__.lower()
        if hasattr(Blocks, name+'_r'):
            to_r = False
            if loc:
                to_r = loc.x>self.loc.x or (loc.x==self.loc.x and loc.y%2==1)
            to_l = not to_r
            if dir and dir in 'hyb' or to_l:
                self.char = getattr(Blocks, name+'_l')
            else:
                self.char = getattr(Blocks, name+'_r')

    def handle_player_move(self, new):
        B=self.B
        pick_up = [ID.gold]
        items = B.get_all_obj(new)
        top_obj = last(items)
        if top_obj:
            # why does this work with unicode offsets? maybe it doesn't..
            if isinstance(top_obj, int):
                top_obj = Objects[top_obj.id]

        for x in reversed(items):
            if x.id in pick_up:
                if self.player:
                    pass
                B.remove(x, new)

        names = [o.name for o in B.get_all_obj(new) if o.name and o!=self]
        plural = len(names)>1
        names = ', '.join(names)
        if names:
            a = ':' if plural else ' a'
            status(f'You see{a} {names}')

    def attack(self, obj):
        if obj.loc in self.B.neighbours(self.loc):
            self.hit(obj)

    def get_dir(self, b):
        a = self.loc
        b = getattr(b, 'loc', None) or b
        if a.x<=b.x and a.y<b.y: return 'n'
        elif a.x<=b.x and a.y>b.y: return 'u'
        elif a.x>=b.x and a.y<b.y: return 'b'
        elif a.x>=b.x and a.y>b.y: return 'y'
        elif a.x<b.x: return 'l'
        elif a.x>b.x: return 'h'

    def hit(self, obj, ranged=False, dmg=None, mod=1, type=None, descr=''):
        if dmg:
            a = dmg
        else:
            str = self.strength
            a = int(round((str * self.n * mod)/3))
        b = obj.hp
        a = obj.defend(a, type)
        c = b - a

        if descr:
            descr = f' with {descr}'
        if a:
            status(f'{self} hits {obj}{descr} for {a} HP')
        else:
            status(f'{self} fails to hit {obj}{descr}')

        if c <= 0:
            status(f'{obj} dies')
            obj.hp = 0
        else:
            obj.hp = c

        self.cur_move = 0

    def defend(self, dmg, type):
        x = 0
        if type==Type.melee_attack:
            x = self.defense
        return dmg - x

    def action(self):
        print ("in def is_near()")
        def is_near(id):
            return getattr(ID, id) in self.B.get_ids(self.B.neighbours(self.loc) + [self.loc])

        if is_near('elder'):
            self.talk(Objects.elder)
            self.caps += 150
            Item('f', 'Vault 13 Flask', id=ID.vault13_flask)
            self.inv[ID.vault13_flask] += 1

    def use(self):
        ascii_letters = string.ascii_letters
        for n, (id,qty) in enumerate(self.inv.items()):
            item = Objects[id]
            puts(0,n, f' {ascii_letters[n]}) {item.name:4} - {qty} ')
        ch = get_and_parse_key()
        item = None
        if ch in ascii_letters:
            try:
                item_id = list(self.inv.keys())[string.ascii_letters.index(ch)]
            except IndexError:
                return
        if not item_id: return

        status('Nothing happens')

    def closest(self, objs):
        return first( sorted(objs, key=lambda x: dist(self.loc, x.loc)) )

    @property
    def alive(self):
        return self.hp>0

    @property
    def dead(self):
        return not self.alive

class Elder(Being):
    id = ID.elder
    char = Blocks.woman

class RangedWeapon:
    id = None
    dmg = None
    _name = None

    def __init__(self):
        Objects[self.id] = self

    @property
    def name(self):
        if self._name:
            return self._name
        chars = self.__class__.__name__
        n=chars[0]
        for c in chars[1:]:
            if c.isupper():
                n+=' '
            n += c
        return n

    def select_target(self, B):
        x=None
        while x not in ('CLICK', ' ', blt.TK_ESCAPE):
            B.draw()
            loc = Loc(*get_mouse_pos())
            puts(loc.x, loc.y, Blocks.circle3)
            refresh()
            x = get_and_parse_key()
        if x=='CLICK':
            loc = Loc(*get_mouse_pos())
            return B.screen_loc_to_map(loc)

    def ai_fire(self, B, being, targets):
        self.apply(being, choice(targets))

    def fire(self, B, being):
        B.draw()
        loc = self.select_target(B)
        if loc:
            tgt = B.get_being(loc)
            if tgt:
                self.apply(being, tgt)

    def apply(self, being, tgt):
        pass


class Pistol(RangedWeapon):
    dmg = 5
    cost = 4
    type = Type.pistol

    def apply(self, being, tgt):
        loc = being.loc
        dmg = self.dmg
        being.hit(tgt, dmg=dmg, type=Type.ranged_attack, descr=self.name)
        # Use some hit animation...
        blt_put_obj(Blocks.bolt1, loc)
        sleep(0.25)
        blt_put_obj(being, loc)


class Player(PartyMixin, Being):
    xp = 0
    speed = 5
    alive = 1
    level = 1
    type = Type.player
    mana = 20
    is_player = True
    level_tiers = enumerate((500,2000,5000,10000,15000,25000,50000,100000,150000))
    char = Blocks.player_l
    hp = 44

    def __init__(self, *args, player=None, party=None, spells=None, **kwargs ):
        super().__init__(*args, **kwargs)
        self.party = []

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f'<P: {self.name}>'

    def is_ai(self):
        return not self.player or self.player.is_ai

    def add_xp(self, xp):
        self.xp+=xp
        for lev, xp in self.level_tiers:
            if xp > self.xp:
                break
            self.level = lev

class IndependentParty(Player):
    pass

class Shooter(Being):
    strength = 6
    defense = 3
    hp = 10
    speed = 4
    cost = 30

    def fire(self, B, player):
        char = Blocks.bullet
        a = Bullet(char, '', loc=self.loc)
        B.put(a)
        mod = 1
        for _ in range(self.range):
            a.move(self.last_dir)
            if B.found_type_at(Type.blocking, a.loc):
                mod = 0.5
            being = B.get_being(a.loc)
            if being and being.alive and being.player!=player:
                self.hit(being, ranged=1, mod=mod)
                B.remove(being)     # shuffle on top of arrow
                B.put(being)
                break
            blt_put_obj(a)
            sleep(0.15)

class Saves:
    saves = {}
    loaded = 0

    def load(self, name):
        global Objects, done_events
        fn = f'saves/{name}.data'
        sh = shelve.open(fn, protocol=1)
        self.saves = sh['saves']
        s = self.saves[name]
        board_grid[:] = s['boards']
        Objects = s['objects']
        done_events = s['done_events']
        player = Objects[ID.player]
        bl = s['cur_brd']
        B = board_grid[bl.y][bl.x]
        return player, B

    def save(self, cur_brd, name=None):
        fn = f'saves/{name}.data'
        sh = shelve.open(fn, protocol=1)
        s = {}
        s['boards'] = board_grid
        s['cur_brd'] = cur_brd
        s['objects'] = Objects
        s['done_events'] = done_events
        player = Objects.player
        bl = cur_brd
        B = board_grid[bl.y][bl.x]
        sh['saves'] = {name: s}
        sh.close()
        return B.get_all(player.loc), name

def main(load_game):
    blt.open()
    blt.set(f"window: resizeable=true, size=80x25, cellsize=auto, title='Atom Punk'; font: FreeMono.ttf, size={SIZE}")
    blt.set("input.filter={keyboard, mouse+}")
    blt.color("white")
    blt.composition(True)
    blt.clear()
    if not os.path.exists('saves'):
        os.mkdir('saves')
    Misc.is_game = 1

    ok=1
    board_setup()
    player = Misc.player = Player(Boards.b_1.specials[1], board_map='1', id=ID.player)
    Misc.B.draw()

    while ok:
        ok = handle_ui(Misc.player)
        if ok=='q': return
        if ok==END_MOVE:
            blt_put_obj(player)
            player.cur_move = player.speed
            ok=1


def handle_ui(unit, battle=False):
    if not unit.cur_move:
        return END_MOVE
    k = None
    while not k:
        k = get_and_parse_key()
    puts(0,1, ' '*78)
    B = Misc.B
    if k=='q':
        return 'q'
    elif k in 'yubnhlHL':
        if k in 'HL':
            k = k.lower()
            unit.last_dir = k
            for _ in range(5):
                rv = unit.move(k)
                if not rv:
                    return END_MOVE
                if isinstance(rv, LoadBoard):
                    break
        else:
            rv = unit.move(k)
            unit.last_dir = k
            if not rv:
                return END_MOVE

        unit.last_dir = k
        if isinstance(rv, LoadBoard):
            loc = rv.b_new
            if chk_b_oob(loc) and board_grid[loc.y][loc.x]:
                Misc.B = unit.move_to_board(Boards.get_by_loc(loc), loc=rv.new)
        stats()

    elif k == '.':
        pass
    elif k == 'f':
        if isinstance(unit, Archer):
            unit.fire(B, hero)
    elif k == 'o':
        name = prompt()
        Misc.hero, B = Saves().load(name)
    elif k == 's':
        if hero:
            hero.cast_spell(B)
    elif k == 'a':
        if Misc.B == Boards.b_battle:
            return AUTO_BATTLE
    elif k == 'S':
        name = prompt()
        Saves().save(Misc.B.loc, name)
        status(f'Saved game as "{name}"')
        refresh()
    elif k == 'v':
        status(str(unit.loc))
    elif k == ' ':
        if battle:
            unit.cur_move=0
        else:
            unit.action()
    elif k == '5' and DBG:
        k = get_and_parse_key()
        k2 = get_and_parse_key()
        if k and k2:
            try:
                print(B.B[int(k+k2)])
                status(f'printed row {k+k2} to debug')
            except:
                status('try again')

    elif k == 't' and DBG:
        # debug teleport
        mp = ''
        while 1:
            k = get_and_parse_key()
            if not k: break
            mp+=k
            status(mp)
            refresh()
            if mp.endswith(' '):
                try:
                    x,y=mp[:-1].split(',')
                    unit.tele(Loc(int(x), int(y)))
                except Exception as e:
                    print(e)
                break

    elif k == 'u':
        unit.use()

    elif k == 'E':
        B.display(str(B.get_all(unit.loc)))
    elif k == 'm':
        manage_castles()

    elif k == 'i':
        txt = []
        for id, n in Misc.player.inv.items():
            item = Objects[id]
            if item and n:
                txt.append(f'{item.name} {n}')
        B.display(txt)

    B.draw(battle = (not unit.is_player))
    return 1


def editor(_map):
    blt.open()
    blt.set("window: resizeable=true, size=80x25, cellsize=auto, title='Editor'; font: FreeMono.ttf, size=20")
    blt.color("white")
    blt.composition(True)

    blt.clear()
    Misc.is_game = 0
    loc = Loc(20, 8)
    brush = None
    written = 0
    fname = f'maps/{_map}.map'
    if not os.path.exists(fname):
        with open(fname, 'w') as fp:
            for n in range(HEIGHT):
                prefix = '' if n%2==0 else ' '
                fp.write(prefix + (Blocks.blank + ' ')*WIDTH + '\n')
    B = Board(None, _map)
    setattr(Boards, 'b_'+_map, B)
    B.load_map(_map, 1)
    B.draw()

    while 1:
        k = get_and_parse_key()
        if k=='Q': break
        elif k and k in 'hlyubnHL':
            n = 1
            if k in 'HL':
                n = 5
            my,mx = dict(h=(0,-1), l=(0,1), y=(-1,-1), u=(-1,1), b=(1,-1), n=(1,1), H=(0,-1), L=(0,1))[k]
            if mx==1 and my and loc.y%2==0:
                mx=0
            if mx==-1 and my and loc.y%2==1:
                mx=0

            for _ in range(n):
                if brush:
                    if brush=='T':
                        B.B[loc.y][loc.x] = [choice((Blocks.tree1, Blocks.tree2))]
                    else:
                        B.B[loc.y][loc.x] = [brush]
                if chk_oob(loc.mod(mx,my)):
                    loc = loc.mod(mx,my)

        elif k == ' ':
            brush = None
        elif k == 'e':
            brush = Blocks.blank
        elif k == 'r':
            brush = Blocks.rock
        elif k and k in '0123456789':
            B.put(k, loc)
        elif k == 'w':
            Item(B, Blocks.water, 'water', loc)
        elif k == 'x':
            Item(Blocks.hex, '', loc, B._map)
        elif k == 'B':
            B.put(Blocks.bricks, loc)
            brush = Blocks.bricks
        elif k == 't':
            B.put(choice((Blocks.tree1, Blocks.tree2)), loc)
            brush = 'T'
        elif k == 'o':
            cmds = 'h1 h2'.split()
            cmd = ''
            while 1:
                k = get_and_parse_key()
                if k:
                    cmd += k
                if cmd == 'h1':
                    B.put(Blocks.house_c1, loc)
                elif cmd == 'h2':
                    B.put(Blocks.house_c2, loc)
                elif any(c.startswith(cmd) for c in cmds):
                    continue
                break

        elif k == 'E':
            puts(2,2, 'Are you sure you want to clear the map? [Y/N]')
            y = get_and_parse_key()
            if y=='Y':
                for row in B.B:
                    for cell in row:
                        cell[:] = [Blocks.blank]
                B.B[-1][-1].append('_')
        elif k == 'f':
            B.put(Blocks.shelves, loc)
        elif k == 'W':
            with open(f'maps/{_map}.map', 'w') as fp:
                for n, row in enumerate(B.B):
                    if n%2==1:
                        fp.write(' ')
                    for cell in row:
                        a = cell[-1]
                        fp.write(str(a) + ' ')
                    fp.write('\n')
            written=1

        B.draw()
        x = loc.x*2 + (0 if loc.y%2==0 else 1)
        blt.clear_area(x,loc.y,1,1)
        puts(x, loc.y, Blocks.circle3)
        if brush==Blocks.blank:
            tool = 'eraser'
        elif brush==Blocks.rock:
            tool = 'rock'
        elif not brush:
            tool = ''
        else:
            tool = brush
        puts(73,1, tool)
        puts(0 if loc.x>20 else 35,
             0, str(loc))
        # loc = Loc(x,loc.y)
        # print("loc", loc)
        puts(1, HEIGHT+2, blt_esc(str(B.get_all_obj(loc))))
        refresh()
        if written:
            puts(65,2, 'map written')
            written=0
        # win.move(loc.y, loc.x)
    blt.set("U+E100: none; U+E200: none; U+E300: none; zodiac font: none")
    blt.composition(False)
    blt.close()


if __name__ == "__main__":
    argv = sys.argv[1:]
    load_game = None
    for a in argv:
        if a == '-d':
            DBG = True
        if a and a.startswith('-l'):
            load_game = a[2:]
        if a and a.startswith('-s'):
            SIZE = int(a[2:])
    if first(argv) == 'ed':
        editor(argv[1])
    else:
        main(load_game)
