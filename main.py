from BigramModel import BigramModel
from Database import Database
from pyrhyme.rhyme import rhymes_with
from pyrhyme.rhyme import rhymes

#examples of the two rhyme functions
# for word in rhymes_with('space'):
#     print word
# print(rhymes('space', 'lace'))

db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
print(bigram.generatePoem())
