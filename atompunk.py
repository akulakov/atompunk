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
import heapq
from copy import copy  #, deepcopy
from enum import Enum, auto

"""
Atom Punk
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
    banize = auto()
    chim = auto()
    kyssa = auto()
    aykin = auto()
    arette = auto()
    arette2 = auto()
    st_junien = auto()
    c_guard = auto()
    metzger = auto()
    lignac = auto()
    leblanc = auto()
    vic = auto()

    arroyo_map_loc = auto()
    klamath_map_loc = auto()
    den_map_loc = auto()


class Type(Enum):
    door = auto()
    roof = auto()
    door1 = auto()
    container = auto()
    blocking = auto()
    player = auto()
    guard = auto()
    vault13_flask = auto()
    cap = auto()
    ranged_attack = auto()
    healing_powder = auto()
    stimpack = auto()

    knife = auto()
    pistol223 = auto()
    pipe_rifle = auto()
    hunting_rifle = auto()
    spear = auto()

    fmj223 = auto()
    magnum44fmj = auto()
    mm10 = auto()


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
    },

    ID.player: {1: 'The wastes have claimed your life..........'},
    ID.kyssa: {1: 'The way you hold that spear.. uhh.. Let me teach you a few things about using spears.',
               2: 'Okay',
               3: 'NO! I know how to hold a spear, thank you very much.'
              },

    ID.aykin: {1: 'Can you tell me anything about nearby towns?',
               2: "There's the Den, but I hardly ever been there. And other folks here, aside from traders, will tell you the same. Travel is dangerous in this here country.",
              },

    ID.arette: {1: 'Hello {}, how is the Wasteland treating you today?',
                2: "Can't complain!",
                3: "Wait, how do you know my name?",
                4: "Your travels are causing something of a stir. You are being noticed.",
                5: "Noticed by who?",
                6: "By anyone and everyone. People paying attention. People looking for someone they can use, someone who can help, or harm, someone who may need to be stopped if things spin out of hand.",
                7: "That explains exactly nothing. If you wish to warn me, give me something tangible. Answer some questions, because this is starting to feel like a waste of time.",
                8: "Very well. You can ask one question.",
                9: "Where can I find the GECK?",
                10: "Where is Vault 13?",
                11: "Where can I find Vic?",
                12: "Hah, that's an old one. Nobody even knows about them, and a few people who do would give up their right hand to get their left hand on one.",
                13: "That's not something I can tell you right now.",
                14: "He ran into some trouble with the Slaverunners. You'll find him with them, if my information is still up to date. But beware: those fellows don't kid.",
              },

    ID.arette2: {1: "There's nothing more I can tell you."},

    Type.guard: [
        {1: 'Move along, now'},
        {1: 'Nothing to see here'},
        {1: "Whatcha lookin' at?"},
        {1: "Oh look, a tribal.. haven't seen one in a while"},
        {1: "This is our turf, in case you're wonderin'"},
        ],

    ID.lignac: {1: "What is this place?",
                2: "Slaver's guild.",
                3: "What do you do?",
                4: "What the fuck do you think, we buy and sell slaves.",
                5: "Where do you get slaves?",
                6: "Ah, you know.. here and there.. and everywhere. I guess.",
                7: "Who runs this place?",
                8: "Metzger. He's in the building to the west. If you need to talk to him, make sure it's something important, he's got a lot on his plate and he's really pissed at that Vic guy. Oh yeah, and he's got a short temper.",
                9: "Why is he pissed at Vic?",
                10: "That's above my pay grade. You can ask him, if you dare.",
               },

    ID.metzger: {1: "The fuck.. this is not a tribal drumming circle you know. What the fuck are you doing here?, - and make it quick.",
                2: "Do you know someone named Vic?",
                3: "Yes, he pissed me off big time with his radio.. tried to run away, too",
                4: "What radio?",
                5: "What the fuck do you know about radios, tribal? Get out of my sight.",
                6: "Can I see Vic?",
                7: "Yeah, knock yourself out, talk to this useless shit. I should probably just strangle him, that would suit him right. If you do that I won't even mind.",
                8: "That was a joke, touch any of my property and I sell you for dog meat. Or worse.",
                9: "What's worse than dog meat?",
                10: "Gecko meat, I guess. Too oily.",
               },

    ID.leblanc: {
        1: 'Alright what do you need tribal?',
        2: 'Metzger said I can see Vic..',
        3: "Whoa he's sending tribals in now? Is it some kind of old injun tor-chure? Well the door's right there, do you need a red 'arpet too?'",
    },

}

conversations = {
    Type.guard: [1],
    ID.player: [1],
    ID.lignac: list(range(1,11)),
    ID.metzger: list(range(1,11)),
    ID.leblanc: [1,2,3],
    ID.aykin: [1,2],
    ID.kyssa: [1, [2,3]],
    ID.arette2: [1],
    ID.arette: [1, 2, 3, 4, 5, 6, 7, 8,
                [[9,12], [10,13], [11,14]],
               ],
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
    def __init__(self, B, being, id_or_type=None, rand=False):
        self.B = B
        id = id_or_type or being.id
        self.conv_str, self.conversations = conv_str[id], conversations[id]
        print( isinstance(self.conv_str, SEQ_TYPES) , rand)
        if isinstance(self.conv_str, SEQ_TYPES) and rand:
            self.conv_str = choice(self.conv_str)
        print("self.conv_str", self.conv_str)

        self.loc = being.loc
        self.ind = 0
        self.current = self.conversations
        self.choice_stack = []
        self.last_conv = None
        self.conv = None

    def choose(self, txt):
        multichoice = len(txt)
        lst = []
        for n, t in enumerate(txt):
            if isinstance(t, SEQ_TYPES):
                t = t[0]
            txt = self.conv_str[t].format(Misc.name)
            lst.append(f'{n+1}) {txt}')
        txt = '\n'.join(lst)
        self.display(txt, False)
        for _ in range(3):
            k = get_and_parse_key()
            if k=='ESCAPE':
                return
            try:
                k=int(k)
            except ValueError:
                k = 0
            if k in range(1, multichoice+1):
                return k

    def talk(self):
        try:
            self.last_conv = conv = self.current[self.ind]
        except Exception as e:
            return
        if isinstance(conv, SEQ_TYPES):
            self.choice_stack.append(conv)
            i = self.choose(conv)
            if i is None:
                return
            self.current = ch = conv[i-1]
            if isinstance(ch, int):
                return i
            self.ind = 1
        else:
            rv = self.display(self.conv_str[conv])
            if not rv: return
            self.ind += 1
        rv = self.talk()
        return rv

    def display(self, txt, wait=True):
        txt = txt.format(Misc.name)
        self.B.draw()
        x = min(self.loc.x, 60)

        x = min(40, x)
        w = 78 - x
        lines = (len(txt) // w) + 4
        txt_lines = wrap(txt, w)
        txt = '\n'.join(txt_lines)
        offset_y = lines if self.loc.y<8 else -lines

        y = max(0, self.loc.y+offset_y)
        W = max(len(l) for l in txt_lines) + 1
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
    bottle = '\u26b9'
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
    circle4 = '\u25cf'
    woman = '\u2700'
    knife = '\u26e0'
    cupboard = '\u269a'
    house_c1 = '\u250c'
    house_c2 = '\u2518'
    hex = '\u26e2'
    roof = hex
    door = '+'
    banize = player_f
    location = '\u25f0'
    party = '\u25ce'
    ant = '\u2707'
    pistol = '\u2734'
    rifle = '\u2736'
    ammo = '-'
    hit1 = '~'
    hit2 = '\u2735'
    stimpack = '\u244c'

    npc2 = '\u2702'
    npc3 = '\u26fd' # Metzger
    spear = '\u008e'


BLOCKING = [Blocks.rock, Type.door1, Type.blocking, Type.roof]


class Misc:
    status = []
    current_unit = None
    player = None
    combat = False
    name = 'Nameless'

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

def blt_put_obj(obj, loc=None, do_refresh=True):
    x,y=loc or obj.loc
    x = x*2 +(0 if y%2==0 else 1)
    blt.clear_area(x,y,1,1)
    puts(x, y, obj)
    if do_refresh:
        refresh()

def dist(a,b):
    a = getattr(a,'loc',a)
    b = getattr(b,'loc',b)
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.x-b.x)*(a.y-b.y))

def getitem(it, ind=0, default=None):
    try: return it[ind]
    except IndexError: return default

def puts(x, y, text, color=None):
    _puts(x, y, text, color=color)

def puts2(x, y, text):
    _puts(x, y+HEIGHT, text)

def _puts(x,y,a, color=None):
    if isinstance(a,str):
        if color:
            a = f'[color={color}]{a}[/color]'
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



def stats(battle=False):
    pl = Misc.player
    if not pl: return
    move_str = ''
    if Misc.combat:
        move, speed = pl.cur_move, pl.speed
        move_str = f' | Move {move}/{speed}'
    s=''
    eqp = pl.equipped[0] or ''
    if eqp:
        eqp = blt_esc(f'| {Objects[eqp].name}')
    st = s + f'[{pl.hp}/{pl.max_hp}] [Caps:{pl.caps}] {move_str} | {Misc.B._map} {eqp}'
    puts2(1, 0, blt_esc(st))
    refresh()

def status(msg):
    Misc.status.append(msg)

def blt_esc(txt):
    return txt.replace('[','[[').replace(']',']]')

def make_choice(B, txt, choices):
    status(txt + ' > ')
    B.draw()
    while 1:
        k = get_and_parse_key()
        if not k: continue
        if k in ('ENTER', 'ESCAPE'):
            return
        if k in choices:
            return k

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
        self.monsters = []
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

    def find_empty_neighbour(self, loc):
        for l in self.neighbours(loc):
            if self[l] is Blocks.blank:
                return l
            else:
                return find_empty_neighbour(l)

    def display(self, txt):
        if not txt: return
        w = max(len(l) for l in txt) + 1
        X,Y = 5, 2
        for y, ln in enumerate(txt):
            blt.clear_area(X, Y+y+1, w+3, 1)
            puts(X, Y+y+1, ' ' + ln)
        refresh()
        blt.read()

    def get_ids_types(self, loc, attr='id'):
        if isinstance(loc, Loc):
            loc = [loc]
        lst = []
        for l in loc:
            lst.extend(self.get_all(l))
        lst = [getattr(x, attr, None) or x for x in lst]
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
        src = getattr(src, 'loc', src)
        tgt = getattr(tgt, 'loc', tgt)
        self.gen_graph(tgt)
        frontier = []
        heapq.heappush(frontier, (0, id(src), src))
        came_from = {}
        cost_so_far = {}
        came_from[src] = None
        cost_so_far[src] = 0

        while frontier:
           current = heapq.heappop(frontier)

           if current[2] == tgt:
              break
           for next in self.g[current[2]]:
              new_cost = cost_so_far[current[2]] + dist(current[2], next)
              if next not in cost_so_far or new_cost < cost_so_far[next]:
                 cost_so_far[next] = new_cost
                 priority = new_cost + dist(tgt, next)
                 heapq.heappush(frontier, (priority, id(next), next))
                 came_from[next] = current[2]
        l = [tgt]
        n = tgt
        while n!=src:
            n = came_from[n]
            l.append(n)
        return list(reversed(l))[1:]

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
        if not isinstance(type, SEQ_TYPES):
            type = (type,)
        def get_obj(x):
            return Objects.get(x) or x
        return any(
            get_obj(x).type in type for x in self.get_all_obj(loc)
        )

    def get_all(self, loc):
        return [n for n in self.B[loc.y][loc.x]
                if n!=Blocks.blank
               ]

    def remove(self, obj, loc=None):
        loc = loc or obj.loc
        cell = self.B[loc.y][loc.x]
        cell.remove(obj if obj in cell else (obj.id or obj.type))

    def get_all_obj(self, loc):
        return [Objects[n] or n for n in self.B[loc.y][loc.x]
                if not isinstance(n, str)
               ]

    def get_obj(self, loc):
        return last(self.get_all_obj(loc))

    def get_being(self, loc):
        return first(o for o in self.get_all_obj(loc) if isinstance(o, Being) and o.alive)

    def load_map(self, map_num, for_editor=0):
        _map = open(f'maps/{map_num}.map').readlines()
        self.containers = containers = []
        self.doors = doors = []
        self.specials = specials = defaultdict(list)
        self.buildings = []
        self.guards = []
        BL=Blocks
        roofs = []

        for y in range(HEIGHT):
            for x in range(WIDTH):
                char = _map[y][x*2 + (0 if y%2==0 else 1)]
                loc = Loc(x,y)
                if char != BL.blank:
                    if char==BL.rock:
                        BlockingItem(Blocks.rock, '', loc, self._map)

                    elif char==Blocks.rock3:
                        BlockingItem(Blocks.rock3, 'rock', loc, board_map=self._map)

                    elif char==Blocks.water:
                        Item(Blocks.water, 'water', loc, type=Type.water, board_map=self._map)

                    elif char==Blocks.roof:
                        Item(Blocks.roof, '', loc, self._map, type=Type.roof)
                        roofs.append(loc)

                    elif char==Blocks.cupboard:
                        c = Cupboard(self, loc)

                    elif char=='g':
                        if for_editor:
                            self.put(char, loc)
                        else:
                            g = Guard(loc, self._map)
                            self.guards.append(g)

                    elif char==Blocks.door:
                        d = Item(Blocks.door, 'door', loc, self._map, type=Type.door)
                        doors.append(d)

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

        hr = HandleRoof(self)
        for loc in roofs:
            hr.handle(loc)
        return containers, doors, specials


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

    def board_map(self):
        self.load_map('map')
        MapLocation('Arroyo', self.specials[1], 'map', loc_map='1', id=ID.arroyo_map_loc, hidden=False)
        MapLocation('Klamath', self.specials[2], 'map', loc_map='3', id=ID.klamath_map_loc, hidden=False)
        MapLocation('Den', self.specials[3], 'map', loc_map='den1', id=ID.den_map_loc)

    def board_1(self):
        self.load_map('1')
        Elder(self.specials[2], '1')
        Kyssa(self.specials[3], '1')
        self.put(Type.pistol223, self.specials[2].mod_r())
        # self.monsters.append(Ant(self.random_empty(), '1'))
        self.monsters.append(Ant(self.random_empty(), '1'))

    def board_2(self):
        # Arroyo 2
        self.load_map('2')

    def board_3(self):
        self.load_map('3')
        Aykin(self.specials[1], '3')

    def board_den1(self):
        self.load_map('den1')
        Arette(self.specials[1], 'den1')
        StJunien(self.specials[2], 'den1')
        self.doors[1].type = Type.blocking

    def board_den2(self):
        self.load_map('den2')
        Metzger(self.specials[1], 'den2')
        Vic(self.specials[2], 'den2')
        Leblanc(self.specials[3], 'den2')
        Lignac(self.specials[4], 'den2')
        self.doors[1].type = Type.blocking

    def screen_loc_to_map(self, loc):
        x,y=loc
        if y%2==1:
            x-=1
        x = int(round(x/2))
        return Loc(x,y)

    def draw(self, battle=False, editor=False, initial=False):
        blt.clear()
        blt.color("white")
        all_fill = set()    # inside buildings
        if not editor:
            for bld, fill, door in self.buildings:
                # check in `bld` here because door is part of `bld` and we want to reveal when standing in the doorway
                fill_loc = set(o.loc for o in fill)
                bld_loc = set(o.loc for o in bld)
                if Misc.player and Misc.player.loc not in fill_loc|bld_loc:
                    for obj in fill:
                        blt_put_obj(obj, do_refresh=0)
                        all_fill.add(tuple(obj.loc))
                        if initial:
                            refresh()

        for y, row in enumerate(self.B):
            for x, cell in enumerate(row):
                if (x,y) in all_fill:
                    continue
                # tricky bug: if an 'invisible' item put somewhere, then a being moves on top of it, it's drawn, but
                # when it's moved out, the invisible item is drawn, but being an empty string, it doesn't draw over the
                # being's char, so the 'image' of the being remains there, even after being moved away.
                cell = [c for c in cell if getattr(c,'char',None)!='']
                a = last(cell)
                x,y = loc_to_scr(x, y)
                if isinstance(a, (ID, Type)):
                    a = Objects[a]
                if self._map!='map' or not getattr(a, 'hidden', False):
                    puts(x,y,a)

        if not editor:
            for bld, fill, door in self.buildings:
                for obj in bld:
                    blt_put_obj(obj, do_refresh=0)

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

    def neighbours_obj(self, loc):
        return filter(None, [self.get_obj(l) for l in self.neighbours(loc)])

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

def loc_to_scr(x, y=None):
    if isinstance(x,Loc):
        x, y = x
    x*=2
    if y%2==1:
        x+=1
    return Loc(x,y)

class HandleRoof:
    def __init__(self, B):
        self.B = B
        self.seen = set()
        self.buildings = []

    def handle(self, loc):
        if loc in self.seen: return
        self.seen.add(loc)
        bld = self.find_connected_roof(loc)
        door = first(l for l in bld if self.B.get_obj(l).type==Type.door)
        inn = self.find_inner(bld)
        fill = self.fill_roof(inn, bld)
        bld = [l for l in bld if l!=door]

        def col():
            return rand_color((30,40),(30,40),(30,40))

        bld = [Item(Blocks.roof, '', l, self.B._map, type=Type.roof, color=col(), put=False) for l in bld]
        fill = [Item(Blocks.roof, '', l, self.B._map, type=Type.roof, color=col(), put=False) for l in fill]
        self.B.buildings.append((bld, fill, door))

    def find_connected_roof(self, loc, bld=None):
        bld = bld or set([loc])
        B = self.B
        for loc in B.neighbours(loc):
            if loc in self.seen:
                continue
            if B.found_type_at((Type.roof, Type.door), loc):
                bld.add(loc)
                self.seen.add(loc)
                self.find_connected_roof(loc, bld)
            self.seen.add(loc)
        return bld

    def find_inner(self, bld, seen=None):
        min_x, max_x = min(l.x for l in bld), max(l.x for l in bld)
        min_y, max_y = min(l.y for l in bld), max(l.y for l in bld)
        for l in bld:
            nbr = self.B.neighbours(l)
            for n in nbr:
                if n not in bld and (min_x<n.x<max_x and min_y<n.y<max_y):
                    break
            return n

    def fill_roof(self, loc, bld, fill=None, seen=None):
        B = self.B
        seen = seen or set([loc])
        fill = fill or set([loc])
        for nloc in B.neighbours(loc):
            if nloc in seen:
                continue
            if not B.found_type_at((Type.roof, Type.door), nloc):
                fill.add(nloc)
                seen.add(nloc)
                self.fill_roof(nloc, bld, fill, seen)
            seen.add(nloc)
        return fill


class Boards:
    @staticmethod
    def get_by_map(map):
        return getattr(Boards, 'b_'+map)

    @staticmethod
    def get_by_loc(loc):
        return board_grid[loc.y][loc.x]


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
                ok = handle_ui(u)
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
                    # path = u.path.get(tgt) or B.find_path(u.loc, tgt.loc)
                    path = B.find_path(u.loc, tgt.loc)
                    if len(path)==0:
                        u.hit(tgt)
                    elif path:
                        u.move(loc=first(path))
                        u.path[tgt] = path
                    else:
                        return

                    B.draw(battle=1)
                    if u.cur_move==0:
                        u.cur_move = u.speed
                        u.color=None
                        blt_put_obj(u)
                        break

class BeingItemBase:
    is_player = 0
    player = None
    state = 0
    color = None
    _str = None
    id = None
    type = None

    def __init__(self, char=None, name=None, loc=None, board_map=None, put=True, id=None, type=None, color=None, n=0):
        self._name, self.loc, self.board_map, self.color, self.n = \
                name, loc, board_map, color, n
        if char:
            self.char = char
        if type:
            self.type = type
        if id:
            self.id = id
        if self.id:
            Objects[self.id] = self
        elif self.type:
            Objects[self.type] = self
        if board_map and put:
            self.B.put(self)

    def __str__(self):
        return self.char

    @property
    def name(self):
        return self._name or self.__class__.__name__

    def tele(self, loc):
        self.B.remove(self)
        self.put(loc)

    def put(self, loc):
        self.loc = loc
        B=self.B
        B.put(self)

    def has(self, id):
        return self.inv.get(id)

    def remove1(self, id, n=1):
        self.inv[id] -= n
        if self.inv[id]<=0:
            del self.inv[id]

    def add1(self, id, n=1):
        self.inv[id] += n

    def move_to_board(self, _map, specials_ind=None, loc=None):
        Misc.combat = False
        to_B = getattr(Boards, 'b_'+_map)
        if specials_ind is not None:
            loc = to_B.specials[specials_ind]
        self.B.remove(self)
        self.loc = loc
        to_B.put(self)
        self.board_map = to_B._map
        if to_B._map != 'map':
            for id in (self.live_party() or []):
                Objects[id].move_to_board(_map, loc=to_B.find_empty_neighbour(loc))
        return to_B

    @property
    def B(self):
        if self.board_map:
            return getattr(Boards, 'b_'+self.board_map)


class Item(BeingItemBase):
    board_map = None
    weight = 1
    value_pound = 1
    _cost = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inv = defaultdict(int)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f'<I: {self.char}>'

    def cost(self, markup=0):
        c = self._cost or self.weight * self.value_pound
        return c + c*markup

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

map_name_to_map_location = {}
loc_to_map_location = {}

class MapLocation(BeingItemBase):
    char = Blocks.location
    hidden = True

    def __init__(self, *args, hidden=True, loc_map=None, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.loc_map = loc_map
        self.hidden = hidden
        map_name_to_map_location[loc_map] = self.id
        loc_to_map_location[self.loc] = self.id


class BlockingItem(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Type.blocking

class PartyMixin:
    party = None

    def total_strength(self):
        return sum(u.hp for u in self.live_party())

    def live_party(self):
        return list(u for u in filter(None, self.party or []) if Objects[u].alive)

    def party_move(self, player, monsters):
        B = self.B
        m = self.closest(monsters)
        if m and (Misc.combat or dist(self, m) <= 6):
            if m.loc in self.neighbours():
                self.attack(m)
            else:
                self.move(loc=self.B.next_move_to(self, m))

        elif dist(self, player) > 6:
            if random() > 0.05:
                self.move(loc=self.B.next_move_to(self, player))
        else:
            self.cur_move = 0

def handle_load_board(unit, rv):
        loc = rv.b_new
        if chk_b_oob(loc) and board_grid[loc.y][loc.x]:
            return unit.move_to_board(Boards.get_by_loc(loc), loc=rv.new)

class Armor:
    pass

class Being(BeingItemBase):
    hp = 1
    max_hp = 1
    is_being = 1
    is_player = False
    speed = 1
    type = None
    char = None
    path = None
    caps = 0
    alive = True
    equipped = None
    armor = None
    base_hit_ap = 2

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
        self.loc, self.board_map, self._name, self.state, self.color  = loc, board_map, name, state, color
        self.char = self.char or char
        self.inv = defaultdict(int)
        self.cur_move = self.speed
        if id:
            self.id = id
        if self.id:
            Objects[self.id] = self
        if board_map and put:
            self.B.put(self)
        self.max_hp = self.hp
        self.path = {}
        self.skills = defaultdict(int)
        self.traits = []
        self.equipped = [None, None]

    def __str__(self):
        return super().__str__() if self.hp>0 else Blocks.rubbish

    @property
    def name(self):
        return ('dead ' if self.dead else '') + (self._name or self.__class__.__name__)

    def ai_move(self, player):
        objs = [Objects[id] for id in player.live_party()]
        tgt = self.closest(objs + [player])

        if tgt and (Misc.combat or (dist(self, tgt) <= 6)):
            Misc.combat = True
            self.color = 'lighter blue'
            if tgt.loc in self.neighbours():
                self.attack(tgt)
            else:
                self.move(loc=self.B.next_move_to(self, tgt))
            self.B.draw(battle=1)
            # self.color=None
        else:
            self.cur_move = 0

    def talk(self, being, id_or_type=None, yesno=False, resp=False, rand=False):
        """Messages, dialogs, yes/no, prompt for response, multiple choice replies."""
        if isinstance(being, int):
            being = Objects.get(being)
        if not yesno:
            talk = Talk(self.B, being, id_or_type, rand)
            rv = talk.talk()
            if resp:
                return prompt()
            return rv, talk.last_conv


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
                    self.attack(being, melee=True)
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
            if self.is_player:
                self.handle_player_move(new)
            return True, True
        return None, None

    def handle_directional_turn(self, dir, loc):
        """Turn char based on which way it's facing."""
        if self.char == Blocks.party:
            return
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
        pick_up = []
        items = B.get_all_obj(new)
        top_obj = last(items)
        if top_obj:
            if isinstance(top_obj, int):
                top_obj = Objects[top_obj.id]

        for x in reversed(items):
            if x.id in pick_up or x.type in pick_up or isinstance(x, Weapon):
                if self.is_player:
                    self.inv[x.id or x.type] += 1
                B.remove(x, new)

        names = [o.name for o in B.get_all_obj(new) if o.name and o!=self]
        plural = len(names)>1
        names = ', '.join(names)
        if names:
            a = ':' if plural else ' a'
            status(f'You see{a} {names}')

    def ai_attack(self, obj):
        for id_or_type in self.inv:
            it = Objects[id_or_type]
            eqp = self.equipped[0]
            if isinstance(it, Weapon) and not eqp or eqp.value_pound < it.value_pound:
                self.equipped[0] = it
                status(f'{self} equipped {it}')
        self.attack(obj)

    def attack(self, obj, melee=False):
        eqp = self.equipped[0]
        wpn = None
        if eqp:
            wpn = Objects[eqp]
            req_ap = wpn.hit_aimed_burst_pts[0]
        if wpn and req_ap > self.cur_move:
            wpn = None
        if melee and wpn and isinstance(wpn, RangedWeapon):
            # force melee
            wpn = None
        if not wpn:
            req_ap = self.base_hit_ap

        if req_ap > self.cur_move:
            self.cur_move = 0
            return

        dmg = self.strength // 2
        if wpn:
            dmg = randrange(*wpn.dmg)

        if isinstance(wpn, RangedWeapon):
            self.hit(obj, dmg, ranged=True)
        elif obj.loc in self.B.neighbours(self.loc):
            self.hit(obj, dmg)
        self.cur_move -= req_ap

    def get_dir(self, b):
        a = self.loc
        b = getattr(b, 'loc', None) or b
        if a.x<=b.x and a.y<b.y: return 'n'
        elif a.x<=b.x and a.y>b.y: return 'u'
        elif a.x>=b.x and a.y<b.y: return 'b'
        elif a.x>=b.x and a.y>b.y: return 'y'
        elif a.x<b.x: return 'l'
        elif a.x>b.x: return 'h'

    def hit(self, obj, dmg=None, ranged=False, mod=1, type=None, descr=''):
        if dmg:
            a = dmg
        else:
            str = self.strength
            a = int(round((str * mod)/3))
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

    def defend(self, dmg, type):
        x = 0
        return dmg - x

    def action(self):
        def is_near(id):
            return getattr(ID, id) in self.B.get_ids_types(self.B.neighbours(self.loc) + [self.loc], 'id')

        def is_near_type(type):
            print( self.B.get_ids_types(self.B.neighbours(self.loc) + [self.loc], 'type') )
            return getattr(Type, type) in self.B.get_ids_types(self.B.neighbours(self.loc) + [self.loc], 'type')

        if is_near('elder'):
            self.talk(Objects.elder)
            self.caps += 150
            Item('f', 'Vault 13 Flask', type=Type.vault13_flask)
            self.inv[Type.vault13_flask] += 1

        elif is_near('chim'):
            ShopUI(self.B, self, Objects.chim).shop_ui()

        elif is_near_type('guard'):
            g = first(o for o in self.B.neighbours_obj(self.loc) if o.type==Type.guard)
            self.talk(g, Type.guard, rand=True)

        elif is_near('st_junien'):
            ShopUI(self.B, self, Objects.st_junien).shop_ui()

        elif is_near('lignac'):
            self.talk(Objects.lignac)

        elif is_near('metzger') and self.charisma>=5:
            self.talk(Objects.metzger)
            Objects.leblanc.state=1

        elif is_near('leblanc') and Objects.leblanc.state==1:
            self.talk(Objects.leblanc)
            self.B.doors[1].type = Type.door

        elif is_near('aykin'):
            self.talk(Objects.aykin)
            Objects.den_map_loc.hidden = False

        elif is_near('arette') and Objects.arette.state==0:
            _, tid = self.talk(Objects.arette)
            if tid >= 12:
                Objects.arette.state = 1

        elif is_near('arette') and Objects.arette.state==1:
            self.talk(Objects.arette, ID.arette2)

        elif is_near('kyssa'):
            ch = self.talk(Objects.kyssa)
            if ch==1:
                self.perception += 1
                self.add_xp(50)
                status('You gain 1 perception')

    def use(self, equip=False):
        ascii_letters = string.ascii_letters
        items = [(id,q) for id,q in self.inv.items() if q>0]

        lst = []
        for n, (id,qty) in enumerate(items):
            item = Objects[id]
            lst.append(f' {ascii_letters[n]}) {item.name:4} - {qty} ')
        W = max(len(l) for l in lst)
        blt.clear_area(2, 2, W, len(lst))
        for n, ln in enumerate(lst):
            puts(2, n+2, ln)

        refresh()
        ch = get_and_parse_key()
        item_id = None
        if ch in ascii_letters:
            try:
                item_id = items[string.ascii_letters.index(ch)][0]
            except IndexError:
                return
        if not item_id: return

        obj = Objects[item_id]
        if hasattr(obj, 'heal'):
            heal = obj.heal if isinstance(obj.heal, int) else randrange(obj.heal)
            self.hp = min(self.hp+heal, self.max_hp)
            self.remove1(item_id)
            status('You feel better')

        eq = self.equipped
        if equip:
            if isinstance(obj, Weapon):
                if eq[0]:
                    self.inv[eq[0]] += 1
                eq[0] = item_id
                self.remove1(item_id)
                status(f'You start using {obj}')
            elif isinstance(obj, Armor):
                if self.armor:
                    self.inv[self.armor] += 1
                self.armor = item_id
                self.remove1(item_id)
                status(f'You start wearing {obj}')
            else:
                status('Cannot equip this item' )

    def closest(self, objs):
        return first( sorted(objs, key=lambda x: dist(self.loc, x.loc)) )

    def neighbours(self):
        return self.B.neighbours(self.loc)

    def neighbours_obj(self):
        return filter(None, [self.B.get_obj(l) for l in self.B.neighbours(self.loc)])

    @property
    def alive(self):
        return self.hp>0

    @property
    def dead(self):
        return not self.alive


