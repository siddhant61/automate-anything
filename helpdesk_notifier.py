import asyncio
from tabulate import tabulate
import htmltabletomd
from selenium import webdriver
from datetime import date
from datetime import datetime
import yaml
import numpy as np
import pandas as pd
import collections
from telegram import Bot
import texttable
import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from py_markdown_table.markdown_table import markdown_table
import markdown

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# conf = yaml.load(open('login_details.yml'))
# myEmail = conf['fb_user']['email']
# myPassword = conf['fb_user']['password']

myEmail = 'Siddhant.Gadamsetti@student.hpi.uni-potsdam.de'
myPassword = 'gylipity'

options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs",prefs)
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument("--headless")
driver = webdriver.Chrome()


def login(url, username, password):
   driver.get(url)

   username_field = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/form/div[1]/input')
   username_field.send_keys(username)
   password_field = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/form/div[2]/input')
   password_field.send_keys(password)

   # driver.find_element(By.ID,usernameId).send_keys(username)
   driver.find_element(By.CLASS_NAME, "btn--primary").click()
   driver.implicitly_wait(10)

   driver.get('https://helpdesk.openhpi.de/#ticket/view/all_open')

   con = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, 'content_permanent_TicketOverview')))

   page = con.find_element(By.CLASS_NAME, 'js-pager')
   pg = page.find_elements(By.CLASS_NAME, 'js-page')
   ticket = []
   time = []
   state = []
   owner = []

   if (len(pg)>0): #len(pg) is the number of pages
      for i in range(len(pg)):
         view = con.find_element(By.CLASS_NAME, 'js-pager')
         view.find_elements(By.CLASS_NAME, 'js-page')[i].click()
         data = con.find_element(By.CLASS_NAME, 'js-tableBody')
         count = data.find_elements(By.CLASS_NAME, 'item')
         for i in range(len(count)): #len(count) is the number of items in one page
            id = count[i].find_element(By.XPATH, f'//*[@id="content_permanent_TicketOverview"]/div[3]/div[2]/div[2]/div/table/tbody/tr[{i + 1}]/td[3]/a').text
            ti = count[i].find_element(By.CLASS_NAME, 'humanTimeFromNow').text
            st = count[i].find_elements(By.CLASS_NAME, 'user-popover')[1].text
            own = count[i].find_element(By.XPATH,
               f'//*[@id="content_permanent_TicketOverview"]/div[3]/div[2]/div[2]/div/table/tbody/tr[{i + 1}]/td[7]').text
            owner.append(own)
            state.append(st)
            time.append(ti)
            ticket.append(id)
   else:
      data = con.find_element(By.CLASS_NAME, 'js-tableBody')
      count = data.find_elements(By.CLASS_NAME, 'item')
      for i in range(len(count)):
         id1 = count[i].find_element(By.XPATH, f'//*[@id="content_permanent_TicketOverview"]/div[3]/div[2]/div[2]/div/table/tbody/tr[{i + 1}]/td[3]/a')
         elems = count[i].find_elements(By.CSS_SELECTOR, ".item [href]")
         id = [elem.get_attribute('href') for elem in elems]
         ti = count[i].find_element(By.CLASS_NAME, 'humanTimeFromNow').text
         st = count[i].find_elements(By.CLASS_NAME, 'user-popover')[1].text
         own = count[i].find_element(By.XPATH,
            f'//*[@id="content_permanent_TicketOverview"]/div[3]/div[2]/div[2]/div/table/tbody/tr[{i + 1}]/td[7]').text
         owner.append(own)
         state.append(st)
         time.append(ti)
         ticket.append(id[0])
   driver.close()
   dat1 = np.array([ticket, state, owner, time])
   set = np.array([ticket, state, owner, time])
   return (set, dat1)

def data(set_2):
   info = set_2
   for i in range(len(set_2[1])):
      if set_2[1][i] == '-':
         set_2[1][i] = 'Not Assigned'
      if set_2[3][i].__contains__('ago'):
         hr = [int(s) for s in set_2[3][i].split() if s.isdigit()]
         if len(hr) > 1:
            set_2[3][i] = str(hr[0]) + 'Hrs : ' + str(hr[1]) + 'Mins'
         else:
            if set_2[3][i].__contains__('hours'):
               set_2[3][i] = str(hr[0]) + 'Hrs'
            else:
               set_2[3][i] = str(hr[0]) + 'Mins'
   dat = {'Ticket': set_2[0],'Status' : set_2[2],'Owner' : set_2[1],'Time' : set_2[3]}
   df = pd.DataFrame(dat)
   df.transpose()
   now = datetime.now()
   df.to_csv(f'tickets_{now.strftime("%H")}_{date.today()}.csv', index=False)
   return(info)

