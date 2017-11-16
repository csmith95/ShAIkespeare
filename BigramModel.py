from collections import defaultdict
import random, re

class BigramModel:

    def __init__(self, corpus):
        """Initialize your data structures in the constructor.
            |corpus| should be a list of lists where each entry is a sentence
            and each sentence contains words of the sentence.
        """
        self.bigramMap = defaultdict(lambda : defaultdict(int))
        self.train(corpus)

    def train(self, corpus):
        """ Takes a corpus and trains your language model. 
            Compute any counts or other corpus statistics in this function.
        """  
        for poem in corpus: 
            for i in range(len(poem)-2):  
                bigram = poem[i] + ' ' + poem[i+1]
                self.bigramMap[bigram][poem[i+2]] += 1

    def generatePoem(self):
        """ Generates a poem of length |numWords| """
        bigram = random.choice(self.bigramMap.keys())    # get random initial seed
        sentence = bigram
        while (True):     # -2 because seed contains 2 words
            nextWord = weightedRandomChoice(self.bigramMap[bigram])
            if nextWord == 'EOF': break
            sentence += ' {}'.format(nextWord)
            bigram = bigram.split()[1] + ' {}'.format(nextWord)    # slide the window

        return re.sub(r'NEWLINE', '\n', sentence)

# Function: Weighted Random Choice
# --------------------------------
# Given a dictionary of the form element -> weight, selects an element
# randomly based on distribution proportional to the weights. Weights can sum
# up to be more than 1. 
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(weightDict[elem])
        elems.append(elem)
    total = sum(weights)
    key = random.uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    return 'EOF'


