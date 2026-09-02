from itertools import combinations #so i dont have to make a function to make 21 different lists
from treys import Card, Evaluator
import random
import tkinter as tk
from PIL import Image, ImageTk
import os

#Classes
class Player:
    def __init__(self,name,money):
        
        self.name = name
        self.money = money
        self.bet = 0
        self.folded = False
        self.allin = False
        self.raw_cards = []
        self.all_cards = []
        self.show_cards = []

    def resetround(self):
        self.bet = 0
        self.folded = False
        self.allin = False
        self.raw_cards=[]
        self.smallblind = False
        self.bigblind = False
        self.all_cards=[]
        self.show_cards=[]

class Human(Player): # in case of future use
    pass

class Bot(Player):
    def botcalc(self,curboard,curhand):
        if(len(curboard)==0):
            return 2
        print(curboard)
        board = [Card.new(c) for c in curboard]
        hand = [Card.new(c) for c in curhand]
        
        rawscore = evaluator.evaluate(board,hand)
        
        #This returns a value between 1 and 7462 
        chances = (1-(rawscore/7462))*100
        print(f"{self.name} chances:",chances)
        k = random.randint(1,100)
        if(k<5):
            return 3 #random raise
        if(k<15):
            return 2 #random call
        if(chances<10):
            return 0 #Fold
        elif(chances<25):
            return 1 #check
        elif(chances<55):
            return 2 #call
        elif(chances<85):
            return 3 #raise
        else:
            return 4 #All in
    def botbet(self,curboard,highestbet,pot):
        oldhighest = highestbet
        act = self.botcalc(curboard,self.show_cards)
        print(f"{self.name} chose",act)
        callcount = highestbet-self.bet
        if(act <2 and callcount>0):
            act=0
        if(act == 0):
            message = (f"{self.name} Folds")
            self.folded=True
        elif(act == 1):
            message =(f"{self.name} Check")
        elif(act == 2):
            amount = min(callcount, self.money)
            self.money -=amount
            self.bet+=amount
            pot+=amount
            if amount==0:
                message = (f"{self.name} Checks")
            else:
                message = (f"{self.name} Calls")
        elif(act==3):
            raisecount = max(startingmoney//50,highestbet//5)
            amountbet = min(callcount+raisecount,self.money)
            self.money-=amountbet
            self.bet+=amountbet
            highestbet=self.bet
            message=(f"{self.name} raises by {raisecount} sheckles")
        elif(act ==4):
            amount=self.money
            self.money=0
            self.bet+=amount
            highestbet=max(highestbet,self.bet)
            self.allin = True
            message=(f"{self.name.upper()} ALL IN")
        israise = highestbet>oldhighest
        return(highestbet,pot,message,israise)
    



#Variables
Clubs = ["c2","c3","c4","c5","c6","c7","c8","c9","c:","c;","c<","c=","c>"]
hearts = ["h2","h3","h4","h5","h6","h7","h8","h9","h:","h;","h<","h=","h>"]
Spades = ["s2","s3","s4","s5","s6","s7","s8","s9","s:","s;","s<","s=","s>"]
Diamonds = ["d2","d3","d4","d5","d6","d7","d8","d9","d:","d;","d<","d=","d>"]
possiblehands = ["High Card","pair","Two Pair","Trips","Straight","Flush","Full House","Quads","Straight Flush","Royal Flush"]
deck = Clubs + hearts + Spades + Diamonds

smallblindindex =0
smallblindseat = 0
bigblindseat = 1
seatorder = []
turnindex = 0
actedsinceraise = set()
human = None
bots = []
smallblindindex = 0

startingmoney = 1000
phase = "preflop"
highestbet = 0
pot = 0
evaluator = Evaluator()
mustbet = 50
highestbet = 2*mustbet
ui = False

root = tk.Tk()
canvas = tk.Canvas(root,width=1280,height=720,bg="#35654d")
canvas.pack()
cardrefs = []

pot_text = your_money_text = opp_money_text = message_text = botactiontext = your_bet_text = None
btn_frame = foldbutton = checkbutton = callbutton = raisebar = raisebutton = opponent_bet_text = None
startbutton = startslider = numbots_slider = None
boardcards = calccards = playercards_unused = None

#All hand types functions
def isroyalflush(L):
    suits = {card[0] for card in L}              # Using sets because i feel like thats pretty cool
    cards = {card[1] for card in L}
    if(len(suits) == 1):
        if cards == {";",">","=","<",":"}:
            return True
    return False
def isstraightflush(L):
    suits = {card[0] for card in L}
    if(len(suits)>1):
        return False
    cards = [card[1] for card in L]
    cards.sort()
    cur=cards[0]
    if(cards == ["2","3","4","5",">"]):
        return True
    for i in range(1,len(cards)):
        prev = cur
        cur = cards[i]
        if(ord(cur)-ord(prev)!=1):
            return False
        
    return True         
def isquads(L):
    cards = [card[1] for card in L]
    cards.sort()
    if(cards[0] == cards[3] or cards[1]==cards[4]):
        return True
    return False
def isfullhouse(L):
    cards = [card[1] for card in L]
    myset = set(cards)
    if(len(myset)==2):
        return True
    return False
def isflush(L):
    suits = [card[0] for card in L]
    suits.sort()
    if(suits[0] == suits[4]):
        return True
    return False
def isstraight(L):
    cards = [card[1] for card in L]
    cards.sort()
    cur=cards[0]
    if(cards == ["2","3","4","5",">"]):
        return True
    for i in range(1,len(cards)):
        prev = cur
        cur = cards[i]
        if(ord(cur)-ord(prev)!=1):
            return False
    return True
def istrip(L):
    cards = [card[1] for card in L]
    cards.sort()
    for i in range(3):
        if(cards[i]==cards[i+2]):
            return True
    return False
def istwopair(L):
    cards = [card[1] for card in L]
    myset = set(cards)
    if(len(myset)==3):
        return True
    return False
def ispair(L):
    cards = [card[1] for card in L]
    myset = set(cards)
    if(len(myset)==4):
        return True
    return False
    
#Function to compare hands for winning if no one folds

def checkhand(a):
    j = list(combinations(a,5))
    #check for royal flush
    if(any(isroyalflush(k) for k in j)):
        return(9,)
    
    #check for straight flush
    if(any(isstraightflush(k) for k in j)):
        allstraighttops = []
        for k in j:
            if isstraightflush(k):
                order = sorted([card[1] for card in k])
                if order == ["2","3","4","5",">"]:
                    top = "5" 
                else:
                    top = order[-1]
                allstraighttops.append(top)
        allstraighttops.sort()

        return(8,allstraighttops[-1])
    
    #check for quads
    if(any(isquads(k) for k in j)):
        bestquad = ("0","0")
        for k in j:
            if(isquads(k)):
                cards = sorted([card[1] for card in k])
                if(cards[0]==cards[3]):
                    quad = cards[0]
                    kicker = cards[4]
                else:
                    quad = cards[1]
                    kicker = cards[0]
                bestquad = max((quad,kicker),bestquad)
        return(7,)+bestquad
                
        
    #check for fullhouse
    if any(isfullhouse(k) for k in j):
        best_fh = ("0", "0")
        for k in j:
            if isfullhouse(k):
                cards = sorted(card[1] for card in k)
                if cards[2] == cards[4]:
                    trip, pair = cards[2], cards[0]
                else:
                    trip, pair = cards[0], cards[3]
                best_fh = max(best_fh, (trip, pair))
        return (6,) + best_fh

        

    #checkflush
    if(any(isflush(k) for k in j)):
        curmax = ['0','0','0','0','0']
        for k in j:
            if(isflush(k)):
                cards = [card[1] for card in k]
                cards.sort(reverse=True)
                if(cards>curmax):
                    curmax = cards
        maxs = tuple(curmax)

        return (5,) + maxs
    
    #checkstraight
    if(any(isstraight(k) for k in j)):
        allstraighttops = []
        for k in j:
            if isstraight(k):
                    order = sorted([card[1] for card in k])
                    if order == ["2","3","4","5",">"]:
                        top = "5" 
                    else:
                        top = order[-1]
                    allstraighttops.append(top)
        allstraighttops.sort()
        return(4,allstraighttops[-1])
    
    #check three of a kind
    if(any(istrip(k) for k in j)):
        kickers = []
        highest = "0"
        for k in j:
            if(istrip(k)):
                cards = sorted(card[1] for card in k)
                if(cards[2]>highest):
                    highest = cards[2]
                    kickers = [x for x in cards if x!=highest]
        kickers.sort(reverse = True)
        return(3,)+(highest,)+tuple(kickers)
    
    #check for two pair
    if(any(istwopair(k) for k in j)):
        highest = ("0","0","0")
        for k in j:
            if(istwopair(k)):
                cards = sorted(card[1] for card in k)
                if(cards.count(cards[0])==1):
                    highest = max(highest, (cards[4],cards[2],cards[0]))
                elif(cards.count(cards[2])==1):
                    highest = max(highest, ((cards[4],cards[0],cards[2])))
                else:
                    highest = max(highest, ((cards[2],cards[0],cards[4])))
        return(2,)+highest
    
    #check for pair
    if(any(ispair(k) for k in j)):
        highestpair = "0"
        largest = ["0","0","0"]
        for k in j:
            if(ispair(k)):
                cards = [card[1] for card in k]
                for i in cards:
                    if(cards.count(i)>1):
                        kickercards = [x for x in cards if x!=i]
                        kickercards.sort(reverse=True)
                        if(i>highestpair):
                            highestpair=i
                            largest = kickercards
                        elif(i==highestpair):
                            largest = max(largest,kickercards)

                        
        return(1,)+(highestpair,)+tuple(largest)
    

    highest = ["0","0","0","0","0"]
    for k in j:
        cards = [card[1] for card in k]
        cards.sort(reverse=True)
        highest = max(cards,highest)
    return(0,)+tuple(highest)

#ui work
def showformat(card):
    suit = card[0]
    value = card[1]
    tuffcardsmap = {":":"T",";":"J","<":"Q","=":"K",">":"A"}
    return(tuffcardsmap.get(value,value)+suit)

def botseat(i,n):
    if n<=1:
        return 520
    spacing = 900//n
    return 120+i*spacing

def contenders():
    return [p for p in seatorder if not p.folded]

def active_players():
    return [p for p in seatorder if not p.folded and p.money > 0]

def betting_round_over():
    act = active_players()
    if len(act) <= 1:
        return True
    return all(p in actedsinceraise and p.bet == highestbet for p in act)

def advance_turn():
    global turnindex
    n = len(seatorder)
    for _ in range(n):
        turnindex = (turnindex+1) % n
        p = seatorder[turnindex]
        if not p.folded and p.money > 0:
            return

def first_to_act_index(after_idx):
    idx = after_idx
    n = len(seatorder)
    for _ in range(n):
        idx = (idx+1) % n
        p = seatorder[idx]
        if not p.folded and p.money > 0:
            return idx
    return after_idx

def first_to_act_index_inclusive(start_idx):
    idx = start_idx
    n = len(seatorder)
    for _ in range(n):
        p = seatorder[idx]
        if not p.folded and p.money > 0:
            return idx
        idx = (idx+1) % n
    return start_idx

def record_check_or_call(player):
    actedsinceraise.add(player)

def record_raise(player):
    actedsinceraise.clear()
    actedsinceraise.add(player)

def check_win_by_fold():
    global pot
    c = contenders()
    if len(c) == 1:
        c[0].money += pot
        pot = 0
        updatelabels()
        disablebuttons()
        botmessage(f"{c[0].name} wins (everyone else folded)")
        root.after(2000, newround)
        return True
    return False

def run_bot_turns():
    global highestbet, pot
    messages = []
    while not betting_round_over():
        current = seatorder[turnindex]
        if current is human:
            break
        if current.folded or current.money <= 0:
            advance_turn()
            continue
        highestbet,pot,message,is_raise = current.botbet(calccards[:currentbettingstage()], highestbet, pot)
        messages.append(message)
        if is_raise:
            record_raise(current)
        else:
            record_check_or_call(current)
        if check_win_by_fold():
            return
        advance_turn()
    updatelabels()
    if messages:
        botmessage(" | ".join(messages))

def begin_betting_round(preflop=False):
    global turnindex, actedsinceraise
    actedsinceraise = set()
    if preflop:
        turnindex = first_to_act_index(bigblindseat)
    else:
        turnindex = first_to_act_index_inclusive(smallblindseat)
    run_bot_turns()
    if check_win_by_fold():
        return
    if betting_round_over():
        advance_to_next_street()
    else:
        refresh_buttons()

def advance_to_next_street():
    global phase, highestbet
    for p in seatorder:
        p.bet = 0
    highestbet = 0
    if phase == "preflop":
        phase = "flop"
        displaycards(boardcards[:3], 360)
        show_message("Flop")
        begin_betting_round()
    elif phase == "flop":
        phase = "turn"
        displaycards(boardcards[:4], 360)
        show_message("Turn")
        begin_betting_round()
    elif phase == "turn":
        phase = "river"
        displaycards(boardcards, 360)
        show_message("River")
        begin_betting_round()
    elif phase == "river":
        phase = "showdown"
        compare()

def compare():
    disablebuttons()
    n = len(bots)
    for i, bot in enumerate(bots):
        displaycards(bot.show_cards, 100, startx=botseat(i,n))

    contenders = [p for p in ([human]+bots) if not p.folded]
    besthand = None
    winners = []
    for p in contenders:
        h = checkhand(p.all_cards)
        if besthand is None or h > besthand:
            besthand = h
            winners = [p]
        elif h == besthand:
            winners.append(p)

    split = pot//len(winners)
    for w in winners:
        w.money += split

    hand = possiblehands[besthand[0]]
    if len(winners)==1:
        if winners[0] is human:
            show_message(f"You win with {hand}!")
        else:
            show_message(f"{winners[0].name} wins with {hand}")
    else:
        names = ", ".join(w.name for w in winners)
        show_message(f"Tie ({hand}): {names}")

    updatelabels()
    root.after(2000, newround)






#Opponent bet amounts  


#One round of betting, e.g flop vs river
def currentbettingstage():
    if(phase =="preflop"):
        return 0
    elif(phase =="flop"):
        return 3
    elif(phase =="turn"):
        return 4
    return 5




#Display and button definitions for UI

#Displaying Cards

def getcardimage(cardcode, width=80):
    if(cardcode=="back"):
        img = Image.open("cards/back.png").convert("RGB").resize((width,int(width*1.452)))
        return ImageTk.PhotoImage(img)
    tuffcardsmap = {":":"T",";":"J","<":"Q","=":"K",">":"A"}     #because files cant be named with those 
    suit = cardcode[0]
    value = cardcode[1]
    filename = tuffcardsmap.get(value,value)+suit # second value is just default if it doesn't find anything for the numbers
    path = f"cards/{filename}.png"
    img = Image.open(path).convert("RGB").resize((width,int(width*1.452)))
    print("size",img.size)
    return(ImageTk.PhotoImage(img))

def displaycards(cards, ylevel, hidden=False,startx=300):
    for i,card in enumerate(cards):
        x = startx + i*120
        if hidden:
            img = getcardimage("back")
        else:
            img = getcardimage(card)
        cardrefs.append(img)
        canvas.create_image(x,ylevel,image=img,tags="card")

#Setting up labels and messages
def refresh_buttons():    
    if seatorder[turnindex] is not human:
        disablebuttons()
        return
    # Can only check if there's no bet to face
    if(highestbet !=human.bet):
        disablebutton(checkbutton)
    else:
        enablebutton(checkbutton)
    
    # Can only call if there's a bet to face and you have money
    if(highestbet > human.bet and human.money > 0):
        enablebutton(callbutton)
    else:
        disablebutton(callbutton)
    
    # Can only raise if you have money beyond the call amount
    can_raise = human.money > (highestbet - human.bet)
    if(can_raise):
        enablebutton(raisebar)
        enablebutton(raisebutton)
    else:
        disablebutton(raisebar)
        disablebutton(raisebutton)
def updatelabels():
    canvas.itemconfig(pot_text,text=f"Pot: ${pot}")
    canvas.itemconfig(your_money_text,text=f"Your money: ${human.money}")
    canvas.itemconfig(your_bet_text,text=f"your bet: ${human.bet}")
    canvas.itemconfig(human.blind_text, text="BB" if human.bigblind else ("SB" if human.smallblind else ""))
    for bot in bots:
        status = " (folded)" if bot.folded else ""
        canvas.itemconfig(bot.money_text, text =f"{bot.name}: ${bot.money}{status}")
        canvas.itemconfig(bot.bet_text,text=f"bet: ${bot.bet}")
        canvas.itemconfig(bot.blind_text, text="BB" if bot.bigblind else ("SB" if bot.smallblind else ""))
    raisebar.config(to=max(0,human.money-highestbet+human.bet))

def show_message(msg):
    canvas.itemconfig(message_text,text=msg)

def botmessage(msg):
    canvas.itemconfig(botactiontext,text=msg)

#Buttons initializing and management
def enablebuttons(btn):
    btn.config(state="normal")
def disablebuttons():
    for btn in [foldbutton,checkbutton,callbutton,raisebar,raisebutton]:
        btn.config(state="disabled")
def disablebutton(btn):
    btn.config(state="disabled")
def enablebutton(btn):
    btn.config(state="normal")


#Specific button actions
def folding():
    if seatorder[turnindex] is not human or human.folded or phase == "showdown":
        return
    human.folded = True
    advance_turn()
    run_bot_turns()
    if check_win_by_fold():
        return
    if betting_round_over():
        advance_to_next_street()
    else:
        refresh_buttons()

def checking():
    if seatorder[turnindex] is not human or human.folded or phase == "showdown":
        return
    if highestbet != human.bet:
        return
    show_message("You Check")
    record_check_or_call(human)
    advance_turn()
    run_bot_turns()
    if check_win_by_fold():
        return
    if betting_round_over():
        advance_to_next_street()
    else:
        refresh_buttons()

def calling():
    global pot
    if seatorder[turnindex] is not human or human.folded or phase == "showdown":
        return
    amount = highestbet-human.bet
    human.money -= amount
    human.bet += amount
    pot += amount
    updatelabels()
    record_check_or_call(human)
    advance_turn()
    run_bot_turns()
    if check_win_by_fold():
        return
    if betting_round_over():
        advance_to_next_street()
    else:
        refresh_buttons()

def raising():
    global highestbet, pot
    if seatorder[turnindex] is not human or human.folded or phase == "showdown":
        return
    amount = raisebar.get()
    if amount == 0:
        show_message("Set a raise amount first")
        return
    call_amount = highestbet - human.bet
    total = amount + call_amount
    if total > human.money:
        show_message("Not enough money")
        return
    human.money -= total
    human.bet += total
    highestbet = human.bet
    pot += total
    updatelabels()
    record_raise(human)
    advance_turn()
    run_bot_turns()
    if check_win_by_fold():
        return
    if betting_round_over():
        advance_to_next_street()
    else:
        refresh_buttons()

#ended here
#preparing variable function
def startgame():
    global human, bots, startingmoney
    money = startslider.get()
    n = numbots_slider.get()
    startingmoney = money
    human = Human("You", money)
    bots = [Bot(f"Bot {i+1}", money) for i in range(n)]
    canvas.delete("startscreen")
    startbutton.destroy()
    startslider.destroy()
    numbots_slider.destroy()
    newround()


#When someone goes broke, game ends and restarts
def restartgame(msg):
    global startbutton, startslider,ui,numbots_slider
    ui=False
    show_message("")
    botmessage("")
    canvas.delete("card")
    #removing current elements
    canvas.delete("gameui")
    #adding the restart screen
    canvas.create_text(640, 280, text=msg, fill="white", font=("Arial", 48), tags="startscreen")
    canvas.create_text(640, 340, text="Choose starting amount:", fill="white", font=("Arial", 20), tags="startscreen")

    startslider = tk.Scale(root, from_=500, to=5000, orient="horizontal",
                           length=300, resolution=50, bg="#35654d", fg="white",
                           font=("Arial", 14))
    startslider.set(1000)
    canvas.create_window(640, 400, window=startslider, tags="startscreen")

    numbots_slider = tk.Scale(root, from_=1, to=5, orient="horizontal", 
                              length=200, bg="#35654d", fg="white", font =("Arial",14),
                              label="Number of Bots")
    numbots_slider.set(1)
    canvas.create_window(640,455,window=numbots_slider,tags="startscreen")

    startbutton = tk.Button(root, text="Play Again", width=15, font=("Arial", 16),
                            bg="#f39c12", fg="white", command=startgame)
    canvas.create_window(640, 515, window=startbutton, tags="startscreen")

    disablebuttons()

#essentially the main game loop
def newround():
    global phase, highestbet, pot, ui,smallblindindex
    global boardcards, calccards, deck, bots, bigblindseat, smallblindseat
    global pot_text, your_money_text, message_text, botactiontext, your_bet_text
    global btn_frame, foldbutton, checkbutton, callbutton, raisebar, raisebutton
    #extra precaution
    if human.money <= 0:
        restartgame("You Lost.")
        return
    bots = [b for b in bots if b.money>0]
    if not bots:
        restartgame("You Won!")
        return
    global seatorder
    seatorder=[human]+bots

    # UI creation without doing it too much
    if not ui:
        ui = True
        pot_text = canvas.create_text(640, 260, text="Pot: $0", fill="white", font=("Arial", 20),tags="gameui")
        your_money_text = canvas.create_text(640, 620, text="Your money: $1000", fill="white", font=("Arial", 16),tags="gameui")
        message_text = canvas.create_text(1040, 500, text="", fill="yellow", font=("Arial", 18),tags="gameui")
        botactiontext = canvas.create_text(1040, 567, text="", fill="yellow", font=("Arial", 18),tags="gameui")
        your_bet_text = canvas.create_text(1040,620,text="Your bet: $100", fill="white", font=("Arial", 16),tags="gameui")
        human.blind_text = canvas.create_text(1040,600,text="", fill="yellow", font=("Arial", 12),tags="gameui")
        n = len(bots)
        for i, bot in enumerate(bots):
            x = botseat(i,n)+60
            bot.money_text = canvas.create_text(x, 20, text=bot.name, fill="white", font=("Arial", 14),tags="gameui")
            bot.bet_text = canvas.create_text(x,175,text="bet: $0", fill="white", font=("Arial", 14),tags="gameui")
            bot.blind_text = canvas.create_text(x,35,text="", fill="yellow", font=("Arial", 12),tags="gameui")
        btn_frame = tk.Frame(root, bg="#35654d")
        canvas.create_window(640, 690, window=btn_frame,tags="gameui")

        foldbutton = tk.Button(btn_frame, text="Fold", width=10, bg="#c0392b", fg="white", command=folding)
        foldbutton.pack(side="left", padx=5)
        checkbutton = tk.Button(btn_frame, text="Check", width=10, bg="#2980b9", fg="white", command=checking)
        checkbutton.pack(side="left", padx=5)
        callbutton = tk.Button(btn_frame, text="Call", width=10, bg="#27ae60", fg="white", command=calling)
        callbutton.pack(side="left", padx=5)
        raisebar = tk.Scale(btn_frame, from_=0, to=human.money, orient="horizontal", length=200,
                            bg="#35654d", fg="white", label="Raise $", resolution=1, digits=1, takefocus=1)
        raisebar.pack(side="left", padx=5)
        raisebutton = tk.Button(btn_frame, text="Raise", width=10, bg="#f39c12", fg="white", command=raising)
        raisebutton.pack(side="left", padx=5)

    # initializing cards
    phase = "preflop"
    human.resetround()
    for bot in bots:
        bot.resetround()
    

    # Deal cards every round
    deck = Clubs + hearts + Spades + Diamonds
    boardcards = []
    for i in range(5):
        k = random.randint(0,len(deck)-1)
        boardcards.append(deck[k])
        deck.pop(k)
    human.raw_cards = []
    for i in range(2):
        k = random.randint(0,len(deck)-1)
        human.raw_cards.append(deck[k])
        deck.pop(k)
    for bot in bots:
        bot.raw_cards=[]
        for i in range(2):
            k = random.randint(0,len(deck)-1)
            bot.raw_cards.append(deck[k])
            deck.pop(k)
    human.all_cards=human.raw_cards+boardcards
    for bot in bots:
        bot.all_cards= bot.raw_cards+boardcards
    for bot in bots:
        bot.show_cards=[showformat(c) for c in bot.raw_cards]
    calccards = [showformat(c) for c in boardcards]

    smallblindindex = smallblindindex % len(seatorder)
    smallblindseat = smallblindindex
    bigblindseat = (smallblindseat+1) % len(seatorder)
    for p in seatorder:
        p.smallblind = False
        p.bigblind = False
    seatorder[smallblindseat].smallblind = True
    seatorder[smallblindseat].money -= mustbet
    seatorder[smallblindseat].bet += mustbet
    pot += mustbet
    seatorder[bigblindseat].bigblind = True
    seatorder[bigblindseat].money -= mustbet*2
    seatorder[bigblindseat].bet += mustbet*2
    pot += mustbet*2
    highestbet = mustbet*2
    smallblindindex = (smallblindindex+1) % len(seatorder)


    if(human.money<=0 or all(bot.money<=0 for bot in bots)):
        if all(bot.money<=0 for bot in bots):
            display = "you win"
        else:
            display = "you lose"
        restartgame(display)
        return
    canvas.delete("card")
    displaycards(human.raw_cards, 500)
    n = len(bots)
    for i,bot in enumerate(bots):
        displaycards(bot.raw_cards, 100, hidden=True,startx=botseat(i,n))
    updatelabels()
    show_message("preflop")
    begin_betting_round(preflop=True)



#Initialization of startscreen

canvas.create_text(640, 140, text="Poker Game", fill="white", font=("Arial", 48), tags="startscreen")
canvas.create_text(640, 340, text="Choose starting amount:", fill="white", font=("Arial", 20), tags="startscreen")

startslider = tk.Scale(root, from_=500, to=5000, orient="horizontal",length=300, resolution=50, bg="#35654d", fg="white",font=("Arial", 14))
startslider.set(1000)
canvas.create_window(640, 400, window=startslider, tags="startscreen")

numbots_slider = tk.Scale(root,from_=1,to=5,orient="horizontal",length=200,bg="#35654d",fg = "white",font=("Arial",14),label="Number of Bots")
numbots_slider.set(1)
canvas.create_window(640,255,window=numbots_slider,tags="startscreen")

startbutton = tk.Button(root, text="Start Game", width=15, font=("Arial", 16),bg="#f39c12", fg="white", command=startgame)
canvas.create_window(640, 470, window=startbutton, tags="startscreen")

root.mainloop()

