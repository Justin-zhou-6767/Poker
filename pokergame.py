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
        self.all_cards=[]
        self.show_cards=[]

class Human(Player): # in case of future use
    pass

class Bot(Player):
    def botcalc(curboard,curhand):
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
    def botbet(curboard,curhand):
        act = self.botcalc(curboard,self.show_cards)
        print(f"{self.name} chose",act)
        callcount = highestbet-self.bet
        if(act <2 and callcount>0):
            act=0
        if(act == 0):
            message = (f"{self.name} Folds")
            oppFolded=True
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
            highestbet=max(highestbet,opponentbet)
            self.allin = True
            message=(f"{self.name.upper()} ALL IN")
    
    



#Variables
Clubs = ["c2","c3","c4","c5","c6","c7","c8","c9","c:","c;","c<","c=","c>"]
hearts = ["h2","h3","h4","h5","h6","h7","h8","h9","h:","h;","h<","h=","h>"]
Spades = ["s2","s3","s4","s5","s6","s7","s8","s9","s:","s;","s<","s=","s>"]
Diamonds = ["d2","d3","d4","d5","d6","d7","d8","d9","d:","d;","d<","d=","d>"]
possiblehands = ["High Card","pair","Two Pair","Trips","Straight","Flush","Full House","Quads","Straight Flush","Royal Flush"]
deck = Clubs + hearts + Spades + Diamonds


human = None
bots = []


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










#Opponent bet amounts  
    
def botaction(): #Connects it with UI and display
    global highestbet,pot
    messages =[]
    for bot in bots:
        if bot.folded or bot.allin:
            continue
        highestbet,pot,message = bot.botbet(calccards[:currentbettingstage()],highestbet,pot)
        messages.append(message)
    updatelabels()
    botmessage(" | ".join(messages) if messages else "")

    if all(bot.folded for bot in bots):
        human.money += pot
        pot = 0 
        updatelabels()
        disablebuttons()
        botmessage("All fold")
        root.after(2000,newround)
    refresh_buttons()



#One round of betting, e.g flop vs river
def currentbettingstage():
    if(phase =="preflop"):
        return 0
    elif(phase =="flop"):
        return 3
    elif(phase =="turn"):
        return 4
    return 5

#g
def nextphase():
    global phase, highestbet
    human.bet = 0
    for bot in bots:
        bot.bet =0
    highestbet=0
    if phase == "preflop":
        phase = "flop"
        displaycards(boardcards[:3], 360)
        show_message("Flop")
    elif phase == "flop":
        phase = "turn"
        displaycards(boardcards[:4], 360)
        show_message("Turn")
    elif phase == "turn":
        phase = "river"
        displaycards(boardcards, 360)
        show_message("River")
    elif phase == "river":
        phase = "showdown"
        compare()
    if(human.money<=0 or all(bot.money<=0 for bot in bots)):
        displaycards(boardcards,360)
        phase="showdown"
        compare()



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
    for bot in bots:
        status = " (folded)" if bot.folded else ""
        canvas.itemconfig(bot.money_text, text =f"{bot.name}: ${bot.money}{status}")
        canvas.itemconfig(bot.bot_text,text=f"bet: ${bot.bet}")
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
    global  pot
    if human.folded or all(bot.folded for bot in bots) or phase == "showdown":
        return
    human.folded =True
    active = [bot for bot in bots if not bot.folded]
    if active:
        split = pot//len(active)
        for bot in active:
            bot.money +=split
    pot = 0
    updatelabels()
    disablebuttons()
    root.after(2000, newround)

def checking():
    if human.folded or all(bot.folded for bot in bots) or phase == "showdown":
        return
    show_message("You Check")
    botaction()
    if all(bot.folded for bot in bots):
        return
    if highestbet > human.bet:           # bot raised let player respond
        show_message(f"A bot raised to ${highestbet}. Call, raise, or fold.")
    else:
        nextphase()
    refresh_buttons()

def calling():
    global  pot
    if human.folded or all(bot.folded for bot in bots) or phase == "showdown":
        return
    amount = highestbet-human.bet
    human.money -= amount
    human.bet += amount
    pot += amount
    updatelabels()
    nextphase()
    refresh_buttons()
    botaction()

def raising():
    global highestbet, pot
    if human.folded or all(bot.folded for bot in bots) or phase == "showdown":
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
    botaction()
    refresh_buttons()
    if all(bot.folded for bot in bots):
        return
    if highestbet > human.bet:
        botmessage(f"A bot re-raised to ${highestbet} Choose what to do")
    else:
        nextphase()

#ended here
#preparing variable function
def startgame():
    global human.money, Opponentmoney, startingmoney
    human.money = startslider.get()
    Opponentmoney = human.money
    startingmoney = human.money
    canvas.delete("startscreen")
    startbutton.destroy()
    startslider.destroy()
    newround()


