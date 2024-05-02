import requests
from bs4 import BeautifulSoup
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from pytz import timezone
import datetime
import mysql.connector
from scrapy.http import HtmlResponse
import sender
from gooey.python_bindings.gooey_decorator import Gooey
from gooey.python_bindings.gooey_parser import GooeyParser
from random import randint
from gooey.python_bindings.gooey_decorator import Gooey
from gooey.python_bindings.gooey_parser import GooeyParser
import re
import ctypes
import logging
from datetime import timedelta
from datetime import datetime as DT
import os
from os import mkdir,makedirs
from datetime import datetime as DT
import sys

today = datetime.datetime.now()

def logger_portal(client_name,portalname,mainclient):
    """This Function is used to Setup logging"""
    path=f"BACKUP//{portalname}//{mainclient}//{client_name}//" #Check path exist
    if not os.path.exists(path):os.makedirs(path)
    LOG_FILENAME = path + '{}'.format(client_name,) + today.strftime('%d-%m-%Y-%H-%M-%S.log')
    logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
    logging.getLogger().propagate=False

photo = '375' #ecesis photographer
auto = '0' #is the order auto accepted '0'-Not auto accepted
#orderid = '1'#dummy value



                 
removeHTML = re.compile('<.*?>')#remove HTML tags from address string
non_decimal = re.compile(r'[^\d.]+')#remove alphabets from price string


def maipping_mailsend(p,address,portal,client,ordertype,to,subject):
    try:
        ordertpe_message = 'We are unable to identify the {} for the following order\n\n Address: {} \n Portal: {} \n Client: {} \n Order Type {}'.format(p,address,portal,client,ordertype)
        mail = sender.Mail('smtp.gmail.com','notifications@bpoacceptor.com','$oft@ece2021', 465, use_ssl=True,fromaddr='notifications@bpoacceptor.com')
        mail.send_message(subject=subject, to=to,body=ordertpe_message)
        #print('Mapping issue reported')
        logging.info('Mapping issue reported')
    except Exception as e:
        #(e)
        logging.error(e)
        
