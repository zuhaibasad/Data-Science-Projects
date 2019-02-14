import requests
import lxml.html
import urllib2
from bs4 import BeautifulSoup
import xlrd
import xlwt
import sys
import time
from xlutils.copy import copy

#excel file where website URL is placed from where to get email (if you preferr excel)
workbook = xlrd.open_workbook("Results_1__Pared_2.xlsx")
sheet = workbook.sheet_by_name("Sheet2")

#excel file to put collected data into.
writebook = xlrd.open_workbook("Results_1__Pared_2.xlsx")
w = copy(writebook)
sheet1= w.get_sheet(0)

sheet1.write(0,25, "Person's LinkedIn profile Url")

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

#Number of emails you want to extract data
i = 1
name = "x?!"
while i <= 28:
	try:
	       	name = name + sheet.cell(i,17).value
		employer = sheet.cell(i,21).value
		if name == "x?!":
			sheet1.write(i,3, "the Name of person in the excel file provided is missing!")
		else:
			name = name.replace("x?!", "")
			keywords = name +" "+ employer+" " + "linkedin"
			keywords = keywords.replace(" ","+")
			#here goes the your told webites URL
	 		url = "https://www.google.com/search?q="+keywords
			print url

			req = urllib2.Request(url, headers=headers)
			page = urllib2.urlopen(req)
			pageText = page.read()
			document = lxml.html.document_fromstring(pageText)

			#the query to find name, address or email from the page etc.
			link = document.xpath("(//*[@id='rso']/div/div/div[1]/div/div/h3/a/@href)[1]")
			#putting in excel file in a specific format
			print link
			sheet1.write(i,25, link[0])
		
		print(i)
		w.save('Results_1__Pared_2.xlsx')

	except UnicodeEncodeError:
		print i
		sys.exit()
	except IndexError:
		xp = [" "]
		sheet1.write(i,25, xp[0])
		w.save('Results_1__Pared_2.xlsx')
	except urllib2.HTTPError:
		time.sleep(3)
		print(i, "failed")
		continue
	name = "x?!"
	i=i+1

