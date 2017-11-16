from BigramModel import BigramModel
from Database import Database
from pyrhyme.rhyme import rhymes_with


db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
print(bigram.generateConstrainedPoem())