class Cupboard(Item):
    def __init__(self, B, loc):
        super().__init__(Blocks.cupboard, 'cupboard', loc, type=Type.container, board_map=B._map)
        # ugly: this doesn't work in the map editor because `objects` dict doesn't have these items
        try:
            if random()>.5:
                self.add1(Type.caps, randrange(1,3))
            elif random()>.7:
                self.add1(Type.healing_powder)
        except: pass

class Weapon(Item):
    dmg = None
    min_st = None
    _name = None
    magazine_size = None    # used for some charged melee wpns
    ammo_type = None
    weight = None
    value_pound = None
    hit_aimed_burst_pts = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Objects[self.type] = self


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

class Spear(Weapon):
    dmg = 3,10
    min_st = 4
    hit_aimed_burst_pts = (4,None,None)
    weight = 4
    value_pound = 20
    char = Blocks.spear
    type = Type.spear

class RangedWeapon(Weapon):
    range = None
    loaded = 0

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
        if self.loaded<=0:
            status('Out of ammo!')
            return
        if being.cur_move < self.hit_aimed_burst_pts[0]:
            status('Not enough Action Points!')
            return

        B.draw()
        loc = self.select_target(B)
        if loc:
            tgt = B.get_being(loc)
            if tgt:
                self.apply(being, tgt)
                self.loaded -= 1
                being.cur_move -= self.hit_aimed_burst_pts[0]

    def apply(self, being, tgt):
        loc = tgt.loc
        dmg = randrange(*self.dmg)
        being.hit(tgt, dmg=dmg, type=Type.ranged_attack, descr=self.name)
        # Use some hit animation...
        blt_put_obj(Blocks.hit1, loc)
        sleep(0.1)
        blt_put_obj(Blocks.hit2, loc)
        sleep(0.1)
        blt_put_obj(tgt, loc)
        sleep(0.1)
        blt_put_obj(Blocks.hit2, loc)
        sleep(0.1)
        blt_put_obj(tgt, loc)

    def reload(self, player):
        ammo = player.inv.get(self.ammo.type)
        if ammo:
            need = self.magazine_size - self.loaded
            qty = min(need, ammo)
            self.loaded += qty
            player.remove1(self.ammo.type, qty)
            status(f'Reloaded {self}')


