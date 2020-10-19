import os,sys
from requests import get
from bs4 import BeautifulSoup as BS
from multiprocessing import Pool, freeze_support

itoa = lambda x:f'0{x}' if x<10 else str(x)


class Wenku8:
	@staticmethod
	def get_number(url):
		number = url.split('/')[4:-1]
		if len(number) == 1:
			number = '2/{}'.format(number[0])
		else:
			number = '/'.join(number)
		
		return number
	
	@staticmethod
	def get_content(url):
		html = get(url).content
		soup = BS(html,'html.parser')
		content = str(soup.find(id='content').text).replace('\xa0',' ').split('\r\n')
		return content[1:-1]
	
	@classmethod
	def download(cls,url):
		form = 'https://www.wenku8.net/novel/{}/{}'
		num = cls.get_number(url)
		html = get(url).content
		soup = BS(html, 'html.parser')
		
		title = soup.find(id='title').text
		tr = soup.find('table').findAll('tr')
		td = []
		for i in tr:
			td+=i.findAll('td')
		
		novel = {}
		now = ''
		j = 0
		for i in td:
			if i.get('class')==['vcss']:
				j+=1
				temp = f'{itoa(j)}'+i.text
				novel[temp] = []
				now = temp
			else:
				if i.text.strip():
					a = i.find('a')
					novel[now].append((a.text,form.format(num,a.get('href'))))
		
		path = f'./download/{title}/'
		if not os.path.isdir(path):
			os.mkdir(path)
		
		for volume, a in novel.items():
			pool = Pool(20)
			content = pool.map_async(cls.get_content, [i[1] for i in a])
			
			pool.close()
			pool.join()
			content.wait()
			content = content.get()

			out = ''
			for i in range(len(a)):
				chapter = a[i][0]
				print(chapter)
				out += f'\n第{i+1}章 {chapter}\n'
				out += '\n'.join(content[i])
				out += '\n'
			
			with open(path+f'{volume}.txt', 'w') as f:
				f.write(out)


class Qianbi:
	@staticmethod
	def get_content(url):
		content = []
		before = []
		i = 1
		while True:
			html = get(url+f'_{i}.html').content
			soup = BS(html,'html.parser')
			this = soup.find(id='TextContent').text.replace('\xa0',' ').split('\n')
			
			if this==before:
				return content
			else:
				before = this.copy()
			
			content += [i for i in this[4:-3] if i.strip()]	
			i += 1
	
	@classmethod
	def download(cls,url):
		form = 'https://www.x23qb.com{}'
		html = get(url).content
		soup = BS(html, 'html.parser')
		
		title = soup.find("div",{"class":'d_title'}).text
		title = title.strip().split()[0]
		print(title)
		li = soup.find(id='chapterList').findAll('li')
		a = [i.find('a') for i in li]
		chapters = [i.text.split(' ',1) for i in a]
		
		j = 0
		before = ''
		for i in chapters:
			if i[0] !=before:
				before = i[0]
				j+=1
			i[0] = itoa(j)+i[0]
		
		novel = {}
		now = ''
		j = 1
		for i in range(len(a)):
			href = form.format(a[i].get('href'))
			volume, chapter = chapters[i]
			
			if volume!=now:
				now = volume
				if now in novel:
					chapter = chapter.split(' ',1)
					if len(chapter)==1:
						pass
					else:
						volume += chapter[0]
						chapter = chapter[1]
				
			novel[volume] = novel.get(volume, []) + [(chapter,href)]
		
		path = f'./download/{title}/'
		if not os.path.isdir(path):
			os.mkdir(path)
				
		for volume, a in novel.items():
			pool = Pool(20)
			content = pool.map_async(cls.get_content, [i[1].rstrip('.html') for i in a])
			
			pool.close()
			pool.join()
			content.wait()
			content = content.get()

			out = ''
			for i in range(len(a)):
				chapter = a[i][0]
				print(chapter)
				out += f'\n第{i+1}章 {chapter}\n'
				out += '\n\n'.join(content[i])
				out += '\n'
			
			with open(path+f'{volume}.txt', 'w') as f:
				f.write(out)
			
