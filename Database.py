import re, random
# from nltk.corpus import words

class Database:

  def __init__(self, filename):
  	self.corpus = []
  	startTag = r'CONTENT/'
  	endTag = r'/CONTENT'
  	startAgeTag = r'AGE/'
  	endAgeTag = r'/AGE'

  	with open(filename) as f:
  		text = re.sub(r'\n+', ' ', f.read())
  		text = re.sub(r'\s+', ' ', text)				# clean up whitespace
  		text = re.sub(r'\[.+?\]', '', text)				# strip [CHORUS] and other song tags
  		text = re.sub(r'[-_,\.;""\(\):]', '', text) 			# remove some non-alphanumeric chars
  		matches = re.findall(r'({})(.+?)({}).*?{}(.*?){}'.format(startAgeTag, endAgeTag, startTag, endTag), text)
		split_words = []
  		for m in matches:
  			if m[1] == 'Renaissance':
  				if random.randrange(1, 101) < 60: 
  					continue
			
			# for x in m[3].split():
				# x_lower = x.lower()
				# if x_lower in realWordsDict:
					# split_words.append(x_lower)
			# split_words = [x.lower() for x in m[3].split()]
			# split_words = m[3].split()
  			# self.corpus.append(split_words + ['EOF'])
			split_words.extend(m[3].split())
		for w in split_words:
			# print(w)
			w_lower = w.lower()
		# 	# if w_lower in realWordsDict: this takes too long!!
			self.corpus.append(w_lower)
		print("done with word splitting")
