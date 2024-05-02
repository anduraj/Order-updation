import requests
from bs4 import BeautifulSoup
import time
from pytz import timezone
#import MySQLdb
import mysql.connector
import p#
import datetime
from random import randint
import sender
from scrapy.http import HtmlResponse
import re
import logging
from datetime import datetime as DT
import ctypes
import os
from os import mkdir,makedirs
from datetime import datetime as DT
import json
import sys

today = datetime.datetime.now()


# urllib3_logger = logging.getLogger('urllib3')
# urllib3_logger.setLevel(logging.CRITICAL)
# LOG_FILENAME = "backup\KSH_AdamBradford/" + DT.now().strftime('AVMOrderUpdation--%H_%M_%S_%d_%m_%Y.log')
# logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

# ctypes.windll.kernel32.SetConsoleTitleW("AVM-KSH_AdamBradford") 

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

#all_order_types={"Interior SPIF":"1","NA":"7","Driveby BPO":"2","Driveby PDCR":"13","Driveby SPIF":"13","QBPO VPS Interior":"1","QBPO VPS Exterior":"2","QBPO Exterior":"2","QBPO Interior":"1","QField Insp Ext":"13","QField Insp Int":"10","BPO - Interior":"1","BPO - Exterior":"2","BPO - Interior (with HUD Addendum)":"1","CMA Exterior SFR":"2","CMA Exterior":"2","CMA Exterior Condo":"2","MIT CMA Int SFR":"1","BPO Exterior":"2","CMA Interior":"1","CMA Interior - Condo":"1","CMA Interior - SFR":"1","Condition Report Interior":"10","EWRA":"11","Exte":"2","EARB":"2","Inte":"1","IREO":"1","IARB":"1","IWRA":"8","Exterior":"2","EREO":"2","Exterior BPO":"2","Interior BPO":"1","Inspection Interior":"10","Inspection Exterior":"13","Driveby CBPO":"2","Driveby CSCE":"2"}
photo = '375' #ecesis photographer
auto = '0'
orderid = '1'#dummy value
removeHTML = re.compile('<.*?>')#remove HTML tags from address string
non_decimal = re.compile(r'[^\d.]+')#remove alphabets from price string

def maipping_mailsend(p,address,portal,client,ordertype,to,subject):
    try:
        ordertpe_message = 'We are unable to identify the {} for the following order\n\n Address: {} \n Portal: {} \n Client: {} \n Order Type {}'.format(p,address,portal,client,ordertype)
        mail = sender.Mail('smtp.gmail.com','notifications@bpoacceptor.com','$oft@ece2021', 465, use_ssl=True,fromaddr='notifications@bpoacceptor.com')
        mail.send_message(subject=subject, to=to ,body=ordertpe_message)
        #print('Mapping issue reported')
        logging.info('Mapping issue reported')
    except Exception as e:
        #(e)
        logging.error(e)

def date_to_IST(due):#convert duedate and time to IST ==> Provide duedate - <due> in MM/DD/YYYY H:M:S format
    try:
        ISTdue = datetime.datetime.strptime(due, "%m/%d/%Y %H:%M:%S") + datetime.timedelta(hours=9,minutes=30)#parse datetime string to datetime object and add required time to it
        ISTdue = datetime.datetime.strftime(ISTdue, "%m/%d/%Y %H:%M:%S")#format datetime object to string
        #('IST Due Date',ISTdue)
        logging.info('IST Due Date {}'.format(ISTdue))
        return ISTdue
    except Exception as e:
        #('Failed to convert duedate ==> {} to IST'.format(due))
        logging.info('Failed to convert duedate ==> {} to IST'.format(due))
        
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


