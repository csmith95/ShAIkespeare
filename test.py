import prosodic as p
# from pyrhyme.rhyme import rhymes_with
# from nltk.corpus import wordnet

# def syllableCount(line):
#     text = p.Text(line)
#     text.parse()
#     return len(text.syllables())
#
# def iambic(line, n):
#     w = 1
#     if abs(syllableCount(line) - n*2) >= 1:
#         return .1
#     t = p.Text(line)
#     for i, syl in enumerate(t.syllables()):
#         syl.feature()
#         if i%2 == 1:
#             if syl.feature('prom.stress') != 1.0: w*=.9
#         if i%2 == 0:
#             if syl.feature('prom.stress') != 0.0: w*=.9
#     # if w >= .6: return True
#     # return False
#     return w
#
# poem = ["Was this the face that launched a thousand see",
#         "But, soft! what light through yonder window breaks?",
#         "And I do love thee: therefore, go with me",
#         "Now is the winter of our discontent",
#         "Which would be planted newly with the time",
#         "As calling home our exiled friends abroad",
#         "So, thanks to all at once and to each one",
#         "abroad"]
