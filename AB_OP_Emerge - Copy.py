import random
import requests
from bs4 import BeautifulSoup
import json
import time
from pytz import timezone
import datetime
import mysql.connector
from scrapy.http import HtmlResponse
import sender
from random import randint
import re
import ctypes
import logging
from datetime import timedelta
from datetime import datetime as DT
import os
import sys
from os import mkdir,makedirs
from datetime import datetime as DT

today = datetime.datetime.now()

def logger_portal(client_name,portalname,mainclient):
    """This Function is used to Setup logging"""
    path=f"BACKUP//{portalname}//{mainclient}//" #Check path exist
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

def mapping_mailsend(p,address,portal,client,ordertype,to,subject):
    try:
        ordertpe_message = 'We are unable to identify the {} for the following order\n\n Address: {} \n Portal: {} \n Client: {} \n Order Type {}'.format(p,address,portal,client,ordertype)
        mail = sender.Mail('smtp.gmail.com','notifications@bpoacceptor.com','$oft@ece2021', 465, use_ssl=True,fromaddr='notifications@bpoacceptor.com')
        mail.send_message(subject=subject, to=to,body=ordertpe_message)
        #print('Mapping issue reported')
        logging.info('Mapping issue reported')
    except Exception as e:
        #(e)
        logging.error(e)

removeHTML = re.compile('<.*?>')#remove HTML tags from address string
non_decimal = re.compile(r'[^\d.]+')#remove alphabets from price string



def date_to_IST(due):#convert duedate and time to IST ==> Provide duedate - <due> in MM/DD/YYYY H:M:S format
    try:
        ISTdue = datetime.datetime.strptime(due, "%m/%d/%Y %H:%M:%S") + datetime.timedelta(hours=9,minutes=30)#parse datetime string to datetime object and add required time to it
        ISTdue = datetime.datetime.strftime(ISTdue, "%m/%d/%Y %H:%M:%S")#format datetime object to string
        #('IST Due Date',ISTdue)
        logging.info('IST Due Date {}'.format(ISTdue))
        return ISTdue
    except Exception as e:
        #(f'Failed to convert duedate ==> {due} to IST')
        
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


def updateATS(mainclient,zadd,orderid,due,adrs,typ,portId,clientId,price,portal,client,instruction,condition):

        #("Order Type",typ)
        logging.info("Order Type:{}".format(typ))
        due = validate_dateTime(due)
        #(due)
        ISTdue = date_to_IST(due)

        #("Due Date",due)
        logging.info("Due Date:{}".format(due))
        if not price: price="0"
        ##########Dummy value#########
        
      
        '''conn = mysql.connector.connect(
            host="34.70.96.52",
            database="order_updation",
            user="order",
            password="acceptance",
            buffered=True)

        cursor = conn.cursor()
        cursor.execute("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(typ))
        #("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(typ))
        if(cursor.rowcount>0):
            typId = cursor.fetchone()[0]
            #(typId)
            #("Order Type -- {} -- Found".format(typ))
        else:
            #("Order Type -- {} --  Not Found".format(typ))
            logging.info("Order Type -- {} --  Not Found".format(typ))
            #("Using Default Type -- 7")
            logging.info("Using Default Type -- 7")
            typId = None  '''
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
                        #("Check next set")
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
        if clientId=='97' and (typId=='10' or typId=='12' or typId=='13' or typId=='14' or typId=='17' or typId=='18' or typId=='9' or typId=='4'):
         #('Inspection order of Vernon')
         logging.info('Inspection order of Vernon')
        
        elif typId and zipcode and clientId and portId:
                #('Updating Order Details to TFS..........')
                logging.info('Updating Order Details to TFS..........')
                #condition=condition
                #('condition======>',condition)
                rentalvalue=0
                #(instruction)
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
                url="https://bpotrackers.com/ecesisapp/ats/Home/AddOrder" 
                # url="http://13.200.17.36/ecesisapp/ats/Home/AddOrder"#testtfsurl
                try:
                    response = session.post(url,data=payload)
                except:
                    session = requests.Session()
                    response = session.post(url,data=payload)
                #(response.text)
                resx=response.text
                logging.info(resx)

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
                            zip=trial.pop()
                            #("folderzip:",zip)
                            trial=trial[:2]
                            x=" ".join(trial)
                            trial=x.lower()    
                            #("foldertrial:",trial)        
                            path="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+mainclient
                            #(os.listdir(path))
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

                            #(addfolders.__contains__(zadd))
                            try:
                                if addfolders.__contains__(zadd)==False:
                                    foldercreation()
                                    logging.info("Folder created")
                                else:
                                    #("no need to create folder")
                                    logging.info("no need to create folder")
                            except Exception as e:
                                #(e)
            #####################################################################
        else:
           
                if not clientId:
                    #('Client Not Active or Unable to Map Client!!')
                    logging.info('Client Not Active or Unable to Map Client!!')
                    mapping_mailsend('clientname',address_copy,portal,client,typ,'teamsoftware@ecesistech.com','Mapping Failed.... Clientname!')
                if not zipcode:
                    #('Invalid Zipcode!!')
                    logging.info('Invalid Zipcode!!')
                if not typId:
                    #('Unable to map order Type -- {}'.format(typ))
                    logging.info('Unable to map order Type -- {}'.format(typ))
                    mapping_mailsend('ordertype',address_copy,portal,client,typ,'mapping@ecesistech.com','Mapping Failed.... Order Type!')
                if not portId:
                    #('Unable to map portal!!')
                    logging.info('Unable to map portal!!')
