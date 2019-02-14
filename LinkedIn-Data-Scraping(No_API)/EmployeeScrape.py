import requests
import lxml.html
import urllib2
from bs4 import BeautifulSoup
import xlrd
import xlwt
import sys
import time
import random as rd
from xlutils.copy import copy

#excel file where website URL is placed from where to get email (if you preferr excel)
workbook = xlrd.open_workbook("Results_1__Pared_2.xlsx")
sheet = workbook.sheet_by_name("Sheet2")

#excel file to put collected data into.
writebook = xlrd.open_workbook("Results_1__Pared_2.xlsx")
w = copy(writebook)
sheet1= w.get_sheet(0)

sheet1.write(0,23, "Employer's Twitter Handle")
sheet1.write(0,24, "Employer's Twitter Page Url")

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

#Number of emails you want to extract data 
i = 1
while i <= 28:
	try:
	       	name = sheet.cell(i,21).value
		keywords = name + " official twitter.com"
		keywords = keywords.replace(" ","+")
		#here goes the your told webites URL
 		url = "https://www.google.com/search?q="+keywords
		print url

		req = urllib2.Request(url, headers=headers)
		page = urllib2.urlopen(req)
		pageText = page.read()
		document = lxml.html.document_fromstring(pageText)

		#the query to find name, address or email from the page etc.
		handle = document.xpath("(//*[@id='rso']/div/div/div[1]/div/div/h3/a/text() )[1]")
		link = document.xpath("(//*[@id='rso']/div/div/div[1]/div/div/h3/a/@href)[1]")
		if handle == [] or link == []:
			keywords2 = name + " twitter"
			keywords2 = keywords2.replace(" ","+")
			url = "https://www.google.com/search?q="+keywords2
			print url
			req = urllib2.Request(url, headers=headers)
			page = urllib2.urlopen(req)
			pageText = page.read()
			document = lxml.html.document_fromstring(pageText)
			#the query to find name, address or email from the page etc.
			handle = document.xpath("(//*[@id='rso']/div/div/div[1]/div/div/h3/a/text() )[1]")
			link = document.xpath("(//*[@id='rso']/div/div/div[1]/div/div/h3/a/@href)[1]")
		#putting in excel file in a specific format
		print handle[0]
		sheet1.write(i,23, handle[0])
		sheet1.write(i,24, link[0])
		print(i)
		w.save('Results_1__Pared_2.xlsx')
	except UnicodeEncodeError:
		print i
		sys.exit()
	except IndexError:
		xp = [" "]
		sheet1.write(i,2, xp[0])
		w.save('Results_1__Pared_2.xlsx')
	except urllib2.HTTPError:
		time.sleep(rd.randrange(3,20) )
		print(i, "failed")
		continue
	i=i+1

