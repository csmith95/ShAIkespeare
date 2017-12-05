from collections import defaultdict
import random, re, operator
from pyrhyme.rhyme import rhymes_with
from nltk.corpus import wordnet
import prosodic as p

class BigramModel:
    global syllableCount, iambic

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
            count = syllableCount(bigram)
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
                    count = syllableCount(bigram)
                    continue

                line.append(nextWord)
                count += syllableCount(nextWord)
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

        def makeIambic(line):

            # def recursiveMakeIambic(currentIndex, line):
            #     # base case -- iambic or reached end of line
            #     weight = iambic(line)
            #     if weight >= 1.5 or currentIndex  len(line) - 1:
            #         return (line, weight)

            #     # recurse on the words left
            #     i = 0
            #     for syn in getSynonyms(line[currentIndex]):
            #         newLine = line[:currentIndex] + syn.split() + line[currentIndex+1:]
            #         print(newLine)
            #         option, weight = recursiveMakeIambic(currentIndex+1, newLine)
            #         if weight >= 1.5:
            #             return (option, weight)
            #         i += 1
            #         if i == 1: break

            #     return (None, 0.0)

            # start
            print(line)
            for index, word in enumerate(line[:-1]):  # try modify everything but last word (rhyming word)
                # option, weight = recursiveMakeIambic(index, line)
                i = 0
                for syn in getSynonyms(line[index]):
                    newLine = line[:index] + syn.split() + line[index+1:]
                    weight = iambic(newLine)
                    # option, weight = recursiveMakeIambic(currentIndex+1, newLine)
                    if weight >= 1.6:
                        return (newLine, weight)
                    i += 1
                    if i == 4: break

            return (None, 0.0)


        def prune(lines, candidateLines):
            options = {}
            if len(lines) <= 1:
                for line in candidateLines:
                    iambicWeight = iambic(line)

                    if iambicWeight >= 1.6: 
                        options[tuple(line)] = iambicWeight
                    else:
                        # try to make it more iambic
                        iambicLine, newIambicWeight = makeIambic(line)
                        if iambicLine != None and newIambicWeight > iambicWeight:   # if we improved iambic score at all, use this line
                            line = iambicLine
                            iambicWeight = newIambicWeight

                    options[tuple(line)] = iambicWeight
                    print('line: {} \n iambic weight: {}'.format(line, iambicWeight))

                # return 16 with highest weight
                return [{t[0]: t[1]} for t in sorted(options.items(), key=operator.itemgetter(1))[-8:]]

            for d in lines[-2]:
                for line, weight in d.items():
                    wordToMatch = line[-1]
                    rhymes = [wordToMatch] + rhymes_with(wordToMatch)

                    for candidate in candidateLines:
                        lastWord = candidate[-1]
                        for syn in getSynonyms(lastWord):
                            if syn.split()[-1] in rhymes:
                                newLine = candidate[:-1] + [syn]
                                iambicWeight = iambic(newLine)

                                if iambicWeight >= 1.6: 
                                    options[tuple(newLine)] = weight * 2.0 * iambicWeight
                                else:
                                    # try to make it more iambic
                                    iambicLine, newIambicWeight = makeIambic(newLine)
                                    if iambicLine != None and newIambicWeight > iambicWeight:   # if we improved iambic score at all, use this line
                                        newLine = iambicLine
                                        iambicWeight = newIambicWeight
                                    
                                    print(iambicWeight)
                                    options[tuple(newLine)] = weight * iambicWeight * 2.0

                                print('line: {} \n iambic weight: {}'.format(newLine, iambicWeight))
                                # keep pointer to previous lines that rhyme
                                rhymingLines[tuple(newLine)].append(line)

                        if tuple(candidate) not in options:
                            options[tuple(candidate)] = weight

            # return 16 with highest weight
            return [{t[0]: t[1]} for t in sorted(options.items(), key=operator.itemgetter(1))[-8:]]

        lines = []  # list of {line -> weight}, maintains top 8 candidates for each line
        rhymingLines = defaultdict(lambda: [])   # dict from line to list of rhyming lines
        for i in range(10):
            print("********* ", i)
            candidateLines = self.generateCandidateLines(16)    # generate 16 lines using a random bigram seed
            weightedLines = prune(lines, candidateLines)    # returns {line -> weight} dictionary w/ 16 lines
            lines.append(weightedLines)

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
        print(lines[-2])
        print
        print(lines[-1])
        print 
        for i in range(8):
            options = rhymingLines[result[1]]
            if len(options) == 0:
                # no rhyming lines -- choose max weight line
                previousLine = getMaxWeightLine(lines[-1*i - 3])
            else:
                previousLine = random.choice(options)

            result.insert(0, previousLine)

        return '\n'.join([' '.join(line) for line in result])

    def syllableCount(line):
        text = p.Text(line)
        text.parse()
        return len(text.syllables())

    def iambic(line):
        line = ' '.join(line)
        w = 1
        if syllableCount(line) != 10:
            return 1
        t = p.Text(line)
        count = len(t.syllables())
        for i, syl in enumerate(t.syllables()):
            syl.feature()
            if i%2 == 1:
                if syl.feature('prom.stress') == 1.0: count += 1
            if i%2 == 0:
                if syl.feature('prom.stress') == 0.0: count += 1

        return float(count)/len(t.syllables())


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