def check(session, resp, mainclient, subclient, portal, cid, ats_client_id, ats_portal_id,username):
        #condition=condition
        client=mainclient+' '+subclient
        #link contains the base link
        if 'You are logged in' in resp.text:
            url = "https://emerge-vendors.clearvalueconsulting.com/Orders/PendingOrders"
            data = {
                                                    '_search': 'false',
                                                    'nd': '1563002911995',
                                                    'rows': '-1',
                                                    'page': '1',
                                                    'sidx': '',
                                                    'sord':'asc'
                                                        }
                                                
            response1=session.get(url, data=data)
            response1=json.loads(response1.text)
            #("response1",response1)
            details=response1['rows']
            #('Orders in progress: {}'.format(len(details)))
            logging.info('Orders in progress: {}'.format(len(details)))
            #(details)
            for o in details:
              try:
                    #(o['OnHold'])
                    if o['OnHold']== False:
                        address= '{} {} {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                        folderadd= '{}, {}, {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                        #(folderadd)
                        zadd=folderadd
                        logging.info('Folder addresss :{}'.format(folderadd))
                        
                        orderid= o['OrderID']
                        AssetType= o['Product']
                        Fee=o['VendorFee']
                        duedate=o['DueDate']
                        Orderitemid=o['OrderItemID']
                        engagementDocumentId=o['EngagementDocumentID']
                        #('Due date from portal is :', duedate)
                        logging.info('Due date from portal is :'.format(duedate))
                        due=duedate.replace('/Date(','').replace(')/','')
                        due=int(due[:-3])
                        duedate=datetime.datetime.fromtimestamp(due, tz=timezone('EST')).strftime("%#m/%#d/%Y") #convert unix time stamp to EST date(without zero padding)
                        #('Converted Due date from portal is :', duedate)
                        logging.info('Converted Due date from portal is :'.format(duedate))
                        #(orderid,address,AssetType,Fee,duedate,Orderitemid,engagementDocumentId)
                        logging.info(orderid,address,AssetType,Fee,duedate,Orderitemid,engagementDocumentId)
                        pendordersurl="https://emerge-vendors.clearvalueconsulting.com/Orders/"+str(orderid)+"/Items/"+str(Orderitemid)
                        pendingordersurl=session.get(pendordersurl)

                        tresp1 = HtmlResponse(url="my HTML string", body=(pendingordersurl.text).replace("', '","").replace("&nbsp;","").replace("\t","").replace("\r\n","").replace("Loading....",""), encoding='utf-8')
                        res1=tresp1.text
                        try:
                            instruction=tresp1.xpath("//*[contains(@id, 'InstructionsTabContent')]//following::div//span//text()").extract()
                            instruction=re.sub('<.*?>','',str(instruction))
                            #("Instruction1",instruction)
                            instruction=str(instruction).replace("', '"," ").replace("×"," ").replace("  "," ").replace("['"," ").replace("']"," ").replace("\\"," ").replace("Order Item{s}","")
                            instruction=instruction.strip() 
                            #("instruction2:",instruction)
                            inst=instruction.upper()
                            #("instruction in uppercase :",inst)
                            logging.info('instruction in uppercase: {}'.format(inst))

                            
               
                            Documents=pendordersurl+"/Documents?_search=false&nd=1678788305383&rows=-1&page=1&sidx=DocumentID&sord=desc"
                            #("Documents",Documents)
                            response2=session.get(Documents)
                            #("response2",response2)
                            response2=json.loads(response2.text)
                            #("response2",response2)
                            details2=response2["records"]
                            #("details2",details2)
                            
                            cond1="ASSUME GOOD CONDITION - RECENTLY REHABBED"
                            cond2="PROPERTY RENOVATIONS HAVE ALREADY BEEN COMPLETED SO ONLY 1 VALUE IS NEEDED. SEE INTERIOR PHOTO REFERENCE FOR SUBJECT CURRENT CONDITION"
                            cond3="REFER TO THE ORDER-SPECIFIC INSTRUCTIONS AND DOCUMENTS DETAILING THE PROJECT PROVIDED BY THE CLIENT"
                            if inst:
                                if (cond2 in inst) and(cond3 in inst) and(details2<0) :
                                    condition="OA"
                                    #("OA Available")
                                elif cond1 in inst or (cond2 in inst and cond3 in inst):
                                    condition="Good"
                                    #("GOOD")
                                else:
                                    condition="New"
                                    #("New")
                                    #('Check this new instruction')
                                    logging.info('Check this new instruction')
                                    
                            else:
                                #("condition not found")
                        except Exception as E:
                            #("Exception in instruction is",E)
                            instruction="We are not able to update the instruction. Please check the portal."
                        #('Condition',condition)
                        logging.info('Condition: {}'.format(condition))
                        updateATS(mainclient,zadd,orderid,duedate,address,AssetType,ats_portal_id,ats_client_id,Fee,portal,client,instruction,condition)
                        #######UPDATING ORDER DETAILS TO DB#########
                    else:
                        #("Past due order----no need to update")
                       
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


    ######################################
def Query_JSON(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        cid = sys.argv[1]
        cid=int(cid)
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
            #('ATS Portal ID:', ats_portal_id)
            ctypes.windll.kernel32.SetConsoleTitleW(f"{subclient}-Emerge")
            logger_portal(subclient,portal,mainclient)
            headers={}#sending headers to prevent login denied ORSS issue
            if credstatus == 'Active':                           
                    #('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    logging.info('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    ###############################################################################13  INDIAN####
                    try:
                                    session = requests.session()
                                    headers1={
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Accept-Language': 'en-US,en;q=0.9',
                                    'Connection': 'keep-alive',
                                    'Host': 'emerge-vendors.clearvalueconsulting.com',
                                    'Referer': 'https://emerge-vendors.clearvalueconsulting.com/Account/Login?ReturnUrl=%2fOrders%2fDashboard',
                                    'Sec-Fetch-Dest': 'document',
                                    'Sec-Fetch-Mode': 'navigate',
                                    'Sec-Fetch-Site': 'same-origin',
                                    'Sec-Fetch-User': '?1',
                                    'Upgrade-Insecure-Requests': '1',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                                    }
                                    headers = {
                                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                                            'Referer': 'https://emerge-vendors.clearvalueconsulting.com/',
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                                            'X-Requested-With':'XMLHttpRequest'
                                                }
                                    url1 = "https://emerge-vendors.clearvalueconsulting.com/Orders/Dashboard"
                                    resp = session.get(url1,headers=headers1)
                                    soup = BeautifulSoup(resp.content, 'html.parser')
                                    tokken = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
                                    #(tokken)
                                    url = "https://emerge-vendors.clearvalueconsulting.com/Account/Login?ReturnUrl=%2fOrders%2fDashboard"                               
                                                                                                    
                                    data = {
                                        '__RequestVerificationToken': tokken,
                                        'Username': username,
                                        'Password': password,
                                        'singlebutton': '',
                                        }
                                    
                                    resp = session.post(url, data=data,headers=headers)

                                    check(session, resp, mainclient, subclient, portal, cid, ats_client_id, ats_portal_id,username)#pass ATS ID's
                                    
                                    random_sleep_time = randint(900,1200)
                                    #('Next account will be checked after %s seconds' % (random_sleep_time))
                                    logging.info('Next account will be checked after {} seconds'.format(random_sleep_time))
                                    time.sleep(random_sleep_time) 
                                
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
                             

#---------------------------------------------------------------------------------------#


json_file_path = 'S:\Portal Order Updation App script\output_data.json'
def main():
    while True:
        Query_JSON(json_file_path)


if __name__ == '__main__':main()