def updateATS(folderadd,Mainclient,Subclient,portal,duedate,address,types,price,clientId,portId,condition,rentalvalue,instruction):
        client=Mainclient+'-'+Subclient
        duedate = validate_dateTime(duedate)
        ISTdue = date_to_IST(duedate)
        
        portId=43
        
        if not price: price="0"


        #=================================================fetching ordewr type from 52  db
        # conn = mysql.connector.connect(host="34.70.96.52",database="order_updation",user="order",password="acceptance",buffered=True)
        # cursor = conn.cursor()
        # cursor.execute("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(types))
        # #("""SELECT typeid, type FROM tfstypeid WHERE FIND_IN_SET('{}', type)""".format(types))
        # if(cursor.rowcount>0):
        #     typId = cursor.fetchone()[0]
        #     #(typId)
        #     #("Order Type --{}-- Found".format(types))
        # else:
        #     #("Order Type --{}--  Not Found".format(types))
        #     logging.info("Order Type --{}--  Not Found".format(types))
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
                        if value == types:
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
                            #("Order Type --{}--  Not Found".format(types))
                            logging.info("Order Type --{}--  Not Found".format(types))
                            #("Using Default Type -- 7")
                            logging.info("Using Default Type -- 7")
                            typId = None  
                    if typId == None:
                        #("Check next set")
                         logging.info("Check next set")
                    else:
                        break
            
            #(typId)
        
        #types=types.strip()
        #if types in all_order_types:
               # typId = all_order_types[types]
       # else:
                ##("Order Type -- {} --  Not Found".format(types))
                #logging.info("Order Type -- {} --  Not Found".format(types))
               # typId = None
                
        address = removeHTML.sub('', address)       
        address = re.sub('\s+', ' ', address).strip()
        address_copy = address   
        address = address.replace(",", " ").replace("  ", " ").replace(" ,", " ").replace("  ", " ").replace(" ,", " ").replace(", ", " ")
        address = re.sub('\s+', ' ', address).strip()
        
        trimsubj="" #trimsubj --> remove 4 digit extension to zipcode from address if present,this will be passed as subchk
        n = address.split(" ")
        r = n[-1].split("-")
        r[0] = str(r[0]).replace(",", "")
        n[-1] = r[0]
        for i in range(0,len(n)): trimsubj = trimsubj + ' '+ n[i]
        
        trimsubj = trimsubj.strip()

        zipcode = n[-1].split("-")
        zipcode = str(zipcode[0]).replace(",", "").strip()

        if len(zipcode) > 5 or len(zipcode)< 3 or not zipcode.isdigit(): zipcode=None
        else: zipcode = zipcode.zfill(5) #add leading zeroes to make zipcode 5 digit,incase of 3 or 4 digit zipcodes

        addressTrm = address.replace("~", "   ")
        subchk = trimsubj.replace("~", "   ")


        price = non_decimal.sub('', str(price)).strip()
        if clientId=='97' and (typId=='10' or typId=='12' or typId=='13' or typId=='14' or typId=='17' or typId=='18' or typId=='9' or typId=='4'):
         #('Inspection order of Vernon')
         logging.info('Inspection order of Vernon')
         
        elif typId and zipcode and portId and clientId:
                #('Updating Order Details to TFS..........')
                logging.info('Updating Order Details to TFS..........')
                session = requests.Session()
                condition='Average'
                rentalvalue=0
                inputData = "{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~".format(orderid,duedate,addressTrm,typId,portId,photo,clientId,price,zipcode,auto,subchk,address_copy,ISTdue,condition,rentalvalue)
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
                            folder="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient+"//"+folderadd
                            os.makedirs(folder)
                            #("folder created")
                            logging.info("folder created")
                        if folderadd.__contains__('#') or folderadd.__contains__('Union') or folderadd.__contains__('UNION') or folderadd.__contains__('APT') or folderadd.__contains__('apt'):
                            foldercreation()
                        else:
                            trial=folderadd.replace(",","")
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
                            path="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient
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
                                    old="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient+"//"+oldaddress
                                    new="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient+"//"+folderadd
                                    os.rename(old,new)
                                    #("Folder renamed")
                                    logging.info("Folder renamed")
                                    break
                                elif trial==listadd and typeofzip==False:
                                    old="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient+"//"+oldaddress
                                    new="Z:\\BPO\\"+year1+"//"+month+"//"+currentdate+"//"+Mainclient+"//"+folderadd
                                    os.rename(old,new)
                                    #("Folder renamed")
                                    logging.info("Folder renamed")
                                    break  
                                else:
                                    #("match not found moving to next address")  
                                    logging.info("match not found moving to next address")                   

                            #(addfolders.__contains__(folderadd))
                            try:
                                if addfolders.__contains__(folderadd)==False:
                                    foldercreation()                           
                                else:
                                    #("no need to create folder")
                                    logging.info("no need to create folder")
                            except Exception as e:
                                #(e)
                                 logging.info(e)
            #####################################################################
        else:
                if not clientId:
                    #('Client Not Active or Unable to Map Client!!')
                    logging.info('Client Not Active or Unable to Map Client!!')
                    if client!="Sharyn" and client!="Sharyn Sharyn" and client!="Sharyn Jenny" and client!="Sharyn Matt" and client!="Matthew Daw" and client!="Sharyn-Sharyn" and client!="Sharyn-Jenny" and client!="Sharyn-Matt":
                        maipping_mailsend('clientname',address_copy,portal,client,types,'teamsoftware@ecesistech.com','Mapping Failed.... Clientname!')
                if not zipcode:
                    #('Invalid Zipcode!!')
                    logging.info('Invalid Zipcode!!')
                if not typId:
                    #('Unable to map order Type -- {}'.format(types))
                    logging.info('Unable to map order Type -- {}'.format(types))
                    maipping_mailsend('ordertype',address_copy,portal,client,types,'mapping@ecesistech.com','Mapping Failed.... Order Type!')
                if not portId:
                    #('Unable to map portakl!!')
                    logging.info('Unable to map portakl!!')
               