class Ammo(Item):
    pass

class Knife(Item):
    char = Blocks.knife
    type = Type.knife

class HealingPowder(Item):
    char = Blocks.bottle
    heal = 5
    type = Type.healing_powder

class Stimpack(Item):
    char = Blocks.stimpack
    heal = 5, 20
    type = Type.stimpack
    _cost = 175

class FMJ223(Ammo):
    _name = '.223 FMJ (50)'
    value = 200
    type = Type.fmj223
    char = Blocks.ammo
    magazine_size = 50
    weight = 2

class MM10(Ammo):
    _name = '10mm'
    value = 4
    type = Type.mm10
    char = Blocks.ammo

class Magnum44FMJ(Ammo):
    _name = '.44 Magnum FMJ'
    value = 50
    type = Type.magnum44fmj
    char = Blocks.ammo
    magazine_size = 20

class Pistol223(RangedWeapon):
    # dmg = 20,30
    dmg = 1,2
    min_st = 5
    range = 30
    hit_aimed_burst_pts = (5,6,None)
    magazine_size = 5
    weight = 5
    value_pound = 700
    char = Blocks.pistol
    type = Type.pistol223
    ammo = FMJ223

class PipeRifle(RangedWeapon):
    # dmg = 20,30
    dmg = 5,12
    min_st = 5
    range = 20
    hit_aimed_burst_pts = (5,6,None)
    magazine_size = 1
    weight = 10
    value_pound = 20
    char = Blocks.rifle
    type = Type.pipe_rifle
    ammo = MM10

