import re

class Database:

  def __init__(self, filename):
  	startTag = 'CONTENT/'
  	endTag = '/CONTENT'
  	with open(filename) as f:
  		text = re.sub(r'\s+', ' ', f.read())
  		text = re.sub(r'\[.+\]', '', text)
  		text = re.sub(r'[^a-zA-z\s\/]', '', text)
  		matches = re.findall(r'{}(.*?){}'.format(startTag, endTag), text)
  		self.corpus = [m.split() for m in matches]

    