from random import randint

class Game:
    def __init__(self):
        self.min_number = 1
        self.max_number = 100
        self.max_guesses = 10
        self.rand_number = randint(self.min_number, self.max_number)
        self.number_of_guesses = 0
        self.all_guesses = []
        self.correct_guess = False
    
    def play(self):
        print("Welcome to the Higher or Lower Game")
        print("Your goal is to guess the generated number ("+str(self.min_number) +
              "-"+str(self.max_number)+") within "+str(self.max_guesses)+" tries")
        print("Good luck !!!")
        while self.number_of_guesses < self.max_guesses:
            print("You have " + str(self.max_guesses-self.number_of_guesses) +
                  " guesses left")
            guess = int(input("Enter your guess: "))
            self.number_of_guesses += 1
            self.all_guesses.append(guess)
            if self.rand_number > guess:
                print("The number is higher")
            elif self.rand_number < guess:
                print("The number is lower")
            else:
                print("Congratulations, you have guessed the number")
                self.correct_guess = True
                break
            print("--------------------------------")
        print("The number was: " + str(self.rand_number))
        if not self.correct_guess:
            print("You have run out of guesses, better luck next time")
    

if __name__ == "__main__": 
    game = Game()
    game.play()
