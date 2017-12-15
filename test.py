import prosodic as p
from BigramModel import BigramModel
from Database import Database
from pyrhyme.rhyme import rhymes_with



def syllableCount(line):
    text = p.Text(line)
    text.parse()
    return len(text.syllables())

def iambic(line, n):
    w = 1
    if abs(syllableCount(line) - n*2) >= 1:
        return .1
    t = p.Text(line)
    for i, syl in enumerate(t.syllables()):
        syl.feature()
        if i%2 == 1:
            if syl.feature('prom.stress') != 1.0: w*=.9
        if i%2 == 0:
            if syl.feature('prom.stress') != 0.0: w*=.9
    # if w >= .6: return True
    # return False
    return w

# Function: Evaluate Poem
# --------------------------------
# Given a generated poem, evaluates it based on percentage of lines that rhyme
# and percentage of lines that maintain the desired meter. Returns a tuple with
# the two percentages.
#
# @ n -> the meter Ex. for iambicpentameter, n = 5
# @ meterThreshold -> the weight that the line needs to generate to be considered
#                     the desired meter. Should be around .6
#
def evalPoem(map, poemLines, n, meterThreshold):
    A = ''
    B = ''
    numIambics = 0
    numRhymes = 0
    numChoices = 0
    numBigrams = 0
    for i, line in enumerate(poemLines):
        if iambic(' '.join(line),n) >= meterThreshold: numIambics+=1
        words = line
        if i%2 == 0:
            if i == 0:
                A = words[-1]
            else:
                if A in rhymes_with(words[-1]) or words[-1] == A: numRhymes += 1
                A = words[-1]
        if i%2 == 1:
            if i == 1:
                B = words[-1]
            else:
                if B in rhymes_with(words[-1]) or words[-1] == B: numRhymes += 1
                B = words[-1]
        for p in xrange(len(line)-2):
            bigram = line[p] + ' ' + line[p+1]
            numBigrams += 1
            if bigram in map:
                numChoices += len(map[bigram])
    numLines = len(poemLines)
    percentIambic = float(numIambics)/numLines
    percentRhyme = float(numRhymes)/(numLines-2)
    averageBigramChoice = (float(numChoices)/numBigrams)/numLines   
    return (percentIambic,percentRhyme, averageBigramChoice)


db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
n = 1
while(n != 0):
    numPoems = 0
    sumPercentIambic = 0
    sumPercentRhyme = 0
    averageSumBigramChoice = 0
    for _ in range(n):
        print(bigram.generateConstrainedPoem())
        poem = bigram.generatedPoem
        tuple = evalPoem(bigram.bigramMap, poem, 5, .6)
        sumPercentIambic += tuple[0]
        sumPercentRhyme += tuple[1]
        averageSumBigramChoice += tuple[2]

    print "---------Evaluation----------"
    print "Number of poems generated: ", n
    print "Percent of lines that rhyme: ", float(sumPercentRhyme)/n
    print "Percent of lines that have iambicpentameter: ", float(sumPercentIambic)/n
    print "Average number of choices per bigram: ", float(averageSumBigramChoice)/n
    print "-----------------------------"
    n = input("Enter number of poems to generate and evaluate (0 to quit): ")
