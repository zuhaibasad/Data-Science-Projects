from selenium import webdriver
import pandas as pd
import time

input_file = open("input.txt",'r')

x = input_file.readlines()
i=0
for each in x:
	x[i] = each.strip('\r\n')
	i = i+1
x = filter(bool, x)
driver = webdriver.Chrome()
count = 0
results = []
for each in x:
	driver.get("https://www.qichacha.com/search?key="+str(each))
	time.sleep(5)
	elem = driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/section/table/tbody/tr/td[2]/a')
	firm_link = elem.get_attribute('href')
	b_name = elem.text
	driver.get(firm_link)
	time.sleep(5)
	type_of = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[5]/td[2]").text
	raw_addr = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[10]/td[2]").text
	repre = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[1]/tbody/tr[2]/td[1]/div/div[1]/div[2]/a[1]/h2").text
	cap = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[1]/td[2]").text
	de = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[2]/td[4]").text
	de = de[0:4]+str(u'年')+de[5:7]+str(u'月')+de[8:10]+str(u'日')
	bt = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[9]/td[4]").text
	bt = bt[0:4]+str("年")+bt[5:7]+str("月")+bt[8:10]+str("日")+bt[10:17]+str("年")+bt[18:20]+str("月")+bt[21:23]+str("日")
	bs = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[11]/td[2]").text
	ad = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/section[2]/table[2]/tbody/tr[6]/td[2]").text
	yearad = ad[0:4]
	monthad = ad[5:7]
	dayad = ad[8:10]
	tup = (each, b_name, type_of, raw_addr,repre, cap, de, bt, bs, yearad, monthad, dayad)
	results.append(tup)
	count = count + 1

base = pd.DataFrame(results, columns=['Business Numbers','Business Name','Type of Business','Address','Legal Representative','Registered Capital','Date of Establishment','Business Term', 'Business Scope', 'Approval Year', 'Approval Month', 'Approval Day'])	
base.set_index('Business Numbers')
base.to_excel('output.xls',index=False)
