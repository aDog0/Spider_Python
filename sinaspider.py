# coding=utf-8
import requests
from bs4 import BeautifulSoup
import urllib
import time

header = {'user-agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}  # 设置代理头

# 这个函数通过key得到拼接好的url
def get_url(key):
    key = key.encode('gb2312')  # 需要将编码改成gb2312，然后再进行urlencode
    keycode = urllib.request.quote(key)  # url转义
    url = 'http://search.sina.com.cn/?q=' + keycode + '&range=all&c=news&sort=rel&page='  # 表示第一页，排序是相关排序
    return url

#获得搜索结果的数量
def get_nums(url):
    r = requests.get(url + str(1), headers=header)#首先请求搜索结果的第一个页
    print('url:', url+str(1))
    soup = BeautifulSoup(r.text, 'lxml')
    #print(r.text)
    context = soup.find('div', {'class': 'l_v2'}).text #这个div中内容类似"找到相关新闻41,245篇"
    print("context:%s" % context)
    num = ""
    for s in context:
        if s.isdigit():
            num += s
    return int(num)


count = 0

# 获取所有文章的链接
def get_urls(key):
    url = get_url(key)
    url_nums = get_nums(url)
    page_nums = url_nums / 20 + 1 #默认一页20篇
    print('结果%d个，一共%d' % (url_nums, page_nums))
    urls = []
    i = 1

    #while i < 150 :
    while i < page_nums:
        r = requests.get(url+str(i), headers=header)
        soup = BeautifulSoup(r.text, 'lxml')
        for s in soup.find_all('div', {'class': 'box-result'}): #每个搜索条目都是在一个class为box-result的div中
            result = s.a['href']
            if "slide" in result:   # slide是新闻网页类似幻灯片的情况
                continue
            if "video" in result:   #新闻内容是视频
                continue
            urls.append(result) #这个div中的a的href属性就是我们想要的

        i += 1
        print('目前到第%d页' % i)
    return urls


# 获取新闻信息
def getnews_info(url):
    r = requests.get(url, headers=header)
    time.sleep(1)
    r.encoding = 'utf-8' #将编码改成utf-8 ，这样不会出现乱码的情况
    soup = BeautifulSoup(r.text, "lxml")

    print("url:", url)
    # 标题
    title = soup.find("h1", {"class": "main-title"})
    if title is None:
        title = soup.find("h1", {"id": "artibodyTitle"})
    if title is None:
        title = soup.find("h1", {"id": "main_title"})
    if title is None:
        title = ""
    else:
        title = title.text
    print('标题：', title)

    # 日期
    date = soup.find("div", {"class": "date-source"})
    if date is None:
        date = soup.find("span", {'class': "time-source"})
    else:
        date = soup.find('span', {'class': 'date'})
    if date is None:
        date = soup.find('span', {'id': 'pub_date'})
    if date is None:
        date = ""
    else:
        date = date.text
    date = date.split("\n")[0]
    print('日期：', date)

    # 发布源
    source = soup.find("div", {"class": "date-source"})
    if source is None:
        source = soup.find("span", {'class': 'time-source'})
    if source is None:
        source = soup.find("span", {"id": "media-name"})
    if source is None:
        source = ""
    else:
        source = source.text
    if "\n" in source:
        source = source.split("\n")[2]

    print('发布源：', source)

    # 关键词
    keyws = soup.find("div", {"class": "keywords"})
    if keyws is None:
        keyws = soup.find("div", {"class": "article-keywords"})
        if keyws is None: #没有关键词，这直接返回空集
            keyws = []
        else:
            keyws = keyws.find_all("a")
    else:
        keyws = keyws.find_all("a")
    keywords = ""
    for keyw in keyws:
        keywords += keyw.text + ","

    # 文章url
    article_url = url

    # 内容
    conts = soup.find("div", {"class": "article"})
    if conts is None:
        conts = soup.find("div", {"class": "content"})
    if conts is None:
        conts = soup.find("div", {"id": "artibody"})
    if conts is not None:
        conts = conts.find_all("p")

    if conts is None:
        conts = []
    print("contes size:%d" % len(conts))
    contents = ""
    for content in conts:
        #print(content.text)
        contents += content.text + "\n"
    # print("contents size:%d" % len(contents))
    result = dict()
    result["title"] = title
    result["date"] = date
    result["source"] = source
    result["keywords"] = keywords
    result["url"] = article_url
    result["content"] = contents
    print(result)
    # result = "标题：" + title + "\n" + "时间：" + date + "\n" + "发布源：" + source + "\n" + "关键词："\
    #          + keywords + "\n" + "文章url：" + article_url + "\n" + "内容：" + contents
    # result += 80*"-"
    # result += "\n"
    #print(contents)

    return result


# 主函数
def spider_news():
    key = "电信诈骗"
    urls = get_urls(key)

    import pymysql
    db = pymysql.connect("192.168.1.221", "root", "501501501", "telecom")
    db.set_charset('utf8')  # mysql默认用的是latin-1的编码在有中文的时候出错，需要设置为utf-8
    for url in urls:
        result = getnews_info(url)
        if len(result["title"]) == 0 or len(result["date"]) == 0:
            continue
        global count
        count += 1
        print('count:%d' % count)
        cursor = db.cursor()
        sql = "insert into data_tbl (data_title, data_date, data_source, data_keywords, data_url, data_content) " \
              "values ('%s','%s','%s','%s','%s','%s');" % \
              (result["title"], result["date"], result["source"], result["keywords"], result["url"], result["content"])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as err:
            print("在Mysql执行时发生错误  ", err)
    db.close()


if __name__ == "__main__":

    spider_news()