#When someone goes broke, game ends and restarts
def restartgame(msg):
    global startbutton, startslider,ui,human.money,Opponentmoney
    ui=False
    human.money=0
    Opponentmoney=0
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

    startbutton = tk.Button(root, text="Play Again", width=15, font=("Arial", 16),
                            bg="#f39c12", fg="white", command=startgame)
    canvas.create_window(640, 470, window=startbutton, tags="startscreen")

    disablebuttons()

#essentially the main game loop
def newround():
    global phase, human.bet, opponentbet, highestbet, pot, oppFolded, youFolded
    global Botallin, Youallin, boardcards, playercards, opponentcards
    global botshow, calccards, deck, ui, human.money, Opponentmoney
    global pot_text, your_money_text, opp_money_text, message_text, botactiontext, your_bet_text
    global btn_frame, foldbutton, checkbutton, callbutton, raisebar, raisebutton, opponent_bet_text
    #extra precaution
    if human.money <= 0:
        restartgame("You Lost.")
        return
    if Opponentmoney <= 0:
        restartgame("You Won!")
        return

    # UI creation without doing it too much
    if not ui:
        ui = True
        pot_text = canvas.create_text(640, 260, text="Pot: $0", fill="white", font=("Arial", 20),tags="gameui")
        your_money_text = canvas.create_text(640, 620, text="Your money: $1000", fill="white", font=("Arial", 16),tags="gameui")
        opp_money_text = canvas.create_text(640, 40, text="Bot money: $1000", fill="white", font=("Arial", 16),tags="gameui")
        message_text = canvas.create_text(1040, 500, text="", fill="yellow", font=("Arial", 18),tags="gameui")
        botactiontext = canvas.create_text(1040, 567, text="", fill="yellow", font=("Arial", 18),tags="gameui")
        your_bet_text = canvas.create_text(1040,620,text="Your bet: $100", fill="white", font=("Arial", 16),tags="gameui")
        opponent_bet_text = canvas.create_text(1040,40,text="opponent bet: $50", fill="white", font=("Arial", 16),tags="gameui")
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
    human.bet = 0
    opponentbet = 0
    highestbet = mustbet * 2
    pot = 0
    oppFolded = False
    youFolded = False
    Botallin = False
    Youallin = False

    # Deal cards every round
    deck = Clubs + hearts + Spades + Diamonds
    boardcards = []
    for i in range(5):
        k = random.randint(0,len(deck)-1)
        boardcards.append(deck[k])
        deck.pop(k)
    playercards = []
    for i in range(2):
        k = random.randint(0,len(deck)-1)
        playercards.append(deck[k])
        deck.pop(k)
    opponentcards = []
    for i in range(2):
        k = random.randint(0,len(deck)-1)
        opponentcards.append(deck[k])
        deck.pop(k)
    playercards+=boardcards
    opponentcards+=boardcards

    showopponentcards = []
    for i in opponentcards:
        suit = i[0]
        card = i[1]
        if(ord(card)>57):
            if(card == ":"):
                card = "T"
            elif(card == ";"):
                card = "J"
            elif(card == "<"):
                card = "Q"
            elif(card == "="):
                card = "K"
            else:
                card = "A"
        showopponentcards.append(card+suit)
    botshow = showopponentcards[:2]

    calccards = []
    for i in boardcards:
        suit = i[0]
        card = i[1]
        if(ord(card)>57):
            if(card == ":"):
                card = "T"
            elif(card == ";"):
                card = "J"
            elif(card == "<"):
                card = "Q"
            elif(card == "="):
                card = "K"
            else:
                card = "A"
        calccards.append(card+suit)

    #Starting the money
    human.money -= mustbet
    Opponentmoney -= mustbet * 2
    human.bet += mustbet
    opponentbet += mustbet * 2
    pot += mustbet * 3

    if human.money <= 0 or Opponentmoney <= 0:
        
        if Opponentmoney < 0:
            winner = "You Won!" 
        else:
            winner = "You Lost."
        restartgame(winner)
        return
    canvas.delete("card")
    displaycards(playercards[:2], 500)
    displaycards(opponentcards[:2], 100, hidden=True)
    updatelabels()
    show_message("preflop")
    refresh_buttons()



#Initialization of startscreen

canvas.create_text(640, 280, text="Poker Game", fill="white", font=("Arial", 48), tags="startscreen")
canvas.create_text(640, 340, text="Choose starting amount:", fill="white", font=("Arial", 20), tags="startscreen")

startslider = tk.Scale(root, from_=500, to=5000, orient="horizontal",length=300, resolution=50, bg="#35654d", fg="white",font=("Arial", 14))
startslider.set(1000)
canvas.create_window(640, 400, window=startslider, tags="startscreen")

startbutton = tk.Button(root, text="Start Game", width=15, font=("Arial", 16),bg="#f39c12", fg="white", command=startgame)
canvas.create_window(640, 470, window=startbutton, tags="startscreen")

root.mainloop()