def analysis(info):
   h6 = 0
   h12 = 0
   h24 = 0
   h48 = 0
   for i in range(len(info[3])):
      hr = [int(s) for s in info[3][i].split() if s.isdigit()]
      if info[1][i] == '-':
         info[1][i] = 'Not Assigned'
      if info[3][i].__contains__('ago'):
         if len(hr) > 1:
            if hr[0]<=6:
               h6 = h6 + 1
            if hr[0] > 6 and hr[0] <= 12:
               h12 = h12 + 1
            if hr[0] > 12 and hr[0] <= 24:
               h24 = h24 + 1
         else:
            if info[3][i].__contains__('hours'):
               if hr[0] <= 6:
                  h6 = h6 + 1
               if hr[0] > 6 and hr[0] <= 12:
                  h12 = h12 + 1
               if hr[0] > 12 and hr[0] <= 24:
                  h24 = h24 + 1
            if info[3][i].__contains__('minutes'):
               h6 = h6 + 1
      if info[3][i].__contains__('/'):
         h48 = h48+1
   elements_count = collections.Counter(info[1])
   # printing the element and the frequency
   elem = []
   freq = []
   for key, value in elements_count.items():
      elem.append(key)
      freq.append(value)

   now = datetime.now()
   table1 = texttable.Texttable()
   table1.set_deco(texttable.Texttable.HEADER)
   table1.set_cols_dtype(['t',  't',  't'])
   table1.set_cols_align(["l", "c", "r"])
   table1.add_rows([["Date", "Time", "Ticket(s)"],
                   [f"{date.today()}", f"{now.strftime('%H:%M')}", f"{len(info[0])}"]])

   table2 = texttable.Texttable()
   table2.set_deco(texttable.Texttable.HEADER)
   table2.set_cols_dtype(['t', 't'])
   table2.set_cols_align(["l", "r"])
   table2.add_rows([["Time Range", "Ticket(s)"],
                    ["Within 06 Hrs", f"{h6}"],
                    ["Within 12 Hrs", f"{h12}"],
                    ["Within 24 Hrs", f"{h24}"],
                    ["Within 48 Hrs", f"{h48}"]])

   table3 = texttable.Texttable()
   table3.set_deco(texttable.Texttable.HEADER)
   table3.set_cols_dtype(['t', 't'])
   table3.set_cols_align(["l", "r"])
   t3_head = ["Owner", "Ticket(s)"]
   t2_row = [["Time Range", "Ticket(s)"],
                    ["Within 06 Hrs", f"{h6}"],
                    ["Within 12 Hrs", f"{h12}"],
                    ["Within 24 Hrs", f"{h24}"],
                    ["Within 48 Hrs", f"{h48}"]]
   t3_row = []
   t3_row.append(t3_head)
   for i in range(len(elem)):
      t3_row.append([f"{elem[i]}", f"{freq[i]}"])
   table3.add_rows(t3_row)
   wid = [17, 10]
   table1.set_cols_width([10, 5, 9])
   table2.set_cols_width(wid)
   table3.set_cols_width(wid)
   print("=====Helpdesk Notification====", table1.draw(), table2.draw(), table3.draw(), sep='\n\n')
   msg = f"""===Helpdesk Notification===\n\n{table1.draw()}\n\n{table2.draw()}\n\n{table3.draw()}"""

   asyncio.run(send(msg, '-1001250348978', '1345063220:AAGhn4GHEJ-nlXlfbpBSDiLUyspK-kZPwwQ'))

async def send(msg, chat_id, token):
   bot = Bot(token)
   text = f"```\n{msg}\n```"
   await bot.send_message(chat_id=chat_id, text=text, parse_mode='MarkdownV2')
   print("\nNotification sent.")

if __name__ == '__main__':
   info = login("https://helpdesk.openhpi.de/#login", myEmail, myPassword)
   data(info[0])
   analysis(info[1])


   time = datetime.now()
   emailfrom = "openhpi.helpdesk.notifier@gmail.com"
   emailto = "openhpi.helpdesk.notifier@gmail.com"
   fileToSend = f'tickets_{time.strftime("%H")}_{date.today()}.csv'
   username = "openhpi.helpdesk.notifier@gmail.com"
   password = "vrnfpwxslcamzkmg"

   msg = MIMEMultipart()
   msg["From"] = emailfrom
   msg["To"] = emailto
   msg["Subject"] = f'Open tickets at {time.strftime("%H")} Uhr on {date.today()}'
   msg.preamble = "Please find the attachment"

   ctype, encoding = mimetypes.guess_type(fileToSend)
   if ctype is None or encoding is not None:
       ctype = "application/octet-stream"

   maintype, subtype = ctype.split("/", 1)

   if maintype == "text":
       fp = open(fileToSend)
       # Note: we should handle calculating the charset
       attachment = MIMEText(fp.read(), _subtype=subtype)
       fp.close()
   elif maintype == "image":
       fp = open(fileToSend, "rb")
       attachment = MIMEImage(fp.read(), _subtype=subtype)
       fp.close()
   elif maintype == "audio":
       fp = open(fileToSend, "rb")
       attachment = MIMEAudio(fp.read(), _subtype=subtype)
       fp.close()
   else:
       fp = open(fileToSend, "rb")
       attachment = MIMEBase(maintype, subtype)
       attachment.set_payload(fp.read())
       fp.close()
       encoders.encode_base64(attachment)
   attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
   msg.attach(attachment)

   server = smtplib.SMTP("smtp.gmail.com:587")
   server.ehlo()
   server.starttls()
   server.login(username, password)
   server.sendmail(emailfrom, emailto, msg.as_string())
   server.quit()
   os.remove(f'tickets_{time.strftime("%H")}_{date.today()}.csv')




