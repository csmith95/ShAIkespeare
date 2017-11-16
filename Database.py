import re, random

class Database:

  def __init__(self, filename):
  	self.corpus = []
  	startTag = r'CONTENT/'
  	endTag = r'/CONTENT'
  	startAgeTag = r'AGE/'
  	endAgeTag = r'/AGE'
  	with open(filename) as f:
  		text = re.sub(r'\n+', ' NEWLINE ', f.read())	# encode newline as special token
  		text = re.sub(r'\s+', ' ', text)				# clean up whitespace
  		text = re.sub(r'\[.+?\]', '', text)				# strip [CHORUS] and other song tags
  		text = re.sub(r'[,\.]', '', text) 			# remove some non-alphanumeric chars
  		matches = re.findall(r'({})(.+?)({}).*?{}(.*?){}'.format(startAgeTag, endAgeTag, startTag, endTag), text)
  		for m in matches:
  			if m[1] == 'Renaissance':
  				if random.randrange(1, 101) < 60: 
  					continue
  			self.corpus.append(m[3].split() + ['EOF'])


    