def updateCondition(date,subclient,mainclient,AssetType,address,duedate,portal,price,condition):
        #creates a new entry in order updation DB with order special instructions corresponding to the order extracted from Bpofulfillment portal
        #if the order is already available in the DB with date in range of 6 days from today then only the condition field is updated(If it is empty),if the condition field is not empty then no changes are made
        prevdate1 = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%m/%d/%Y')
        prevdate2 = (datetime.datetime.now() - datetime.timedelta(2)).strftime('%m/%d/%Y') 
        prevdate3 = (datetime.datetime.now() - datetime.timedelta(3)).strftime('%m/%d/%Y') 
        prevdate4 = (datetime.datetime.now() - datetime.timedelta(4)).strftime('%m/%d/%Y') 
        prevdate5 = (datetime.datetime.now() - datetime.timedelta(5)).strftime('%m/%d/%Y') 
        prevdate6 = (datetime.datetime.now() - datetime.timedelta(6)).strftime('%m/%d/%Y')
        tommorrow = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%m/%d/%Y')
        date=datetime.datetime.now().strftime('%m/%d/%Y')

        #connection to our order updation DB
        localconn = mysql.connector.connect(host='34.70.96.52',database='order_updation',user='order',password='acceptance',autocommit=True,buffered=True)
        if localconn.is_connected():
                #('Connected to MySQL database...')
                logging.info('Connected to MySQL database...')
                #('Creating new entry with condition...')
                logging.info('Creating new entry with condition...')
                #### CHECKING DUPLICATES#####
                local_cursor = localconn.cursor()
                #("SELECT `address` FROM `orders` WHERE `address` = '{}' AND `client` = '{}' AND `portal` = '{}' AND `date` IN ('{}','{}')".format(address,mainclient,portal,date,prevdate1))
                local_cursor.execute("SELECT `address` FROM `orders` WHERE `address` = '{}' AND `client` = '{}' AND `portal` = '{}'".format(address,mainclient,portal,date,prevdate1))
                logging.info("SELECT `address` FROM `orders` WHERE `address` = '{}' AND `client` = '{}' AND `portal` = '{}'".format(address,mainclient,portal,date,prevdate1))
                count=len(local_cursor.fetchall())
                if(count==0):
                    #("INSERT INTO `orders`(`date`, `client`, `subclient`, `address`, `duedate`, `portal`, `price`, `type`, `time`, `pic`, `pastdue`,`pastdate`,`status`, `condition`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(date,mainclient,subclient,address,duedate,portal,price,AssetType, datetime.datetime.now(),"No","No","NA","Neworder",condition))
                    local_cursor.execute("INSERT INTO `orders`(`date`, `client`, `subclient`, `address`, `duedate`, `portal`, `price`, `type`, `time`, `pic`, `pastdue`,`pastdate`,`status`, `condition`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(date,mainclient,subclient,address,duedate,portal,price,AssetType, datetime.datetime.now(),"No","No","NA","Neworder",condition))
                    logging.info("INSERT INTO `orders`(`date`, `client`, `subclient`, `address`, `duedate`, `portal`, `price`, `type`, `time`, `pic`, `pastdue`,`pastdate`,`status`, `condition`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(date,mainclient,subclient,address,duedate,portal,price,AssetType, datetime.datetime.now(),"No","No","NA","Neworder",condition))
                    #("New order inserted")
                    logging.info("New order inserted")
                    local_cursor.close()
                    localconn.close()
                else:
                    #("Order already inserted into DB-----Duplicate")
                    logging.info("Order already inserted into DB-----Duplicate")
                    local_cursor.close()
                    localconn.close()

        else:
                #('DB Connection Failed')
                logging.info('DB Connection Failed')
                localconn.close()


def date_to_IST(due):#convert duedate and time to IST ==> Provide duedate - <due> in MM/DD/YYYY H:M:S format
    try:
        ISTdue = datetime.datetime.strptime(due, "%m/%d/%Y %H:%M:%S") + datetime.timedelta(hours=9,minutes=30)#parse datetime string to datetime object and add required time to it
        ISTdue = datetime.datetime.strftime(ISTdue, "%m/%d/%Y %H:%M:%S")#format datetime object to string
        #('IST Due Date',ISTdue)
        logging.info('IST Due Date {}'.format(ISTdue))
        return ISTdue
    except Exception as e:
        logging.info('Failed to convert duedate ==> {due} to IST')
        
#=====================================================================================
    

def validate_dateTime(date_text): #function checks if due time is present in datetime string and appends 17:00:00 if no time is present #TFS default Time 5 PM
    try:
        datetime.datetime.strptime(date_text, "%m/%d/%Y %H:%M:%S")
        return date_text
    except ValueError:
        #("Incorrect date format, should be MM/DD/YYYY H:M:S")
        logging.info("Incorrect date format, should be MM/DD/YYYY H:M:S")
        #("Appending time to date")
        logging.info("Appending time to date")
        date_text = f'{date_text} 17:00:00'  
        return date_text


def updateATS(zadd,mainclient,orderid,due,adrs,typ,portId,clientId,price,instruction,portal,client):
    try:
        #("Order Type",typ)
        logging.info("Order Type:{}".format(typ))
        due = validate_dateTime(due)
        #(due)
        ISTdue = date_to_IST(due)

        #("Due Date",due)
        logging.info("Due Date:{}".format(due))
        if not price: price="0"
        
        typ=typ.strip()
        
        
        #----------------------------------fetchinb from db
        
        # conn = mysql.connector.connect(host="34.70.96.52",database="order_updation",user="order",password="acceptance",buffered=True)
        # cursor = conn.cursor()
        # cursor.execute("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(typ))
        # #("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(typ))
        # if(cursor.rowcount>0):
        #     typId = cursor.fetchone()[0]
        #     #(typId)
        #     #("Order Type --{}-- Found".format(typ))
        # else:
        #     #("Order Type --{}--  Not Found".format(typ))
        #     logging.info("Order Type --{}--  Not Found".format(typ))
        #     #("Using Default Type -- 7")
        #     logging.info("Using Default Type -- 7")
        #     typId = None  
        # cursor.close()
        # conn.close()
        ordertype_json = 'S:\Portal Order Updation App script\order_type.json'
        with open(ordertype_json, 'r') as json_file:
            data_type = json.load(json_file)
            for entry in data_type:
                    filedtype_values = entry['filedtype']
                    type_value =entry['values']
                    terms = filedtype_values.split(',')
                    for value in terms : 
                        if value == typ:
                            #("ordertype match found from json")
                            logging.info("ordertype match found from json")
                            for values in type_value:    
                                typId=values.get('typeid') 
                                if typId is not None:
                                    #('typId:', typId)
                                    break
                                else:
                                    #("typid not found") 
                                    logging.info("typid not found") 
                            break                    
                        else:
                            #("Order Type --{}--  Not Found".format(typ))
                            logging.info("Order Type --{}--  Not Found".format(typ))
                            #("Using Default Type -- 7")
                            logging.info("Using Default Type -- 7")
                            typId = None  
                    if typId == None:
                       logging.info("Check next set")
                    else:
                        break
            
            #(typId)
                
        adrs = removeHTML.sub('', adrs)
        
        adrs = re.sub('\s+', ' ', adrs).strip()
        address_copy = adrs   
        adrs = adrs.replace(",", " ").replace("  ", " ").replace(" ,", " ").replace("  ", " ").replace(" ,", " ").replace(", ", " ")
        adrs = re.sub('\s+', ' ', adrs).strip()
        
        trimsubj="" #trimsubj --> remove 4 digit extension to zipcode from address if present,this will be passed as subchk
        n = adrs.split(" ")
        r = n[-1].split("-")
        r[0] = str(r[0]).replace(",", "")
        n[-1] = r[0]
        for i in range(0,len(n)): trimsubj = trimsubj + ' '+ n[i]
        
        trimsubj = trimsubj.strip()

        zipcode = n[-1].split("-")
        zipcode = str(zipcode[0]).replace(",", "").strip()

        if len(zipcode) > 5 or len(zipcode)< 3 or not zipcode.isdigit(): zipcode=None
        else: zipcode = zipcode.zfill(5) #add leading zeroes to make zipcode 5 digit,incase of 3 or 4 digit zipcodes

        addressTrm = adrs.replace("~", "   ")
        subchk = trimsubj.replace("~", "   ")


        price = non_decimal.sub('', str(price)).strip()
        #("Order Price",price)
        logging.info("Order Price:{}".format(price))

        ############checking ELIZABETH NY OR NJ#############
        #("CHECKING WHETHER ORDER ACCEPTED FOR MATTHEW-ELIZABETH NY OR MATTHEW-ELIZABETH NJ............")
        logging.info("CHECKING WHETHER ORDER ACCEPTED FOR MATTHEW-ELIZABETH NY OR MATTHEW-ELIZABETH NJ............")
        #(clientId)
        logging.info(clientId)
        if clientId=="10742" or clientId=="10743":
                state=adrs.split()[-2]
                #('STATE',state)
                logging.info(state)
                #("CHECKING STATE (NY or NJ)")
                logging.info("CHECKING STATE (NY or NJ)")
                if state=="NY":
                    clientId=10742
                elif state=="NJ":
                    clientId=10743
                else:
                    #("CHECK THE ORDER...........")
                    logging.info("CHECK THE ORDER...........")
        ###################################################################################
                    
        if typId and zipcode and clientId and portId:
                #('Updating Order Details to TFS..........')
                logging.info('Updating Order Details to TFS..........')
                session = requests.Session()
                condition="Average"
                rentalvalue=0
                #instruction="No instructions Found"
                inputData = "{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~".format(orderid,due,addressTrm,typId,portId,photo,clientId,price,zipcode,auto,subchk,address_copy,ISTdue,condition,rentalvalue)
                instruction="{}".format(instruction)
                splinstruction="We are not able to update the instruction. Please check the portal."
                #(inputData)
                logging.info('inputData : {}'.format(inputData))
                payload={
                     "clientId":clientId,
                     "procData":inputData,
                     "instructions":instruction,
                     "splInstructions":splinstruction
                    }
                #(payload)
                # url="http://13.200.17.36/ecesisapp/ats/Home/AddOrder"
                url="https://bpotrackers.com/ecesisapp/ats/Home/AddOrder"
                try:
                        response = session.post(url,data=payload)
                except:
                        session = requests.Session()
                        response = session.post(url,data=payload)
                #(response.text)
                resx=response.text
                logging.info('response: {}'.format(resx))
                if 'Success' not in resx:
                        #('Updation Failed..........')
                        logging.info('Updation Failed..........')
                else:
                        #('Successfully updated the order')
                        logging.info('Successfully updated the order')
                        ######################################################################
                        today=DT.now
                        year1=today().strftime('%Y')
                        month=today().strftime('%B')
                        currentdate=today().strftime('%m-%d-%Y')
                        #(currentdate)       
                        logging.info("Currentdate {}".format(currentdate))
                        def foldercreation():        
                            folder="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient+"//"+zadd
                            os.makedirs(folder)
                            #("folder created")
                            logging.info("folder created")
                        if zadd.__contains__('#') or zadd.__contains__('Union') or zadd.__contains__('UNION') or zadd.__contains__('APT') or zadd.__contains__('apt'):
                            foldercreation()
                        else:
                            trial=zadd.replace(",","")
                            trial=trial.strip()
                            #("replaced trial:",trial)
                            trial=trial.split(" ")           
                            zip=trial[-1]   
                            #("folderzip:",zip)
                            logging.info(zip)
                            trial=trial[:2]
                            x=" ".join(trial)
                            trial=x.lower()    
                            #("foldertrial:",trial)   
                            logging.info(trial)      
                            path="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient
                            #(os.listdir(path))
                            logging.info(os.listdir(path))
                            addfolders=os.listdir(path)
                            for i in addfolders:
                                oldaddress=i
                                i=i.replace(",","")
                                i=i.split(" ")
                                zippro=i[-1]   
                                typeofzip=zippro.isdigit()          
                                list=i[:2]
                                x=" ".join(list)
                                listadd=x.lower()
                                #("listadd=",listadd)
                                #("zippro:",zippro)
                                #("i=",i)
                                if trial==listadd and zip==zippro:
                                    old="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient+"//"+oldaddress
                                    new="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient+"//"+zadd
                                    os.rename(old,new)
                                    #("Folder renamed")
                                    logging.info("Folder renamed")
                                    break
                                elif trial==listadd and typeofzip==False:
                                    old="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient+"//"+oldaddress
                                    new="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient+"//"+zadd
                                    os.rename(old,new)
                                    #("Folder renamed")
                                    logging.info("Folder renamed")
                                    break  
                                else:
                                    #("match not found moving to next address") 
                                    logging.info("match not found moving to next address")                     

                            #(addfolders.__contains__(zadd))
                            try:
                                if addfolders.__contains__(zadd)==False:
                                    foldercreation()
                                    logging.info("Folder created")
                                else:
                                    #("no need to create folder")
                                    logging.info("no need to create folder")
                            except Exception as e:
                                logging.info(e)
            #####################################################################
        else:
                if not clientId:
                    #('Client Not Active or Unable to Map Client!!')
                    logging.info('Client Not Active or Unable to Map Client!!')
                    if client!="Sharyn" and client!="Sharyn Sharyn" and client!="Sharyn Jenny" and client!="Sharyn Matt" and client!="Matthew Daw" and client!="Sharyn-Sharyn" and client!="Sharyn-Jenny" and client!="Sharyn-Matt":
                        maipping_mailsend('clientname',address_copy,portal,client,typ,'teamsoftware@ecesistech.com','Mapping Failed.... Clientname!')

                if not zipcode:
                    #('Invalid Zipcode!!')
                    logging.info('Invalid Zipcode!!')
                if not typId:
                    #('Unable to map order Type -- {}'.format(typ))
                    logging.info('Unable to map order Type -- {}'.format(typ))
                    maipping_mailsend('ordertype',address_copy,portal,client,typ,'mapping@ecesistech.com','Mapping Failed.... Order Type!')
                if not portId:
                    #('Unable to map portakl!!')
                    logging.info('Unable to map portakl!!')
    except Exception as ex:
        #(ex)
        logging.info(f"Exception in updateATS: {ex}")

##############################################
def zillowfunc(folderadd):        
                    portaladdress = re.sub('\s+', ' ', folderadd).strip()
                    #(portaladdress)
                    logging.info("Org Address: {}".format(portaladdress))
                    zadd=folderadd
                    return zadd
                    '''headers = {
                    'authority': 'www.zillow.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://www.zillow.com/?utm_medium=cpc&utm_source=google&utm_content=1471764169|65545421228|kwd-570802407|603457706088|&semQue=null&gclid=Cj0KCQiAvqGcBhCJARIsAFQ5ke7rTk7RocXIajKTxmwHqUem5wp2SK8MNa7zoXF8uTE0ppY1lLn4JW8aArpKEALw_wcB',
                    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    }
                    zilladdress=folderadd.replace(',','')
                    zilladdress=zilladdress.replace(' ','-')
                    #(zilladdress)
                    logging.info('Zaddress1 : {}'.format(zilladdress))

                    url='https://www.zillow.com/homes/{}_rb/'.format(zilladdress)
            
                    response = requests.get(url,headers=headers)
                    response =response.text
                    response = HtmlResponse(url="my HTML string", body=response, encoding='utf-8')
                    zadd=response.xpath('/html/head/title/text()').extract_first()
                    #("portaladdress",portaladdress)
                    logging.info('portaladdress : {}'.format(portaladdress))

                    #(zadd)
                    logging.info('Zillowaddress1 : {}'.format(zadd))
            

                    if zadd == None or zadd=='Access to this page has been denied':
                        zadd=folderadd                         
                    zadd=zadd.split('| Zillow')[0]
                    zadd=zadd.split('- Apartments for Rent')[0]
                    zadd=zadd.split('| MLS')[0]
                    #(zadd)

                    zadd1=zadd.split(' ')[-1]
                    subadd=zadd.split(' ')[:-1]
                    subadd=" ".join(subadd)
                    #("subadd:",subadd)
                    if zadd1.__contains__("-"):
                        zadd1=zadd1.split('-')[0]
                        zadd= subadd+ " "+zadd1
                        #(zadd)
                    logging.info('Zillowaddress : {}'.format(zadd))
                    return zadd'''
            ###################################################################

def check(mainclient,session, resp, Mainclient, Subclient, portal, cid, ats_client_id, ats_portal_id,link):
        client=Mainclient+'-'+Subclient
        #link contains the base link
        if 'You are logged in' in resp.text:
            url = link+"/Orders/PendingOrders"
            data = {
                '_search': 'false',
                'nd': '1563002911995',
                'rows': '-1',
                'page': '1',
                'sidx': '',
                'sord':'asc'
                    }
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': link+'/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'
                    }
            response1=session.get(url, data=data,headers=headers)
            response1=json.loads(response1.text)
            details=response1['rows']
            #('Orders in progress: {}'.format(len(details)))
            logging.info('Orders in progress: {}'.format(len(details)))
            for o in details:
                try:
                    address= '{} {} {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                    folderadd= '{}, {}, {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                    #(folderadd)
                    logging.info(folderadd)
                    # address_value=zillowfunc(folderadd) ###calling function to get the zillow address
                    address_value=folderadd
                    orderid= o['OrderID']
                    AssetType= o['Product']
                    Fee=o['VendorFee']
                    duedate=o['DueDate']
                    #('Due date from portal is :', duedate)
                    logging.info('Due date from portal is :'.format(duedate))
                    due=duedate.replace('/Date(','').replace(')/','')
                    due=int(due[:-3])
                    duedate=datetime.datetime.fromtimestamp(due, tz=timezone('EST')).strftime("%#m/%#d/%Y") #convert unix time stamp to EST date(without zero padding)
                    #('Converted Due date from portal is :', duedate)
                    logging.info('Converted Due date from portal is :'.format(duedate))
                    orderitemid=o['OrderItemID']
                    engagementDocumentId=o['EngagementDocumentID']
                    #(orderid,address,AssetType,Fee,duedate,orderitemid)
                    logging.info(orderid,address,AssetType,Fee,duedate,orderitemid)
                    pendordersurl=link+"/Orders/"+str(orderid)+"/Items/"+str(orderitemid)+"/Documents/"+str(engagementDocumentId)
                    pendingordersurl =session.get(pendordersurl)
                    #("++++====")
                    #(pendingordersurl.text)                    
                    tresp1 = HtmlResponse(url="my HTML string", body=(pendingordersurl.text).replace("', '","").replace("&nbsp;","").replace("\t","").replace("\r\n","").replace("Loading....",""), encoding='utf-8')
                    res1=tresp1.text
                    try:
                        instruction=str(res1).split('INSTRUCTIONS')[1].split('STATE MANAGEMENT LICENSE:')[0]
                        instruction=re.sub('<.*?>','',instruction)                        
                        instruction=str(instruction)
                    except Exception as E:
                        #("Exception in instruction is",E)
                        instruction="We are not able to update the instruction. Please check the portal."
                    #('instruction',instruction)
                    logging.info('instruction: {}'.format(instruction))
                    updateATS(address_value,mainclient,orderid,duedate,address,AssetType,ats_portal_id,ats_client_id,Fee,instruction,portal,client)
                    #######UPDATING ORDER DETAILS TO DB#########
                    if portal == 'CA':
                        condition='Average'
                        try:
                            updateCondition(time.strftime("%m/%d/%Y"),Subclient,Mainclient,AssetType,address,duedate,portal,Fee,condition)#add this order to our DB
                        except Exception as e:
                            #("Could not update order to DB")
                            logging.info("Could not update order to DB")
                            #(e)
                            logging.info(e)
             
                except Exception as ex:
                    #('exception here')
                    logging.info('exception here')
                    #(ex)
                    logging.info(ex)
            
        else:
            url = "http://192.168.2.95/uporder/uppython.php?$cid={}".format(cid)
            r = requests.get(url)
            #('Bad Password')
            logging.info('Bad Password')

#---------------------------------------------------------------------------------------#
     



def login_toportal(username,password,session):
    link = "https://swbcls-vendors.clearvalueconsulting.com"
    try:
        # session = requests.session()
        # #(session)
        url='https://swbcls-vendors.clearvalueconsulting.com/Account/Logout'
        headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',                
                    'Host': 'swbcls-vendors.clearvalueconsulting.com',
                    'Referer': 'https://swbcls-vendors.clearvalueconsulting.com/Account/Login?ReturnUrl=%2fAccount%2fLogout',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'

                }
        resp = session.get(url,headers=headers)
        #(resp)
        soup = BeautifulSoup(resp.content, 'html.parser')
        tokken = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
        #(tokken)
        url = link+"/Account/Login?ReturnUrl=%2f"
        data = {
                '__RequestVerificationToken':tokken,
                'Username':username,
                'Password':password,
                'singlebutton':''
        }
        headers = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Content-Length': '66',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Host': link.replace("https://",""),
                    'Origin': link,
                    'Referer': link+'/Account/Login?ReturnUrl=%2f',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36ari/537.36'
                    }
        
        resp = session.post(url, data=data,headers=headers)
        return session,resp,link

    except Exception as e:
        logging.info(e)
  