class HuntingRifle(RangedWeapon):
    # dmg = 20,30
    dmg = 8,20
    min_st = 5
    range = 40
    hit_aimed_burst_pts = (5,6,None)
    magazine_size = 10
    weight = 9
    value_pound = 111
    char = Blocks.rifle
    type = Type.hunting_rifle
    ammo = FMJ223

class XPLevelMixin:
    xp = 0
    level = 1
    level_tiers = enumerate(())

class Ant(Being):
    speed = 6
    char = Blocks.ant
    hp = 1
    strength = 1

class Player(PartyMixin, XPLevelMixin, Being):
    speed = 5
    type = Type.player
    is_player = True
    level_tiers = enumerate((500,2000,5000,10000,15000,25000,50000,100000,150000))
    char = Blocks.player_l
    hp = 40

    def __init__(self, *args, player=None, party=None, spells=None, **kwargs ):
        super().__init__(*args, **kwargs)
        self.party = [ID.banize]
        self.player = self
        self.inv[Type.pipe_rifle] = 1
        self.inv[Type.spear] = 1
        self.inv[Type.stimpack] = 2
        self.inv[Type.mm10] = 20

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f'<P: {self.name}>'

    def add_xp(self, xp):
        self.xp+=xp
        for lev, xp in self.level_tiers:
            if xp > self.xp:
                break
            self.level = lev

    def fire(self):
        eqp = self.equipped[0]
        if eqp:
            Objects[eqp].fire(self.B, self)

