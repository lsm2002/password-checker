from flask import Flask, send_from_directory, request, render_template
from flask_socketio import SocketIO
import random #importing external modules
from tkinter import *

topkeyboard = "QWERTYUIOP"
middlekeyboard = "ASDFGHJKL"
bottomkeyboard = "ZXCVBNM"
wholekeyboard = topkeyboard + middlekeyboard + bottomkeyboard
digits = "0123456789"
symbols = "!$%^&*()-_=+"
allowedcharacters = wholekeyboard + wholekeyboard.lower() + digits + symbols
pointconditions = [wholekeyboard, wholekeyboard.lower(), digits, symbols]
pointconditions2 = [wholekeyboard + wholekeyboard.lower(), digits, symbols]
pointsconditionsstrs = ["Upper Case Characters", "Lower Case Characters", "Numbers", "Symbols"]
pointsconditionsstrs2 = ["Upper Case and Lower Case Characters", "Numbers", "Symbols"]
dictionary = []


APP = Flask(__name__)
def opendictionary():
    f = open("Dictionary.txt", "r")
    for line in f:
        dictionary.append(line[0:-1].lower())
    f.close()

opendictionary()

def checkallowedcharacters(password):
    for character in password:
        if not(character in allowedcharacters):
            return character
    return True

def checkpasswordallowed(password):
    if checkallowedcharacters(password) != True:
        return "Error: The \'" + checkallowedcharacters(password)+ "\' character is not allowed"
    elif len(password) < 8:
        return "Error: The password is too short, the password must be 8 or more characters long"
    elif len(password) > 24:
        return "Error: The password is too long, the password must be 24 or less characters long"
    else:
        return True

def charactersincharacters(characters1, characters2):
    for character in characters1:
        if character in characters2:
            return True
    return False

def charactersonlyincharacters(characters1, characters2):
    for character in characters1:
        if not(character in characters2):
            return False
    return True

def dictionarycheck(password):
    wordsfound = []
    for i in dictionary:
        for j in range(0, len(password)-len(i)+1):
            teststring = password[j:j+len(i)]
            if i.upper() == teststring.upper():
                if not(i[0].upper() + i[1:] in wordsfound):
                    wordsfound.append(i[0].upper() + i[1:])
    return wordsfound

def keyboardcheck(password):
    deductions = 0
    for i in range(0,len(password)-2):
        for j in range(0,len(topkeyboard)-2):
            if(password[i]+password[i+1]+password[i+2]).upper()==(topkeyboard[j]+topkeyboard[j+1]+topkeyboard[j+2]):
                deductions += 5
        for j in range(0,len(middlekeyboard)-2):
            if(password[i]+password[i+1]+password[i+2]).upper()==(middlekeyboard[j]+middlekeyboard[j+1]+middlekeyboard[j+2]):
                deductions += 5
        for j in range(0,len(bottomkeyboard)-2):
            if(password[i]+password[i+1]+password[i+2]).upper()==(bottomkeyboard[j]+bottomkeyboard[j+1]+bottomkeyboard[j+2]):
                deductions += 5
    return deductions
    
def passwordgenerator():
    score = 0
    while score <= 20:
        password=""
        length = random.randint(8,12)
        for i in range(0,length):
            password += random.choice(allowedcharacters)
        score = passwordchecker(password)
    print(password)
    return[password,score]

def passwordchecker(password):
    message = ""
    if checkpasswordallowed(password) == True:
        containscharacters = ""
        points = 0
        i = 0
        message += ("<p style='color:green;'>Your password is " + str(len(password)) + " characters long adding " + str(len(password)) + " points</p><br>")
        for characters in pointconditions:
            if charactersincharacters(password, characters):
                points += 5
                containscharacters += ", "+pointsconditionsstrs[i]
            i += 1
        message += ("<p style='color:green;'>Your password contains:" + containscharacters[1:] + " adding " + str(points) + " points</p><br>")
        if points == 20:
            points += 10
            message += ("<p style='color:green;'>Your password contains characters of all types, adding an additional 10 points</p><br>")
        i=0
        for characters in pointconditions2:
            if charactersonlyincharacters(password, characters):
                points += -5
                message += ("<p style='color:red;'>Your password contains only "+pointsconditionsstrs2[i] + " subtracting 5 points</p><br>")
            i+=1
        if keyboardcheck(password) != 0:
            message += "<p style='color:red;'>Subtracting " + str(keyboardcheck(password)) + " points for use of consecutive characters on the keyboard</p><br>"
        points += -1 * keyboardcheck(password)
        points += len(password)
        message += ("<p style='color:black;'>Your final score is "+ str(points)+"</p><br>")
        if dictionarycheck(password) != []:
            printstring = ""
            for word in dictionarycheck(password):
                printstring += ", " + word
            message += ("<p style='color:red;'>The password checker found the following words in your password:" + printstring[1:]+"</p><br>")
            message += ("<p style='color:red;'>Having words in your password makes your password vunerable to dictionary attack, a more efficient cracking method</p><br>")
        if points < 0:
            colour = "red"
            strength = "Weak"
        elif points > 20:
            colour = "green"
            strength = "Strong"
        else:
            colour = "yellow"
            strength = "Medium"
        f = open("Passwords.txt", "a+")
        f.write("\"" +password + "\"" + " Score: " + str(points) + " " +strength + "\n")
        return (message,colour)
    else:
        return ("<p style='color:red;'>"+checkpasswordallowed(password)+"</p>", "red")

socketio = SocketIO(APP)
@APP.route('/')
def main():
    return render_template('main.j2', text="WOW")

@APP.route('/styles')
def styles():
    return send_from_directory("templates", "styles.css")
	
@socketio.on('sendpassword')
def checkpassword(password):
    message, colour = passwordchecker(password)
    socketio.emit('sendfeedback', message)
    socketio.emit('changebackground', colour)

socketio.run(APP)
