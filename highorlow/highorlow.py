from random import randint

class Game:
    def __init__(self):
        self.MIN_NUMBER = 1
        self.MAX_NUMBER = 100
        self.MAX_GUESSES = 10
        self.randnumber = randint(self.MIN_NUMBER, self.MAX_NUMBER)
        self.numberofguesses = 0
        self.allguesses = []
        self.correctguess = False
    
    def play(self):
        print("Welcome to the Higher or Lower Game")
        print("Your goal is to guess the generated number ("+str(self.MIN_NUMBER) +
              "-"+str(self.MAX_NUMBER)+") within "+str(self.MAX_GUESSES)+" tries")
        print("Good luck !!!")
        while self.numberofguesses < self.MAX_GUESSES:
            print("You have " + str(self.MAX_GUESSES-self.numberofguesses) +
                  " guesses left")
            guess = int(input("Enter your guess: "))
            self.numberofguesses += 1
            self.allguesses.append(guess)
            if self.randnumber > guess:
                print("The number is higher")
            elif self.randnumber < guess:
                print("The number is lower")
            else:
                print("Congratulations, you have guessed the number")
                self.correctguess = True
                break
            print("--------------------------------")
        print("The number was: " + str(self.randnumber))
        if not self.correctguess:
            print("You have run out of guesses, better luck next time")
    

if __name__ == "__main__": 
    game = Game()
    game.play()
