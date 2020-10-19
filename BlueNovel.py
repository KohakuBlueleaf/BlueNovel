from crawler import Qianbi,Wenku8

if __name__ == '__main__':
	url = input('請輸入網址: ')
	
	if url.find('https://www.wenku8.net/novel/')==0:
		loader = Wenku8()
	elif url.find('https://www.x23qb.com/book/')==0:
		loader = Qianbi()
	
	loader.download(url)