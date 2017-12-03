from BigramModel import BigramModel
from Database import Database

db = Database('poem_song_db')
# db2 = Database('test_books_db')
# print(db2.corpus)
bigram = BigramModel(db.corpus)
print(bigram.generateConstrainedPoem())