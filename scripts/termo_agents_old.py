import pandas as pd
import random

guesses_path = "../data/valid_guesses.csv"
file_guesses = pd.read_csv(guesses_path)
answers_path = "../data/valid_answers.csv"
file_answers = pd.read_csv(answers_path)

valid_guesses = file_guesses['word']
valid_answers = file_answers['word']


# ------------------------------------------
#                Bogo Agent
# ------------------------------------------

def bogo_agent(*args):
    """
    Bogo Agent tenta acertar as palavras de maneira aleatória.
    """
    return random.choice(valid_answers)


# ------------------------------------------
#            Simple Reflex Agent
# ------------------------------------------

def try_word_check(try_word, target_word):
    """
    1  -> letra correta no lugar correto
    0  -> letra existe mas em outra posição
    -1 -> letra não existe
    """

    result = [-1] * len(try_word)

    available = list(target_word)

    # Marca os acertos exatos (1)
    for i in range(len(try_word)):
        if try_word[i] == target_word[i]:
            result[i] = 1
            available[i] = None  # consome a letra

    # Marca letras existentes fora de posição (0)
    for i in range(len(try_word)):
        if result[i] == -1:
            if try_word[i] in available:
                result[i] = 0

                # consome apenas UMA ocorrência da letra
                letter_index = available.index(try_word[i])
                available[letter_index] = None
                
    return result

def ranking_words(valid_answers, valid_guesses):
    words = {}
    for guess in valid_guesses:
        words[guess] = 0 
        for answer in valid_answers:
            score = sum(try_word_check(guess, answer))
            words[guess] += score 
    return words

def simple_reflex_agent(history, valid_answers=file_answers['word'], valid_guesses=file_guesses['word']):
    """
    Simple Reflex Agent faz tentativas com a vencedora da funcao:
    ranking_words()
    """
    
    if(not history):
        #ranked_words = ranking_words(valid_answers, valid_guesses)
        #return max(ranked_words, key=ranked_words.get)
        return 'serao'

    # History é uma LISTA de DICIONÁRIOS
    # history = [
    #     {'abc': [1, 1, -1]},
    #     {'dec': [-1, -1, -1]}
    # ]

    # attempt -> {'abc': [1, 1, -1]}
    # word -> 'abc'
    # score -> [1, 1, -1]

    letters_in_word = set()
    for attempt in history:
        for word, score in attempt.items():
            for i in range(len(word)):
                if score[i] >= 0:  # Se for 0 ou 1, a letra existe
                    letters_in_word.add(word[i])
                    
    wrong_letters = set()
    for attempt in history:
        for word, score in attempt.items():
            for i in range(len(word)):
                if score[i] == -1 and word[i] not in letters_in_word:
                    wrong_letters.add(word[i])
    
    # wrong_letters = ['c', 'd', 'e', 'c']

    # Remover todas as palavras que contem as wrong_letters
    valid_answers = [
        word for word in valid_answers 
        if not any(letter in word for letter in wrong_letters)
    ]

    history_words = set()
    for attempt in history:
        history_words.update(attempt.keys())

    valid_answers = [
        word for word in valid_answers 
        if word not in history_words
    ]

    # valid_guesses = [
    #     word for word in valid_guesses 
    #     if not any(letter in word for letter in wrong_letters)
    # ]

    # Filtro de letras nas posições corretas ou quase corretas

    for attempt in history:
        for word, score in attempt.items():
            for i in range(len(word)):
                letter = word[i]
                s = score[i]

                if s == 1: # Verde: a letra tem que estar nesta posição
                    valid_answers = [w for w in valid_answers if w[i] == letter]

                if s == 0: # Amarelo: a letra tem que existir mas não nesta posição
                    valid_answers = [w for w in valid_answers if letter in w and w[i] != letter]


    # Rankeamento das palavras
    ranked_words = ranking_words(valid_answers, valid_answers)
    #print(ranked_words)
    return max(ranked_words, key=ranked_words.get)
