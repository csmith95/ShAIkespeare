from collections import defaultdict
import random, re, operator
from pyrhyme.rhyme import rhymes_with
from nltk.corpus import wordnet
import prosodic as p

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

        def randomSeed(bigramMap):
            while True:
                bigram = random.choice(self.bigramMap.keys())    # get random initial seed
                if not 'NEWLINE' in bigram.split(): 
                    return bigram

        candidates = []
        line = []
        # each iteration of this loop appends a candidate line
        for _ in range(n):

            bigram = randomSeed(self.bigramMap)
            line = bigram.split()
            count = self.syllableCount(bigram)
            while True:
                nextWord = weightedRandomChoice(self.bigramMap[bigram])

                # add if count is in the neighborhood of 10 syllables
                # number of syllables can change when we sub in synonyms 
                # trying to enforce rhyme/meter
                if count >= 9 and count <= 11: 
                    candidates.append(line)
                    line = []
                    break

                if count > 11:  # overshot -- try again from start
                    bigram = randomSeed(self.bigramMap)
                    line = bigram.split()
                    count = self.syllableCount(bigram)
                    continue

                line.append(nextWord)
                count += self.syllableCount(nextWord)
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

        def makeIambic(self, line):

            def recursiveMakeIambic(self, currentIndex, line):
                # base case -- iambic or reached end of line
                weight = self.iambic(line)
                if weight >= 0.7 or currentIndex == len(line) - 1:
                    return (line, weight)

                # recurse on the words left
                for syn in getSynonyms(line[currentIndex]):
                    newLine = line[:currentIndex] + syn.split() + line[currentIndex+1:]
                    option, weight = recursiveMakeIambic(currentIndex+1, newLine)
                    if weight >= 0.7:
                        return (option, weight)

                return (None, 0.0)


            # start
            for index, word in enumerate(line[:-1]):  # try modify everything but last word (rhyming word)
                option, weight = self.recursiveMakeIambic(index, line)
                if weight >= 0.7:
                    return (option, weight)

            return (None, 0.0)


        def prune(lines, candidateLines):
            options = {}
            if len(lines) <= 1:
                for line in candidateLines:
                    options[tuple(line)] = self.iambic(line)

                # return 16 with highest weight
                return [{t[0]: t[1]} for t in sorted(options.items(), key=operator.itemgetter(1))[-16:]]

            options = {}
            for d in lines[-2]:
                for line, weight in d.items():
                    wordToMatch = line[-1]
                    rhymes = [wordToMatch] + rhymes_with(wordToMatch)

                    for candidate in candidateLines:
                        lastWord = candidate[-1]
                        for syn in getSynonyms(lastWord):
                            if syn.split()[-1] in rhymes:
                                newLine = candidate[:-1] + [syn]
                                iambicWeight = self.iambic(line)
                                if iambicWeight >= 0.7:     # 0.7 is almost perfectly iambic
                                    options[tuple(newLine)] = weight * 2.0  # * 2 for the rhyme
                                else:
                                    # try to make it more iambic
                                    iambicLine, newIambicWeight = self.makeIambic(line)
                                    if newIambicWeight > iambicWeight:   # if we improved iambic score at all, use this line
                                        newLine = iambicLine
                                        iambicWeight = newIambicWeight
                                    
                                    options[tuple(newLine)] = weight * iambicWeight * 2.0

                                # keep pointer to previous lines that rhyme
                                rhymingLines[tuple(newLine)].append(line)

                        if tuple(candidate) not in options:
                            options[tuple(candidate)] = 2.0 if self.iambic(line) else 1.0

            # return 16 with highest weight
            return [{t[0]: t[1]} for t in sorted(options.items(), key=operator.itemgetter(1))[-16:]]

        lines = []  # list of {line -> weight}, maintains top 8 candidates for each line
        rhymingLines = defaultdict(lambda: [])   # dict from line to list of rhyming lines
        n = 0
        while (True):
            candidateLines = self.generateCandidateLines(40)    # generate 40 lines using a random bigram seed
            weightedLines = prune(lines, candidateLines)    # returns {line -> weight} dictionary w/ 16 lines
            lines.append(weightedLines)
            n += 1
            if n == 12: break

        def getMaxWeightLine(options):
            for d in options:
                maxWeight = 0.0
                bestLine = None
                for line, weight in d.items():
                    if weight > maxWeight:
                        maxWeight = weight
                        bestLine = line
            return bestLine

        result = [getMaxWeightLine(lines[-1])]
        result.insert(0, getMaxWeightLine(lines[-2]))
        for i in range(10):
            options = rhymingLines[result[1]]
            if len(options) == 0:
                # no rhyming lines -- choose max weight line
                previousLine = getMaxWeightLine(lines[i-12-1])
            else:
                previousLine = random.choice(options)

            result.insert(0, previousLine)

        return '\n'.join([' '.join(line) for line in result])

    def syllableCount(self, line):
        print(line)
        text = p.Text(line)
        text.parse()
        return len(text.syllables())

    def iambic(self, line):
        joined = ' '.join(line)
        return self.syllableCount(joined) == 10


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