class NPC(PartyMixin, XPLevelMixin, Being):
    pass

class Guard(NPC):
    type = Type.guard
    char = Blocks.npc2

class Elder(NPC):
    id = ID.elder
    char = Blocks.woman

class Kyssa(NPC):
    id = ID.kyssa
    char = Blocks.npc2

class Aykin(NPC):
    id = ID.aykin
    char = Blocks.npc2

class Arette(NPC):
    id = ID.arette
    char = Blocks.npc2

#--
class Metzger(NPC):
    id = ID.metzger
    char = Blocks.npc3

class Lignac(NPC):
    # Metzger's capo
    id = ID.lignac
    char = Blocks.npc2

class Leblanc(NPC):
    # Metzger's guard
    id = ID.leblanc
    char = Blocks.npc2

#--

class Vic(NPC):
    id = ID.vic
    char = Blocks.npc2

class StJunien(NPC):
    id = ID.st_junien
    char = Blocks.npc2
    caps = 58
    inv = {
        Type.stimpack: 2,
        Type.hunting_rifle: 1,
        Type.mm10: 5,
        Type.fmj223: 3,
      }

class Banize(NPC):
    speed = 4
    id = ID.banize
    char = Blocks.banize
    hp = 15

class Chim(NPC):
    speed = 4
    id = ID.chim
    char = Blocks.banize
    markup = 0.1
    caps = 300

