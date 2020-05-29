import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy
import tensorflow as tf
import tflearn
import random
import json
import pickle

stemmer = LancasterStemmer()
# nltk.download('punkt')



# https://techwithtim.net/tutorials/ai-chatbot/part-1/


def get_existing_data():
    with open('data.pickle', 'rb') as f:
        return pickle.load(f)


def create_trainable_data(data):
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    words = [stemmer.stem(w.lower()) for w in words if w != '?']
    print(words)
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open('data.pickle', 'wb') as f:
        pickle.dump((words, labels, training, output), f)
    return words, labels, training, output


def create_dnn(training, output):
    tf.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
    net = tflearn.regression(net)

    model = tflearn.DNN(net)
    return model


def run():
    with open('newintents.json') as file:
        data = json.load(file)

    words, labels, training, output = get_existing_data()
    model = create_dnn(training, output)
    # Comment out load part when training new data
    model.load('model.tflearn')
    chat(model, words, labels, data)


def train():
    with open('newintents.json') as file:
        data = json.load(file)

    words, labels, training, output = create_trainable_data(data)
    model = create_dnn(training, output)
    # Comment out two lines below if not training
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save('model.tflearn')


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def chat(model, words, labels, data):
    print('Start talking')
    last_question = ''
    while True:
        inp = input('You: ')
        if inp.lower() == 'quit':
            break

        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if results[results_index] > 0.6:
            answer = get_answer(data, tag)
            if answer['type'] == 'followup': # TODO: Check that this even works at all
                responses = handle_followup(data, answer['tag'], last_question)
            else:
                responses = answer['responses']

            last_question = answer['tag']

            print(random.choice(responses))
            if tag.lower() == 'goodbye':
                break

        else:
            print('Sorry, try again')


# Iterates json object to find the correct object
def get_answer(data, tag):
    for tg in data['intents']:
        if tg['tag'] == tag:
            return tg


# Returns the answer from the follow up question TODO: Fix
def handle_followup(data, tag, last_tag):
    print('last tag: ', last_tag)
    print('tag: ', tag)
    if len(last_tag) > 0:
        last_answer = get_answer(data, last_tag)
        if 'followup' in last_answer:
            if tag in last_answer['followup']:
                return last_answer['followup'][tag]

        else:
            return ['Jag har inte så mycket mer att säga om det']

    return ['Förlåt vad menar du?']


# train()
run()
