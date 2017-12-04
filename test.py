import prosodic as p

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

line = "Was this the face that launched a thousand ships"
print iambic(line, 5)
