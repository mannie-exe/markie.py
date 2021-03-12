from os.path import abspath
from hashlib import md5
import numpy as np

ENCODING = "utf-8"
MESSAGES = "./data/messages.txt"


def word_to_hash(word):
    hasher = md5()
    hasher.update(bytes(word, ENCODING))
    return hasher.hexdigest()


def create_word_sequence(text):
    sentences = []
    for sentence in text.split("\n"):
        for word in sentence.split(" "):
            sentences.append(word)
        sentences.append("\n")
    return sentences


create_markov_obj = lambda: {}


def recalculate_markov_obj(markov_obj):
    for word_key in markov_obj:
        word_data = markov_obj[word_key]
        if word_data["value"] == "\n":
            continue

        # get all counts of next words
        # possible after current
        total_next_count = 0
        for next_word_key in word_data["next_words"]:
            next_word_data = word_data["next_words"][next_word_key]
            total_next_count += next_word_data["count"]

        # calculate probabilities based
        # on total word occurrences
        for next_word_key in word_data["next_words"]:
            next_word_data = word_data["next_words"][next_word_key]
            next_word_data["probability"] = next_word_data["count"] / total_next_count


def update_markov_obj(markov_obj, text):
    word_sequence = create_word_sequence(text)

    # ensure newline terminations
    # are handled before filling
    if not word_to_hash("\n") in markov_obj:
        markov_obj[word_to_hash("\n")] = {
            "value": "\n",
            "next_words": None,
        }

    for idx, word in enumerate(word_sequence):
        if word == "\n":
            continue

        next_word = word_sequence[idx + 1]
        word_key = word_to_hash(word)
        next_word_key = word_to_hash(next_word)

        # check if key exists
        if not word_key in markov_obj:
            # next word definitely doesn't
            # exist, initialize markov_obj[word_key]
            # and fill next word with count 0
            # and (RECALCULATE)
            markov_obj[word_key] = {
                "value": word,
                "next_words": {
                    next_word_key: {
                        "value": next_word,
                        "count": 1,
                        "probability": None,
                    }
                },
            }
            continue

        word_data = markov_obj[word_key]
        # key exists, check if next word
        # has been encountered before
        if not next_word_key in word_data["next_words"]:
            # this word has never preceded
            # the next word before. initialize
            # it to 1 (RECALCULATE)
            word_data["next_words"][next_word_key] = {
                "value": next_word,
                "count": 1,
                "probability": None,
            }
            continue

        # next word's key exists, update
        # word encounters (RECALCULATE)
        next_word_data = word_data["next_words"][next_word_key]
        next_word_data["count"] = next_word_data["count"] + 1

    recalculate_markov_obj(markov_obj)


def select_next_word(markov_obj, current_word_key):
    next_words = markov_obj[current_word_key]["next_words"]

    words = []
    probabilities = []
    for next_word_key in next_words:
        next_word_data = next_words[next_word_key]
        words.append(next_word_key)
        probabilities.append(next_word_data["probability"])

    return np.random.choice(words, p=probabilities)


def random_walk(markov_obj):
    all_keys = list(markov_obj)

    current_word_key = all_keys[np.random.randint(len(all_keys))]
    current_word = markov_obj[current_word_key]
    random_sentence = []

    newline_encounter = False
    while not newline_encounter:
        random_sentence.append(current_word["value"])
        current_word_key = select_next_word(markov_obj, current_word_key)
        current_word = markov_obj[current_word_key]
        if current_word["value"] == "\n":
            newline_encounter = True

    return " ".join(random_sentence)


def init():
    markov = create_markov_obj()
    with open(abspath(MESSAGES), "r", encoding=ENCODING) as messages_file:
        update_markov_obj(markov, messages_file.read())
    return markov


if __name__ == "__main__":
    markov = create_markov_obj()
    with open(abspath(MESSAGES), "r", encoding=ENCODING) as messages_file:
        update_markov_obj(markov, messages_file.read())
    print(random_walk(markov))
else:
    init()