def checkproxy_country(username,password,ip_address):
        session=requests.session()
        if '9000' in ip_address:
            proxies = {'http': 'http://{}'.format(ip_address),
                   'https': 'http://{}'.format(ip_address)
                   }
            ip_address=ip_address.split(':')[0]
        session.proxies.update(proxies)
        ip_test_url1="https://customer.api.drift.com/geo/v2"
        ipapify = session.get(ip_test_url1, proxies=proxies)
        ipadress=json.loads(ipapify.text)['ip']
        country=json.loads(ipapify.text)['country']
        #(country)
        logging.info(f"session IP {ipadress}")
        logging.info(f"Database IP {ip_address}")
        #(f"session IP {ipadress}")
        #(f"Database IP {ip_address}")
        if ip_address == ipadress: # Cross checking IP in DB with current session IP after updating proxy with Luminati
                #(f"Database IP matched with the session IP {ipadress}")
                logging.info(f"Database IP matched with the session IP {ipadress}")
                if country == "US": # Just make sure login from USA
                        #('Country identified as USA')
                        logging.info('Country identified as USA')
                        #('Try to login and update orders if any')
                        logging.info('Try to login and update orders if any')
                        return country,session
        else:
            #('IP not matching..')
            logging.info('IP not matching..')
            return 