def check(session, resp, Mainclient, Subclient,portal,cid,clientId,portId):
    if 'Splash Screen' in resp.text or  'RealtorProfile' in resp.text:
            #('Succes Login')
            logging.info('Succes Login')
            new_orders_url='https://avm.assetval.com/avm/Realtor/PendingAssignments.aspx'
            head={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'en-US,en;q=0.9',
                'Connection':'keep-alive',
                'Host':'avm.assetval.com',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
                }
            
            response1 = session.get(new_orders_url, headers=head)
            soup=BeautifulSoup(response1.text,"html.parser")
            count=soup.find("span",{"id":"ctl00_Body_lblRecordCount"})
            #(count.text)
            logging.info(count.text)
            count=(count.text).split("Total: ")[1]
            if count: count=count.strip()
            if(int(count) > 0):
                    x=soup.find("table",{"id":"ctl00_Body_grdOrder"})
                    x=x.find_all("tr")
                    count1=0
                    for count1,s in enumerate(x):
                            if "PENDING" in s.text:
                                    break
                    for s in x[count1+1:]:
                        address=s.find_all("td")[2].text+" "+s.find_all("td")[3].text+" "+s.find_all("td")[4].text+" "+s.find_all("td")[5].text
                        folderadd=s.find_all("td")[2].text+", "+s.find_all("td")[3].text+", "+s.find_all("td")[4].text+" "+s.find_all("td")[5].text
                        duedate=s.find_all("td")[6].text
                        types=s.find_all("td")[8].text.strip()
                        portal="AVM"
                        #(address)
                        logging.info(address)
                        #(duedate)
                        logging.info(duedate)
                        #(types)
                        logging.info(types)
                        #(portal)
                        logging.info(portal)
                        count1=soup.find("img",{"id":"ctl00_Body_grdOrder_ctl03_imgOrderRequest"})
                        #(count1)
                        #(str(count1))
                        instructionid=str(count1).split("OrderRequest.aspx?bpo_cd=")[1].split('");')[0]
                        #("instruction================================>")
                        #(instructionid)
                        tresp=session.get("https://avm.assetval.com/avm/OrderRequest.aspx?bpo_cd="+instructionid)
                        tresp=tresp.text
                        #(tresp)
                        tresp = HtmlResponse(url="my HTML string", body=tresp.replace('&nbsp;',''), encoding='utf-8')
                        #(tresp.text)
                        res1=tresp.text
                        try:
                            instruction = str(res1).split('Special Instructions:')[1].split('TO ACCEPT/DECLINE THIS ASSIGNMENT')[0]
                        except IndexError:
                            # Handle the case where the expected substrings are not found
                            logging.warning("Special instructions not found in res1")
                            instruction = ""
                        instruction=re.sub(removeHTML,'',instruction)
                        instruction=str(instruction).strip()
                        #('instruction',instruction)
                        condition='Average'
                        rentalvalue=0  
                        price=str(res1).split('Payment:')[1].split('Special Instructions:')[0]
                        price=re.sub(removeHTML,'',price)
                        price=str(price).strip()
                        logging.info(price)
                                       
                        updateATS(folderadd,Mainclient,Subclient,portal,str(duedate),address,types,price,clientId,portId,condition,rentalvalue,instruction)
            else:
                #('No new orders in portal..')
                logging.info('No new orders in portal..')
    else:
        logging.info("Bad Password")
        url = "http://192.168.2.95/uporder/uppython.php?$cid={}".format(cid)
        r = requests.get(url)
                        