class IndependentParty(Player):
    pass

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

def board_setup():

    Boards.b_1 = Board(Loc(0,2), '1')
    Boards.b_1.board_1()
    Boards.b_2 = Board(Loc(1,2), '2')
    Boards.b_2.board_2()

    Boards.b_3 = Board(Loc(0,4), '3')
    Boards.b_3.board_3()

    Boards.b_den1 = Board(Loc(0,6), 'den1')
    Boards.b_den1.board_den1()

    Boards.b_den2 = Board(Loc(1,6), 'den2')
    Boards.b_den2.board_den2()

    Boards.b_map = Board(Loc(0,0), 'map')
    Boards.b_map.board_map()

    board_grid[:] = [
        ['map', None, None],
        [None, None, None],
        ['1', '2', None],
        [None, None, None],
        ['3', None, None],
        [None, None, None],
        ['den1', 'den2', None],
    ]
    # Misc.B = Boards.b_1
    Misc.B = Boards.b_den2

def init_items():
    Pistol223()
    PipeRifle()
    HuntingRifle()
    FMJ223()
    MM10()
    HealingPowder()
    Stimpack()
    Spear()

def main(load_game):
    blt.open()
    blt.set(f"window: resizeable=true, size=80x25, cellsize=auto, title='Atom Punk'; font: FreeMono.ttf, size={SIZE}")
    blt.set("input.filter={keyboard, mouse+}")
    blt.set("input.mouse-cursor=false")
    blt.color("white")
    blt.composition(True)
    blt.clear()
    if not os.path.exists('saves'):
        os.mkdir('saves')
    Misc.is_game = 1
    init_items()

    ok=1
    board_setup()
    # player = Misc.player = Player(Boards.b_1.specials[1], board_map='1', id=ID.player)
    player = Misc.player = Player(Boards.b_den1.specials[1].mod_l(2), board_map='den2', id=ID.player)
    Banize(Boards.b_1.specials[1].mod_r(10), board_map='1')
    Chim(Boards.b_1.specials[1].mod_r(5), board_map='1')
    Misc.B.draw(initial=1)

    def live_monsters():
        return [m for m in Misc.B.monsters if m.alive]

    while ok:
        while 1:
            ok = handle_ui(player)
            if ok=='q': return
            if not Misc.combat or player.cur_move<=0 or player.dead:
                player.cur_move = player.speed
                break

        for u in player.live_party():
            u = Objects[u]
            while 1:
                u.party_move(player, live_monsters())
                if Misc.combat:
                    sleep(0.15)
                refresh()
                if not Misc.combat or u.cur_move<=0 or u.dead:
                    u.cur_move = u.speed
                    break

        for m in live_monsters():
            while 1:
                m.ai_move(player)
                if Misc.combat:
                    sleep(0.15)
                refresh()
                if not Misc.combat or m.cur_move<=0 or m.dead:
                    m.cur_move = m.speed
                    break

        if not live_monsters():
            Misc.combat = False

        if player.dead:
            player.talk(player)
            sys.exit()
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
            B = Misc.B = handle_load_board(unit, rv)
            B.draw()
        stats()

    elif k == '.':
        pass
    elif k == 'f':
        unit.fire()

    elif k == 'm':
        if B._map=='map':
            maploc_id = loc_to_map_location.get(unit.loc)
            if maploc_id:
                maploc = Objects[maploc_id]
                Misc.B = B = unit.move_to_board(maploc.loc_map, loc=Loc(0,0))
                unit.char = Blocks.player_f
        elif unit.is_player and not battle:
            map_loc = map_name_to_map_location[unit.B._map]
            loc = Objects[map_loc].loc
            Misc.B = B = unit.move_to_board('map', loc=loc)
            unit.char = Blocks.party

    elif k == 'o':
        name = prompt()
        Misc.player, B = Saves().load(name)
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
        if Misc.combat:
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

    elif k == 'U':
        Misc.player.use()

    elif k == 'E':
        B.display(str(B.get_all(unit.loc)))

    elif k == 'r':
        pl = Misc.player
        eqp = pl.equipped[0]
        if eqp:
            Objects[eqp].reload(pl)
            pl.cur_move -= 1

    elif k == 'e':
        Misc.player.use(equip=True)

    elif k == 'i':
        txt = []
        for id, n in Misc.player.inv.items():
            item = Objects[id]
            if item and n:
                txt.append(f'{item.name} {n}')
        B.display(txt)

    B.draw(battle = (not unit.is_player))
    return 1

