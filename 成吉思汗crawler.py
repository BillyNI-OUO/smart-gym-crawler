import sys
import re
links=[]
with open('成吉思汗link.txt','r') as fp:
	lines=fp.readlines()
	for line in lines:
		links.append(line.split("\n")[0])
#for lin in link:
#	print(lin)
cid=[]
for link in links:
	try:
		cid.append(int(re.search(r":0x\w*", link).group()[1:], 16))
	except Exception as e:
		sys.stderr.write(str(e)+"\n")
for c in cid:
	print(c)
with open('成吉思汗_cid.txt', 'w') as fp:
	for i in cid:
		fp.write(str(i)+"\n")