#--------------------------Main Function-------------------------------------------------# 
def Query_JSON(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        cid = sys.argv[1]
        cid=int(cid)
        # cid = 7323
        filtered_data = [entry for entry in data if entry.get("filedtype") == cid]
        #(filtered_data)
    for value in filtered_data:
        for values in value['values']:
            mainclient = values.get('mainclient')
            subclient = values.get('subclient')
            portal = values.get('portal')
            username = values.get('username')
            password = values.get('password')
            credstatus = values.get('credstatus')
            ordercheckstatus = values.get('ordercheckstatus')
            ats_client_id = values.get('ats_client_id')
            ats_portal_id = values.get('ats_portal_id')
            ip_address = values.get('ip_address')

            #('Fetching details from JSON file...')
            #('CID:', cid)
            #('Mainclient:', mainclient)
            #('Subclient:', subclient)
            #('Portal:', portal)
            #('Username:', username)
            #('Password:', password)
            #('Credstatus:', credstatus)
            #('Ordercheckstatus:', ordercheckstatus)
            #('ATS Client ID:', ats_client_id)
            #('ip_address:', ip_address)
            ctypes.windll.kernel32.SetConsoleTitleW(f"{subclient}-SWBC")
            logger_portal(subclient,portal,mainclient)
            headers={}#sending headers to prevent login denied ORSS issue
            if credstatus == 'Active':                            
                            #('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                            logging.info('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                            ###################################################################################
                            try:
                                    
                                    if portal == 'SWBC':
                                                
                                                country,session=checkproxy_country(username,password,ip_address)
                                                if country == "US":
                                                    session,resp,link=login_toportal(username,password,session)
                                                    check(mainclient,session, resp, mainclient, subclient, portal, cid, ats_client_id, ats_portal_id,link)#pass ATS ID's
                                                    random_sleep_time = randint(900,1200)
                                                    #('Next account will be checked after %s seconds' % (random_sleep_time))
                                                    logging.info('Next account will be checked after {} seconds'.format(random_sleep_time))
                                                    time.sleep(random_sleep_time) 
                                                    #('Unable to login')
                                                    logging.info('Unable to login')
                                                    time.sleep(10)


                                    else:
                                            #('Portal not added in order updation')
                                            logging.info('Portal not added in order updation')    

                                            
                                        
                            except Exception as ex:
                                            #('Exception raised ..')
                                            logging.info('Exception raised ..')
                                            #(ex)
                                            logging.info(ex)
                                            time.sleep(10)
            else:
                        #('Bad Password')
                        logging.info('Bad Password')
                        random_sleep_time = randint(900,1200)
                        #('Next account will be checked after %s seconds' % (random_sleep_time))
                        logging.info('Next account will be checked after {} seconds'.format(random_sleep_time))
                        time.sleep(random_sleep_time)
                                
json_file_path = 'S:\Portal Order Updation App script\output_data.json'
# Query_JSON(json_file_path)     
#---------------------------------------------------------------------------------------#

def main():
        while True:
                Query_JSON(json_file_path)



if __name__ == '__main__':main()
