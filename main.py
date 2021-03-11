import json
from hashlib import md5
import numpy as np

SAMPLE_SENTENCES = [
    "Hello,    my name is Michael.",
    "Hello, my name is Mannie.",
    "Hello, my name is multi\nline sentence.",
    "Hello, my name is dog",
    "Hello, my name is dog",
    "Hello, my name is cat",
    "Hello, my game is zaggit",
]

ENCODING = "utf-8"


def create_word_sequence(text):
    sentences = []
    for entry in text:
        entry = entry.split("\n")
        for line in entry:
            sentences += line.split(" ")
            sentences.append("\n")
    return sentences


def word_to_hash(word):
    hasher = md5()
    hasher.update(bytes(word, ENCODING))
    return hasher.hexdigest()


def create_markov_obj():
    return {}


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


if __name__ == "__main__":
    markov = create_markov_obj()
    update_markov_obj(markov, SAMPLE_SENTENCES)
    print(json.dumps(markov, indent=2))
