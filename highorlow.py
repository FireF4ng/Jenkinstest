from random import randint

# Game parameters
MIN_NUMBER = 1
MAX_NUMBER = 100
MAX_GUESSES = 10

# Number to be guessed
randnumber = randint(MIN_NUMBER, MAX_NUMBER)
# Current number of guesses
numberofguesses = 0
# A list of all guesses
allguesses = []
# is a correct guess
correctguess = False

print("Welcome to the Higher or Lower Game")
print("Your goal is to guess the generated number ("+str(MIN_NUMBER) +
"-"+str(MAX_NUMBER)+") within "+str(MAX_GUESSES)+" tries")
print("Good luck !!!")
while """cond-arrêt""":
# Afficher le nombre des essais restants
# Lire le chiffre depuis la console, incrémenter le nombre d'essais et
    ajouter le chiffre courant à la liste des essais
# Comparer les chiffres en donnant des indices au joueur en fonction
    de son essai courant
    if ("""si le chiffre généré est plus grand que le chiffre courant"""):
    if ("""si le chiffre généré est plus petit que le chiffre courant"""):
    if ("""si le chiffre généré est le même que le chiffre courant"""):
    # Afficher la liste des essais
    print("Your guesses are :" + str(allguesses))
    if """si le joueur a gagné""":
    if """si le joueur a perdu""":