class ShopUI:
    def __init__(self, B, player, trader):
        self.B = B
        self.trader = trader
        self.player = player

    def shop_ui(self):
        ch = make_choice(self.B, 'B)uy S)ell', 'bs')
        if ch == 'b':
            self._shop_ui(False)
        elif ch == 's':
            self._shop_ui()


    def _shop_ui(self, sell=True):
        i = 0
        self.B.draw()
        transaction = defaultdict(int)
        seller_caps = 0
        buyer_caps = self.trader.caps if sell else self.player.caps
        markup = -self.trader.markup if sell else self.trader.markup
        inv = self.player.inv if sell else self.trader.inv
        tgt_inv = self.trader.inv if sell else self.player.inv
        if not any(inv.values()):
            status('Nothing to '+('sell' if sell else 'buy'))
            return

        while 1:
            stats(self)
            blt.clear_area(5,5,60,10)

            puts(5, 8 + i, Blocks.circle3)

            x = y = 8
            items = [(type, q, Objects[type]) for type,q in inv.items()]
            ln = len(items)
            for n, (_,qty,obj) in enumerate(items):
                puts(7, y+n, f'{obj.name:30} {qty:-2} {obj.cost(markup):-2}caps')
            puts(7, y+n+1, 'SELL' if sell else 'BUY')

            refresh()
            k = get_and_parse_key()
            if k in ('q', 'ESCAPE'):
                # rollback transaction
                for id, qty in transaction.items():
                    inv[id] += qty
                return
            elif k == 'ENTER':
                if sell:
                    self.trader.caps = buyer_caps
                    self.player.caps += seller_caps
                else:
                    self.player.caps = buyer_caps
                    self.trader.caps += seller_caps
                for id, qty in transaction.items():
                    tgt_inv[id] += qty
                return
            elif k == 'UP':
                i-=1
                if i<0: i = ln
            elif k == 'DOWN':
                i+=1
                if i>ln: i = 0

            # BUYBACK
            elif k == 'LEFT' and i<ln:
                id, qty, obj = items[i]
                if transaction[id]<=0:
                    continue
                if blt.state(blt.TK_SHIFT):
                    n = transaction[id]
                else:
                    n = 1
                inv[id] += n
                transaction[id] -= n
                total = n * obj.cost(markup)
                buyer_caps += total
                seller_caps -= total

            # SELL
            elif k == 'RIGHT' and i<ln and items[i][1]>0:
                id, qty, obj = items[i]
                if obj.cost() > buyer_caps:
                    continue

                if blt.state(blt.TK_SHIFT):
                    n = int(math.floor(buyer_caps / obj.cost(markup)))
                else:
                    n = 1
                inv[id] -= n
                transaction[id] += n
                total = n * obj.cost()
                buyer_caps -= total
                seller_caps += total


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
    B.load_map(_map, for_editor=1)
    B.draw(editor=1)

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
                if chk_oob(loc.mod(mx,my)):
                    loc = loc.mod(mx,my)
                if brush:
                    if brush=='T':
                        B.B[loc.y][loc.x] = [choice((Blocks.tree1, Blocks.tree2))]
                    else:
                        B.B[loc.y][loc.x] = [brush]

        elif k == ' ':
            brush = None
        elif k == 'e':
            brush = Blocks.blank
        elif k == 'r':
            brush = Blocks.rock
        elif k == 'g':
            B.put(k, loc)
        elif k == 'R':
            brush = Blocks.roof
            B.put(Blocks.roof, loc)
        elif k == '+':
            B.put(k, loc)
        elif k and k in '0123456789':
            B.put(k, loc)
        elif k == 'w':
            Item(B, Blocks.water, 'water', loc)
        elif k == 'c':
            # Item(B, Blocks.cupboard, 'cupboard', loc)
            c = Cupboard(B, loc)
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

        B.draw(editor=1)
        x = loc.x*2 + (0 if loc.y%2==0 else 1)
        # blt.clear_area(x,loc.y,1,1)
        puts(x, loc.y, Blocks.circle4, color='blue')
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
