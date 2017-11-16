from collections import defaultdict
import random, re, operator
from pyrhyme.rhyme import rhymes_with
from nltk.corpus import wordnet

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

    def generateUnconstrainedPoem(self):
        """ Generates a poem of random length """
        bigram = random.choice(self.bigramMap.keys())    # get random initial seed
        sentence = bigram
        while (True):     # -2 because seed contains 2 words
            nextWord = weightedRandomChoice(self.bigramMap[bigram])
            if nextWord == 'EOF': break
            sentence += ' {}'.format(nextWord)
            bigram = bigram.split()[1] + ' {}'.format(nextWord)    # slide the window

        return re.sub(r'NEWLINE', '\n', sentence)

    def generateCandidateLines(self, n):
        
        candidates = []
        line = []
        for _ in range(n):

            while True: 
                bigram = random.choice(self.bigramMap.keys())    # get random initial seed
                if not 'NEWLINE' in bigram.split(): break

            line = bigram.split()
            while True:
                nextWord = weightedRandomChoice(self.bigramMap[bigram])

                if nextWord == 'EOF' or nextWord == 'NEWLINE': 
                    candidates.append(line)
                    line = []
                    break

                line.append(nextWord)
                # if len(line) > 3:
                    # candidates.append(line)  # use subsentences as candidates for our constrained line function
                bigram = bigram.split()[1] + ' {}'.format(nextWord)    # slide the window

        return candidates

    def generateConstrainedPoem(self):
        """ Generates a poem using basic rhyme scheme constraints """

        def getSynonyms(word):
            synonyms = [word]
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    if lemma.name() != word:
                        w, n = re.subn("_", " ", lemma.name())
                        synonyms.append(w)
            s = list(set(synonyms))
            return s

        def prune(lines, candidateLines):
            if len(lines) <= 1:
                return [{tuple(line): 1.0} for line in candidateLines[0:8]]   # no constraints to satisfy -- return first 5 with weight 1.0

            options = {}
            for d in lines[-2]:
                for line, weight in d.items():
                    wordToMatch = line[-1]
                    rhymes = [wordToMatch] + rhymes_with(wordToMatch)

                    for candidate in candidateLines:
                        lastWord = candidate[-1]
                        for syn in getSynonyms(lastWord):
                            if syn.split()[-1] in rhymes:
                                options[tuple(candidate[:-1] + [syn])] = weight * 2.0


                        if tuple(candidate) not in options:
                            options[tuple(candidate)] = 1.0

            return [{t[0]: t[1]} for t in sorted(options.items(), key=operator.itemgetter(1))[-8:]]

        lines = []  # list of {line -> weight}, maintains top 5 candidates for each line
        n = 0
        while (True):
            candidateLines = self.generateCandidateLines(20)    # generate 20 sentences using a random bigram seed
            weightedLines = prune(lines, candidateLines)    # returns {line -> weight} dictionary of length 5
            lines.append(weightedLines)
            n += 1
            if n == 12: break

        i = 0
        for weighted in lines:
            i += 1
            print()
            print("candidates for line {}:\n{} ".format(i, weighted))

        return '\n'.join(lines)


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


