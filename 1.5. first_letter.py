'''Assignment: Pick apart your user's input
Write a script named first_letter.py that first 
prompts the user for input by using the
string: Tell me your password:
The script should then determine the first letter of the user's input, convert that letter to
upper-case, and display it back. As an example, if the user input was "no" then the
program should respond like this: The first letter you entered was: N
For now, it's okay if your program crashes when the user enters nothing as input (just
hitting ENTER instead). We'll find out a couple ways you could deal with this situation in
an upcoming chapter.'''

userInput = input('Tell me your password: ')
upperUserInput = userInput.upper()
print('The first letter you entered was: ', upperUserInput[0])
