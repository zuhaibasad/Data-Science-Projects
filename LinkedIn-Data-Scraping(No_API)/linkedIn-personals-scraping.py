from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time
import xlrd
import xlsxwriter

#excel file where website URL is placed from where to get email (if you preferr excel)
reading_file = xlrd.open_workbook("data.xlsx")
read_sheet = reading_file.sheet_by_name("Sheet0")

writing_file = xlsxwriter.Workbook('output.xlsx')
write_sheet = writing_file.add_worksheet()
bold = writing_file.add_format({'bold': True})

### Headers ###
write_sheet.write('A1', "Email", bold)
write_sheet.write('B1', "Sex", bold)
write_sheet.write('C1', "Location", bold)
write_sheet.write('D1', "Occupation & Company", bold)
write_sheet.write('E1', "LinkedIn-URL", bold)
write_sheet.write('F1', "Interests", bold)
###############

browser = webdriver.Firefox()
browser.get("https://www.linkedin.com")

username = browser.find_element_by_xpath('//*[@id="login-email"]')
password = browser.find_element_by_xpath('//*[@id="login-password"]')

username.send_keys("enter your email used for login here") #enter your username for facebook tologin
password.send_keys("password ")   	   #enter your password for facebook
browser.find_element_by_id('login-submit').click()


i = 2
## to start again and try https://www.spytox.com/people/search?email=zuhaibasad%40gmail.com
while i <= 9:
	email = read_sheet.cell(i,2).value
	write_sheet.write('A'+str(i), email)
	try:	
		if email:
			browser.get('https://www.linkedin.com/sales/gmail/profile/viewByEmail/'+email)
			x = browser.find_element_by_xpath("//*[@id='li-header']/div[1]/div/a")
			if x:
				profile_link = x.get_attribute('href')
				write_sheet.write('E'+str(i), profile_link)
				browser.get(profile_link)

				location = browser.find_element_by_xpath("/html/body/div[5]/div[5]/div[2]/div/div/div/div/div/div[1]/div[2]/section/div[3]/div[1]/h3")		  
				write_sheet.write('C'+str(i), location.text)
				ocuu_comp = browser.find_element_by_xpath("/html/body/div[5]/div[5]/div[2]/div/div/div/div/div/div[1]/div[2]/section/div[3]/div[1]/h2")
				write_sheet.write('D'+str(i), ocuu_comp.text)
				browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
				time.sleep(3)
				interests = browser.find_element_by_xpath("/html/body/div[5]/div[5]/div[2]/div/div/div/div/div/div[1]/div[3]/div[8]/div/section/ul")
				write_sheet.write('F'+str(i), interests.text)
				print i
		i=i+1
	except Exception as e:
		print e
		#print("Person not found!")
		i=i+1
		continue

browser.close()
writing_file.close()
