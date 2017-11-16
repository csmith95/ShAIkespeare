from BigramModel import BigramModel
from Database import Database
from pyrhyme.rhyme import rhymes_with


# words = rhymes_with('space')
# for word in words:
#     print word

db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
print(bigram.generatePoem())
