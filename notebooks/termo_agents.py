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

def model_based_reflex_agent(histories, valid_answers=file_answers['word']):
    """
    Model-Based Reflex Agent faz tentativas com a vencedora da funcao:
    ranking_words()
    Ele usa o histórico para descartar palavras

    """

    if all(not history for history in histories):
        return 'serao'

    # Removendo boards que já foram finalizados
    won_histories = []
    for history in histories:
        for attempt in history:
            for score in attempt.values():
                if score == [1,1,1,1,1]:
                    won_histories.append(history)

    for history in won_histories:
        histories.remove(history)

    # len(histories) -> Quantidade de quadros de jogos
    # Dueto -> len(histories) = 2
    # Quarteto -> len(histories) = 4

    qnt_board = len(histories)

    # Histories é uma LISTA de 'History'
    # Histories = [
    #   [ # game01
    #     {'abc': [1, 1, -1]},
    #     {'dec': [-1, -1, -1]}
    #   ],
    #   [ # game02
    #     {'abc': [1, 1, -1]},
    #     {'dec': [-1, -1, -1]}
    #   ]
    # ]
    # 'History' é uma LISTA de DICIONÁRIOS
    # history = [
    #     {'abc': [1, 1, -1]},
    #     {'dec': [-1, -1, -1]}
    # ]

    # attempt -> {'abc': [1, 1, -1]}
    # word -> 'abc'
    # score -> [1, 1, -1]

    # Um set() para cada board
    letters_in_games = [set() for i in range(qnt_board)]

    # Salvando letras que existem em cada board
    for i, history in enumerate(histories):
        for attempt in history:
            for word, score in attempt.items():
                for j in range(len(word)):
                    if score[j] >= 0:  # Se for 0 ou 1, a letra existe
                        letters_in_games[i].add(word[j])

   # letters_in_games = [
   #     {'a', 'b'},
   #     {'b', 'c'}
   # ]

    # Salvando letras erradas de cada board
    wrong_letters_in_games = [set() for i in range(qnt_board)]
    for i, history in enumerate(histories):
        for attempt in history:
            for word, score in attempt.items():
                for j in range(len(word)):
                    if score[j] == -1 and word[j] not in letters_in_games[i]:
                        wrong_letters_in_games[i].add(word[j])

    #print("wrong_letters:", wrong_letters_in_games)
    # wrong_letters_in_games = [
    #       {'c', 'd'},
    #       {'c', 'd', 'e', 'c'},
    # ]

    # Remove todas as palavras que contem as wrong_letters
    valid_answers_games = [valid_answers for i in range(qnt_board)]
    for i in range(len(valid_answers_games)):
        valid_answers_games[i] = [
            word for word in valid_answers
            if not any(letter in word for letter in wrong_letters_in_games[i])
        ]


    # Remover palavras já tentadas em cada board
    histories_words = [set() for i in range(qnt_board)]
    for i, history in enumerate(histories):
        for attempt in history:
            histories_words[i].update(attempt.keys())

    for i, valid_answers in enumerate(valid_answers_games):
        valid_answers_games[i] = [
            word for word in valid_answers
            if word not in histories_words[i]
        ]

    # Filtro de letras nas posições corretas ou quase corretas
    for i, history in enumerate(histories):
        for attempt in history:
            for word, score in attempt.items():
                for j in range(len(word)):
                    letter = word[j]
                    s = score[j]

                    if s == 1: # Verde: a letra tem que estar nesta posição
                        valid_answers_games[i] = [w for w in valid_answers_games[i] if w[j] == letter]

                    if s == 0: # Amarelo: a letra tem que existir mas não nesta posição
                        valid_answers_games[i] = [w for w in valid_answers_games[i] if letter in w and w[j] != letter]

    #print("valid_answers após filtro:", valid_answers_games)

    # Rankeamento das palavras
    ranked_words_games = [dict() for i in range(qnt_board)]
    for i, valid_answers in enumerate(valid_answers_games):
        ranked_words_games[i] = ranking_words(valid_answers, valid_answers)

    #print("ranked_words:", ranked_words_games)

    all_ranked_words = {}
    for i, words in enumerate(ranked_words_games):
        for word, score in words.items():
            # Se a palavra aparece em vários boards, soma os scores
            all_ranked_words[word] = all_ranked_words.get(word, 0) + score
    #ranked_words = ranking_words(valid_answers, valid_answers)
    #print(ranked_words)
    return max(all_ranked_words, key=all_ranked_words.get)

def test_agents_exhaustive(agent, valid_answers):
    tries_count = [0] * 7

    for target_word in valid_answers:
        history = []
        tries = -1

        for attempt in range(6):
            if agent.__name__ == 'model_based_reflex_agent':
                try_word = agent([history], valid_answers)
            else:
                try_word = agent(history, valid_answers)

            history.append({try_word: try_word_check(try_word, target_word)})

            if try_word == target_word:
                tries = attempt
                break

        # if tries == -1:
        #     print(target_word)

        tries_count[tries] += 1

    return tries_count


# resultado = test_agents_exhaustive(model_based_reflex_agent, valid_answers)
#
# print("Distribuição de vitórias por tentativa (e derrotas no final):")
# print(resultado)
#
# total_jogos = len(valid_answers)
# vitorias = sum(resultado[:-1])
# derrotas = resultado[-1]
#
# print(f"\nTotal de palavras testadas: {total_jogos}")
# print(f"Taxa de acerto exata: {(vitorias / total_jogos) * 100:.2f}%")
# print(f"Taxa de derrota exata: {(derrotas / total_jogos) * 100:.2f}%")