def Query_JSON(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        cid = sys.argv[1]
        cid=int(cid)
        # cid = 6639
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
            logger_portal(subclient,portal,mainclient)
            if credstatus == 'Active':
                    #('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    logging.info('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    ###################################################################################
                    
                    session = requests.session()
                    url = 'https://avm.assetval.com/avm/login.aspx'
                    init_url=session.get(url)
                    response=init_url
                    #("initial response:",response)
                    resp = HtmlResponse(url="my HTML string", body=response.text, encoding='utf-8')
                    EVENTVALIDATION=resp.xpath("//input[contains(@id,'__EVENTVALIDATION')]//@value").extract_first()
                    #("EVENTVALIDATION:",EVENTVALIDATION)
                    VIEWSTATE=resp.xpath("//input[contains(@id,'__VIEWSTATE')]//@value").extract_first()
                    #("VIEWSTATE:",VIEWSTATE)
                    VIEWSTATEGENERATOR=resp.xpath("//input[contains(@id,'__VIEWSTATEGENERATOR')]//@value").extract_first()
                    #("VIEWSTATEGENERATOR:",VIEWSTATEGENERATOR)
                    
                    #####################################################################################
                    # data={
                    #     '__EVENTTARGET':'',
                    #     '__EVENTARGUMENT':'',
                    #     '__VIEWSTATE':VIEWSTATE,
                    #     '__VIEWSTATEGENERATOR':VIEWSTATEGENERATOR,
                    #     '__EVENTVALIDATION':EVENTVALIDATION,
                    #     'ctl00$Body$pcLoginState':'{&quot;windowsState&quot;:&quot;1:1:12000:558:60:0:-10000:-10000:1:0:0:0&quot;}',
                    #     'ctl00$Body$pcLogin$txtUsername$State':'{&quot;validationState&quot;:&quot;&quot;}',
                    #     'ctl00$Body$pcLogin$txtUsername':"tmitrakas1",
                    #     'ctl00$Body$pcLogin$txtPassword$State':'{&quot;validationState&quot;:&quot;&quot;}',
                    #     'ctl00$Body$pcLogin$txtPassword':"Timon123$1@",
                    #     'ctl00$Body$pcLogin$btnLogin':'LOG IN',
                    #     'ctl00$Body$pcNotice':'{&quot;collapsed&quot;:false}',
                    #     'ctl00$Body$hdnLoginPage':'http://avm.assetval.com/avm/login.aspx',
                    #     'ctl00$Body$hdnUsernameProcessed':'',
                    #     'ctl00$Body$hdnPasswordAttempt':'',
                    #     'ctl00$Body$hdnIsLockedOut':'',
                    #     'ctl00$Body$hdnpcNotice':'1',
                    #     'DXScript':'1_10,1_11,1_22,1_62,1_12,1_13,1_14,1_16,1_40,1_257,1_263,1_258,1_256,1_47,1_37,1_41',
                    #     'DXCss':'0_4193,1_66,1_67,1_68,0_4197,0_2,0_16,1_283,0_4077,1_284,0_4073,/avm/Styles/jquery.ui.all.css,/avm/Styles/template.css,/avm/Styles/avm_v2.css,/avm/Styles/misc.css,/avm/Styles/autocomplete.css,/avm/Styles/countdown.css,/avm/Styles/uploadify.css,/avm/Styles/tooltip.css,images/assetval.ico'
                    #     }
                    data = {
                                '__EVENTTARGET': '',
                                '__EVENTARGUMENT': '',
                                '__VIEWSTATE': VIEWSTATE,
                                '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                                '__EVENTVALIDATION': EVENTVALIDATION,
                                'ctl00$Body$rpLogin': '{&quot;collapsed&quot;:false}',
                                'ctl00$Body$rpLogin$txtUsername$State': '{&quot;validationState&quot;:&quot;&quot;}',
                                'ctl00$Body$rpLogin$txtUsername': username,
                                'ctl00$Body$rpLogin$txtPassword$State': '{&quot;validationState&quot;:&quot;&quot;}',
                                'ctl00$Body$rpLogin$txtPassword': password,
                                'ctl00$Body$rpLogin$btnLogin': 'LOG IN',
                                'ctl00$Body$pcNotice': '{&quot;collapsed&quot;:false}',
                                'ctl00$Body$hdnLoginPage': 'https://avm.assetval.com/avm/login.aspx',
                                'ctl00$Body$hdnUsernameProcessed': '',
                                'ctl00$Body$hdnPasswordAttempt': '',
                                'ctl00$Body$hdnIsLockedOut': '',
                                'ctl00$Body$hdnpcNotice': '0',
                                'DXScript': '1_11,1_252,1_12,1_23,1_64,1_13,1_14,1_15,1_48,1_38,1_183,1_189,1_184,1_182,1_42,1_17',
                                'DXCss': '100_258,1_68,1_69,100_261,1_209,100_153,1_210,100_149',
                            }
                    resp = session.post(url, data=data)
                    #(resp.text)
                    #(resp.status_code)
                    time.sleep(10)
                    
                    check(session, resp, mainclient, subclient,portal,cid,ats_client_id,ats_portal_id)
                    random_sleep_time = randint(900,1200)
                    #('Next account will be checked after %s seconds' % (random_sleep_time))
                    logging.info('Next account will be checked after %s seconds' % (random_sleep_time))
                    time.sleep(random_sleep_time)                     
            else:
                    '''success_message = """Hi Team,\n\nThis is an auto generated mail to inform you that order updation failed due to BAD PASSWORD!!!!! \nTime: {}\nMain Client: {}\nSubclient: {}\nPortal: {}\n\nKindly change the password at the earliest.\nNote: Please make sure that the credentials are working before you update the credential status.""".format(str(datetime.datetime.now()), mainclient, subclient,portal)
                    mail = sender.Mail('smtp.zoho.com', 'autogenerated@zoho.com', 'Ece$!@18', 465, use_ssl=True,fromaddr=('Ecesis Notifier','autogenerated@zoho.com'))
                    mail.send_message(subject='Urgent !!! Order Updation Failed', to=('ratish@ecesistech.com','busdev@ecesistech.com','azeena@ecesistech.com'), body=success_message)'''
                    #("Not able to Login {}-{} Account.".format(mainclient,subclient))
                    logging.info("Not able to Login {}-{} Account.".format(mainclient,subclient))
                    random_sleep_time = randint(900,1200)
                    logging.info('Next account will be checked after %s seconds' % (random_sleep_time))
                    time.sleep(random_sleep_time) 

json_file_path = 'S:\Portal Order Updation App script\output_data.json'
# Query_JSON(json_file_path)     
#---------------------------------------------------------------------------------------#

def main():
    while True:
       
        Query_JSON(json_file_path)

if __name__ == '__main__':main()
