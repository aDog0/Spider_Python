import requests
from bs4 import BeautifulSoup
import json
import urllib.request
import lxml
import re

#获取所有文章的链接
def geturls(key):
	keycode=urllib.request.quote(key)
	page=400
	urls=[]
	while page>=400 and page<572:
		url="http://api.search.sina.com.cn/?c=news&t=&q="+keycode+"&page=%s&stime=2017-01-26&etime=2018-01-28&sort=rel&highlight=1&num=10&ie=utf-8" % str(page)
		r=requests.get(url)
		js=json.loads(r.content)['result']['list']
		for js_ in js:
			if js_['url'] in urls:
				continue
			urls.append(js_['url'])
		page+=1
	return urls

#获取新闻信息
def getnews_info(url):
	r=requests.get(url)
	soup=BeautifulSoup(r.content,"lxml")
	try:
		#标题
		title=soup.find("h1",{"class":"main-title"}).text
	except Exception as e:
		title=soup.find("h1",{"id":"artibodyTitle"}).text
	
	try:
		#时间
		date=soup.find("div",{"class":"date-source"}).find("span",{"class":"date"}).text
	except Exception as e:
		date=soup.find("span",{"class":"time-source"}).text
		
	try:
		#发布源
		source=soup.find("div",{"class":"date-source"}).find("a").text
	except Exception as e:
		source=soup.find("span",{"class":"time-source"}).find("a").text
		
	try:
		#关键词
		keyws=soup.find("div",{"class":"keywords"}).find_all("a")
	except Exception as e:
		keyws=soup.find("div",{"class":"article-keywords"}).find_all("a")

	keywords=""
	for keyw in keyws:
		keywords+=keyw.text+","

	#文章url
	article_url=soup.find("meta",{"property":"og:url"}).get("content")

	try:
		#内容
		conts=soup.find("div",{"class":"article"}).find_all("p")
	except Exception as e:
		conts=soup.find("div",{"id":"artibody"}).find_all("p")
		
	contents=""
	for content in conts:
		contents+=content.text+"\n"
	
	result="标题："+title+"\n"+"时间："+date+"\n"+"发布源："+source+"\n"+"关键词："+keywords+"\n"+"文章url："+article_url+"\n"+"内容："+contents
	return result,title


#主函数
def spidernews():
	key="电信诈骗"
	urls=geturls(key)
	i=1941
	pathpat='[\*\|"]'
	for url in urls:
		try:
			results,title=getnews_info(url)
			title=re.sub(pathpat,"",title)
			f=open('C:\Application Soft\SinaNews\SinaNews_Spider\%s-%s.txt' % (str(i),title),'w',encoding='utf-8') 
			f.write(results)
			f.close()
			i+=1
		except Exception as e:
			fa=open('C:\Application Soft\SinaNews\\failed.txt','a',encoding='utf-8')
			fa.write(url+'\n')
			fa.close()

spidernews()
