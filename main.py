from BigramModel import BigramModel
from Database import Database

db = Database('poem_song_db')
bigram = BigramModel(db.corpus)
print(bigram.generateConstrainedPoem())
