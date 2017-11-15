import re
match = re.match(r"^.*\['(.*)'\].*$",str)

class Database:

  def __init__(self, filename):
  	startTag = '"CONTENT/'
  	endTag = '/CONTENT"'
  	with open(filename) as f:
  		text = myfile.read().replace('\n', '')
  		matches = re.findall(r"^.*startTag'(.*)'endTag.*$", text)
        for m in matches:
            print(m)
    