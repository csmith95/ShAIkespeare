from BigramModel import BigramModel
from Database import Database

db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
print(bigram.generateConstrainedPoem())

scores = []
y = 1
n = -1
for i in xrange(10):
    prompt = "Did you like line %d of the poem? (y/n) " % i
    line_score = input(prompt)
    if (line_score == y):
        scores.append(1)
    elif (line_score == n):
        scores.append(-1)
    else:
        print("Please write 'y' if you liked the line, or 'n' if not.")
        i -= 1
print("scores: ", scores)
bigram.updateDirichlet(scores)
