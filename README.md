Poker Game
ICS3U-01
Final Project
Justin Zhou 

Playing Requirements:
Tkinter Library
Pillow Library 
Treys Library
Iterativetools Library 
Random Library 

Game process: 
This is a traditional texas hold-em poker game. 
It is a one versus one against a bot playing under rules set by an algorithm of if and elses.
The bot chooses how to act based on probability of winning. 
Players cannot control what cards they have, only how much they choose to bet. 
In order to help the player, they cannot fold if checking is available. 
The game auto calculates how much is needed to call, and includes a slider that goes upwards to the maximum raise amount possible for the player's current money.
The rounds go until someone goes broke, either player or bot. 
Currently there still exists logs in the terminal that show the bot's cards and board cards. 

How to win:
There are 10 different hands in Texas Hold-em poker
Royal Flush
Straight Flush
Quads
Full house
flush
straight
Trips 
Two pair
Pair 
High card
This is the ranking from highest at the top and lowest at the bottom 
If no player decides to fold before a round ends, 
it goes to a showdown comparing the two hands of the players. 
It first checks if the players have different tiers of hands, 
if they have the same hand, e.g. High Card, it then compares the actual 
cards involved. 


UI:
Working with this game's UI is quite simple. 
The player begins by choosing how much money both sides start with
however no matter the starting amount, there is always a small blind and big blind of 50 and 100. 
There is displays towards the top and bottom to show the remaining amount of money for both players, as well as what the bot is doing on the right and what phase it is of a round. 
The game itself is very intuitive. 

Start by just running pokergame.py
