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
import sys
import re
import ctypes
import logging
from datetime import datetime as DT
import os
from os import mkdir,makedirs
from datetime import datetime as DT
ctypes.windll.kernel32.SetConsoleTitleW("OA_Orderupdation_lresnew_v40") 

today = datetime.datetime.now()
photo = '375' #ecesis photographer
auto = '0' #is the order auto accepted '0'-Not auto accepted
#orderid = '1'#dummy value

removeHTML = re.compile('<.*?>')#remove HTML tags from address string
non_decimal = re.compile(r'[^\d.]+')#remove alphabets from price string

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
def conditionUpdate(orderid,session,engagement_document_id):
     #("sucess",engagement_document_id)
     try:
          #(orderid)
          headers = {
                'authority': 'vendor-genesis.lres.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                # 'cookie': '.AspNetCore.Antiforgery.GmgsQRxrXrk=CfDJ8J1xr_EGEiVNqIGirQ0B1Esa9mgS46JI1JPtF01OsU4nKC2JRWeR4pZiqIKM5XT6k1jKtnprmvbLyP7WZ6Td9r9O7mk41OjC2kJi7ujq0gfwSx8it3jVSbgF300pe3rkyJyQUwA5cJKOyfQ69VWl_dI; .AspNetCore.Session=CfDJ8J1xr%2FEGEiVNqIGirQ0B1EvAn69WV2xH4sIE64Ek%2BR0GNcKQDCXxtSK7OMfTGZu%2F%2FTF5AUPtPXMrCVvukNfpxGNQg8WbFZQve5MuYRJRkgugOSscqK7av20tQFqxsXB0%2BhaPj3CHcaUOvrzO9B7%2FRUjT%2Fi%2B35dTD3lxO5WNSswZt; CookieAuth=CfDJ8J1xr_EGEiVNqIGirQ0B1EsWFpUjsrZDAHS2p1qxd3wGY-crB_oUVHJNx2zL7J-6mbluSofGG2Tte84yl6kT5FVfd_qq-b9EfG42omx7i7e7rO7zCCcfzIYvTAa-p1u1IS1m1OGIH9o-T-rdHrqfx_KkICY5xaLHTW7Me7siz_w1l_TFvbMaKL6Q3RYiVSDrtoHRuPTvbmiy9g3j2MAHw3bVhXS72p9i088XrXWgOqxIefiBejq173DNBVrPr03KRGNWVCXPasvl-ThcNr62QWBBOrAbworJoda6wUb6w1Z6KVUpOHvUYphqj5Dcl9Kx2yL-h4pkmcwoqvzAKrMsc5xmFsSlIxDfW_UTnWA8FS2lCkmBy0UuPvN1Qw7R8z_RZ73L6xDT8sWxkxZjy-iRRUE904b4ISQsHMx2IkH1jTETPz7Jn8SkjT-rff1kcwqiMP0rP24aEGVaUJboRco7TZ9p51kO3OjL4wgKDpB_9cUe8ekqA0BrbBPAKYBkD9tVHAhnYnnWAA_pGhVILBmgUnQgL09BeUQTw6NGnBGD9eP3KMLPRG3KGIw9oG1FxWGQqnf-3n2vy3qdRttFdPCtS4_bmS_Bg4dtoUMbJuQ7cHMY6JbchjbCWHWtpwxphdgP77m1--0MAghXeiqRe1ZYoMkB9Q0oZ21yXhKn-O2AIw76I6B_EJF9d1HToAV96NC2f6WdVyNLrngEetHy-Ae9CQBl5NGjSVivhgArNKQxGZAphN0UFMZMulqLKkEiZ4XFhbI-vqiuJBYsk4ONRBnhAlN5mO2GqMzPD3-gZD78jZgb99lNKZ6dScXB1neDf9pZH3qAariR83xxs-b2gErC8YJ-5Qi-8dHXZjJ5YIw_c9ZOTFgsLgyP3hpTPtKLcrQf7Zd2Z-8MZj2DCcCrJ-wiYPJs9A1mCBFKdxlCAtsxFCuFv1sGh80NdrrV7ctERmRaILHKc6ehfo6SSqYwh0gNbVh4kGQi4vW1Yt-y8T0wcpUQVtvJuMhp3VPgPFSh0tlIz79QckJreI3ZqE_eeM67w77lWA447WNyVBbcX-UTJSqA8WEM_v-w8fARh0TyAjpmPt1Wpy4Nm-mkW7bWeMOz3BrOnQiL8Oz9Ql-zni5bbnuhxA9rV3iZbdOZ8tmSuYSw3KQOMS5h3h-OoA-CODnjxnMIexSpAG0kUPca2CMBmaPICYR8Kq2_4sGiUOYNhjYrpD2pYllXWS6_EBZseiIkgPE3w4sdV9O220eMx9mBjdyC2JlbMCuWiWs-PusAgatqVMfqE6N9U0wAwgcmyRZN3uVlHWAvCujIvNXu8qJDA4rLdsPJb_-YUZzlIuWMEVw_NUnRXELPVNf4s_5QeTqQVoJgFhXjbTdDGOGiPmpgCimLaJiH6j1YMiNvJ7DuK4B1LjcMHuXESc4bNOKU1XhevfhA4JyM26QJulcRof8oKpHCrsagRllHNCQojWeKH0xzBlKBrjqSye4d2sWhPJAD3jLq2xgfUGz2KuUIu_2shbzD2RioYS5HSz4P7lJAfoT-g0kBkRb89Olrrp_gWdMSD5nQ7NCaqiScGMX_HTlu-0spTTZmIqugejSm6y5AL_8Zaf5YHe2LUjyIscZf5-iPw8FwMhjli0XmpnR2oYkZCTV6PrAjCbPJeCDW_k_n4Jvc9gwnd2R1QIvVGyWFdWoMvE6i-UIhQ9ERH8g6CUro04-bp419f7Xv9xFqnE6_lHbQTKbYufjidUnL2T0bN41_1ZCQmu6aJm5na1fOE5sFEGp7pceHeBYvfT9cgSkraRABL8WFmAO1rCMENt4WPJvDKa3jzrzPB3WlMOnUu92WN8U_EYEseW2vaoQ7Sd9tczWEaCzU7vbOKEgd7wiv05Mz8eWzV4ke3votj07P-uRZ1g7nPH0WrTVBMEtRFqRYxzlquChcqYDpxcJUBgJqECgJuBfsmaR8ELcL3QMsuC8qCA38hQG-AAd_Jv2_3iYU6zbJlYJLtkHohaQ_sJFLv614ORI76oPNKdkfJryHe8TaWNrmXCCjn7PtD3T9TYTZ752n63B9Ss1F0F41PptaTb9mzhrXJjaQY2Jbn6nO8t1XeZA-47gsXm2tVBKK0KWTlNGADKnYUB82Zht1RYJiDPIL7CmuuTlgx9h5AVpE6AOII7JobcQOptgaHNS52P9nEQ9Ipku7D1lV2GDfzVf4l-dvKb4XeHRlO8fq7V9ytxmB6FXL',
                'referer': 'https://vendor-genesis.lres.com/Orders/Dashboard',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }

          instrResponse = session.get("https://vendor-genesis.lres.com/Orders/{}/Items/1".format(orderid))
          #("instrResponse :",instrResponse.text)
          instrResponse1 = session.get("https://vendor-genesis.lres.com/Orders/{}/Items/1/Documents/{}".format(orderid,engagement_document_id))
          #print("instrResponse1 :",instrResponse1.text)
          #("****************************************************************************")
          #keyWord1 = "Assignment requires 12 comps in total"
          #KeyWord1 = "Verdana_MSFontService"
          if "Assignment requires 12 comps in total" in instrResponse.text:
               condition = "Bad"
               logging.info(condition)
               #("Condition1:",condition)
          elif "Assignment requires 12 comps in total" in instrResponse1.text:
               condition = "Bad"
               logging.info(condition)
               #("Condition2:",condition)
          else:
               condition = 'Average'
               logging.info(condition)
               #("Condition3:",condition)
          #("Condition:",condition)     
          #exit()
          return condition
          #exit()
     except Exception as e:
          logging.info(e)
#exit()
          
def mapping_mailsend(p,address,portal,client,ordertype,to,subject):
    try:
        ordertpe_message = 'We are unable to identify the {} for the following order\n\n Address: {} \n Portal: {} \n Client: {} \n Order Type {}'.format(p,address,portal,client,ordertype)
        mail = sender.Mail('smtp.gmail.com','notifications@bpoacceptor.com','$oft@ece2021', 465, use_ssl=True,fromaddr='notifications@bpoacceptor.com')
        mail.send_message(subject=subject, to=to,body=ordertpe_message)
        #('Mapping issue reported')
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
       logging.info(f'Failed to convert duedate ==> {due} to IST')
        
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
    
def updateATS(engagement_document_id,zadd,mainclient,orderid,due,adrs,typ,portId,clientId,price,portal,client,session):
    try:

        #("Order Type",typ)
        logging.info("Order Type:{}".format(typ))
        due = validate_dateTime(due)
        #(due)
        ISTdue = date_to_IST(due)

        #("Due Date",due)
        logging.info("Due Date:{}".format(due))
        if not price: price="0"
        ##########Dummy value#########
        

        #################################################################################################
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
        
        #clientId=clientId.strip()
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
                 condition = conditionUpdate(orderid,session,engagement_document_id)
                 #('Updating Order Details to TFS..........')
                 logging.info('Updating Order Details to TFS..........')
                 rentalvalue=0
                 instruction="We are not able to update the instruction. Please check the portal."
                 inputData = "{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}~".format(orderid,due,addressTrm,typId,portId,photo,clientId,price,zipcode,auto,subchk,address_copy,ISTdue,condition,rentalvalue)
                 instruction="{}".format(instruction)
                 splinstruction="We are not able to update the instruction. Please check the portal."
                 logging.info('inputData : {}'.format(inputData))
                 payload={
                      "clientId":clientId,
                      "procData":inputData,
                      "instructions":instruction,
                      "splInstructions":splinstruction
                     }
                 #(payload)
                 #url="http://43.205.191.132/ecesisapp/ats/Home/AddOrder"#testtfsurl
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
                            trial=trial[:2]
                            x=" ".join(trial)
                            trial=x.lower()
                            #("folderzip:",zip)
                            logging.info(zip)
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
    except Exception as ex:
        #(f'Exception raised .. in check function: {ex}')
        logging.info(f'Exception raised .. in check function: {ex}')
                        
def check(session, resp, mainclient, subclient, portal, cid, ats_client_id, ats_portal_id,username):
    try:
        client=mainclient+' '+subclient
        #link contains the base link
        if 'You are logged in' in resp.text:
            logging.info("Success login into the account")
            url = 'https://vendor-genesis.lres.com/Account/Login?ReturnUrl=%2fOrders%2fDashboard'
            headers1={
                    'authority': 'vendor-genesis.lres.com',
                    'method': 'GET',
                    'path': '/Account/Login?ReturnUrl=%2fOrders%2fDashboard',
                    'scheme': 'https',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
                    }
            resp = session.get(url,headers=headers1)
            soup = BeautifulSoup(resp.content, 'html.parser')
            tokken = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
            url = "https://vendor-genesis.lres.com/Orders/PendingOrders"
            json_data = {
                            '_search': 'false',
                            'nd': 1703757122895,
                            'rows': -1,
                            'page': 1,
                            'sidx': '',
                            'sord': 'asc',
                            'criteria': {
                                'VendorFirmID': 0,
                                'Filters': [
                                    {
                                        'SearchCriteriaFilterID': 0,
                                        'SearchCriteriaID': 0,
                                        'VendorID': username,
                                        'State': None,
                                    },
                                ],
                                'SearchCriteriaID': 0,
                            },
                        }

            headers = {
                'authority': 'vendor-genesis.lres.com',
                '__requestverificationtoken': tokken,
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://vendor-genesis.lres.com',
                'referer': 'https://vendor-genesis.lres.com/Orders/Dashboard',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                    }
            
            response1=session.post(url, json=json_data,headers=headers)
            response1=json.loads(response1.text)
            if response1['records'] != 0:
                 #("res")
                 if "EngagementDocumentID" in response1['rows'][0]:
                    engagement_document_id = response1['rows'][0]['EngagementDocumentID']
                    #("EngagementDocumentID:", engagement_document_id)
                 else:
                    EngagementDocumentID = None
                    #("engagement_document_id is not present")

            details=response1['rows']
            #('Orders in progress: {}'.format(len(details)))
            logging.info('Orders in progress: {}'.format(len(details)))
            logging.info('Orders in progress: {}'.format(details))
            for o in details:
                try:
                    if 'EngagementDocumentID' in str(o):
                         engagement_document_id=o['EngagementDocumentID']
                         #("EngagementDocumentID:", engagement_document_id)
                         
                    else:
                         EngagementDocumentID = None
                    #(o['OnHold'])
                    if o['OnHold']== False:
                        address= '{} {} {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                        folderadd= '{}, {}, {} {}'.format(o['SubjectPropertyAddress1'],o['SubjectPropertyCity'],o['SubjectPropertyState'],o['SubjectPropertyPostalCode'])
                        #######################################################################
                        portaladdress = re.sub('\s+', ' ', folderadd).strip()
                        #(portaladdress)
                        logging.info("Org Address: {}".format(portaladdress))
                        zadd=folderadd
                        # headers = {
                        # 'authority': 'www.zillow.com',
                        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        # 'accept-language': 'en-US,en;q=0.9',
                        # 'referer': 'https://www.zillow.com/?utm_medium=cpc&utm_source=google&utm_content=1471764169|65545421228|kwd-570802407|603457706088|&semQue=null&gclid=Cj0KCQiAvqGcBhCJARIsAFQ5ke7rTk7RocXIajKTxmwHqUem5wp2SK8MNa7zoXF8uTE0ppY1lLn4JW8aArpKEALw_wcB',
                        # 'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                        # 'sec-ch-ua-mobile': '?0',
                        # 'sec-ch-ua-platform': '"Windows"',
                        # 'sec-fetch-dest': 'document',
                        # 'sec-fetch-mode': 'navigate',
                        # 'sec-fetch-site': 'same-origin',
                        # 'sec-fetch-user': '?1',
                        # 'upgrade-insecure-requests': '1',
                        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                        # }
                        # zilladdress=folderadd.replace(',','')
                        # zilladdress=zilladdress.replace(' ','-')
                        # #(zilladdress)
                        # logging.info('Zaddress1 : {}'.format(zilladdress))

                        # url='https://www.zillow.com/homes/{}_rb/'.format(zilladdress)
            
                        # response = requests.get(url,headers=headers)
                        # response =response.text
                        # response = HtmlResponse(url="my HTML string", body=response, encoding='utf-8')
                        # zadd=response.xpath('/html/head/title/text()').extract_first()
                        # #(zadd)
                        # logging.info('Zillowaddress1 : {}'.format(zadd))
            

                        # if zadd == None or zadd=='Access to this page has been denied':
                        #     zadd=folderadd
                         
                        # zadd=zadd.split('| Zillow')[0]
                        # zadd=zadd.split('- Apartments for Rent')[0]
                        # zadd=zadd.split('| MLS')[0]
                        # #(zadd)
                        # logging.info('Zillowaddress : {}'.format(zadd))
            ####################################################################
                        orderid= o['OrderID']
                        AssetType= o['VendorProduct'].strip()
                        Fee=o['VendorFee']
                        duedate=o['DueDate']
                        #('Due date from portal is :', duedate)
                        if "." in duedate:
                             duedate=duedate.split(".")[0]
                             #("duedate :",duedate)
                        logging.info('Due date from portal is :'.format(duedate))
                        duedate= DT.strptime(duedate,'%Y-%m-%dT%H:%M:%S').strftime("%#m/%#d/%Y")                       
                        due=duedate.replace('/Date(','').replace(')/','')
                        #('Converted Due date from portal is :', duedate)
                        logging.info('Converted Due date from portal is :'.format(duedate))
                        #(orderid,address,AssetType,Fee,duedate)
                        # logging.info(orderid,address,AssetType,Fee,duedate)
                        logging.info(orderid)
                        logging.info(address)
                        logging.info(AssetType)
                        logging.info(duedate)
                        #('updateATS')
                        updateATS(engagement_document_id,zadd,mainclient,orderid,duedate,address,AssetType,ats_portal_id,ats_client_id,Fee,portal,client,session)
                        #######UPDATING ORDER DETAILS TO DB#########
                    else:
                        logging.info("Past due order----no need to update")
                except Exception as ex:
                    #('exception here')
                    logging.info('exception here')
                    #(ex)
                    logging.info(ex)           
        else:
            url = "http://192.168.2.95/uporder/uppython.php?$cid={}".format(cid)
            r = requests.get(url)
            #('Bad Password')    
    except Exception as ex:
        #(f'Exception raised .. in check function: {ex}')
        logging.info(f'Exception raised .. in check function: {ex}')
def Query_JSON(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        cid = sys.argv[1]
        cid=int(cid)
        # cid = 5952
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
            ctypes.windll.kernel32.SetConsoleTitleW(f"{subclient}-{portal}")
            logger_portal(subclient,portal,mainclient)
            headers={}#sending headers to prevent login denied ORSS issue
            if credstatus == 'Active':                      
                    #('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    logging.info('Checking {} - {} ->{} account'.format(mainclient,subclient,portal))
                    ###################################################################################
                    try:
                                    session = requests.session()
                                    headers={
                                                'authority': 'vendor-genesis.lres.com',
                                                'method': 'POST',
                                                'path': '/Account/Login?ReturnUrl=%2f',
                                                'scheme': 'https',
                                                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                                'accept-encoding': 'gzip, deflate, br',
                                                'accept-language': 'en-US,en;q=0.9',
                                                'cache-control': 'no-cache',
                                                'content-length': '222',
                                                'content-type': 'application/x-www-form-urlencoded',
                                                'origin': 'https://vendor-genesis.lres.com',
                                                'pragma': 'no-cache',
                                                'referer': 'https://vendor-genesis.lres.com/Account/Login?ReturnUrl=%2f',
                                                'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                                                'sec-ch-ua-mobile': '?0',
                                                'sec-fetch-dest': 'document',
                                                'sec-fetch-mode': 'navigate',
                                                'sec-fetch-site': 'same-origin',
                                                'sec-fetch-user': '?1',
                                                'upgrade-insecure-requests': '1',
                                                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
                                    }
                                    headers1={
                                            'authority': 'vendor-genesis.lres.com',
                                            'method': 'GET',
                                            'path': '/Account/Login?ReturnUrl=%2fOrders%2fDashboard',
                                            'scheme': 'https',
                                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                            'accept-encoding': 'gzip, deflate, br',
                                            'accept-language': 'en-US,en;q=0.9',
                                            'cache-control': 'no-cache',
                                            'pragma': 'no-cache',
                                            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                                            'sec-ch-ua-mobile': '?0',
                                            'sec-fetch-dest': 'document',
                                            'sec-fetch-mode': 'navigate',
                                            'sec-fetch-site': 'none',
                                            'sec-fetch-user': '?1',
                                            'upgrade-insecure-requests': '1',
                                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
                                            }
                                    loginurl='https://vendor-genesis.lres.com/Account/Login?ReturnUrl=%2f'
                                    url = 'https://vendor-genesis.lres.com/Account/Login?ReturnUrl=%2fOrders%2fDashboard'
                                    resp = session.get(url,headers=headers1)
                                    soup = BeautifulSoup(resp.content, 'html.parser')
                                    tokken = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')   
                                    data = {
                                        '__RequestVerificationToken': tokken,
                                        'Username': username,
                                        'Password': password,
                                        'checkAcceptLoginTnC': 'true',
                                        'checkAcceptLoginTnC': 'false',
                                        'singlebutton':''
                                        }
                                    
                                    resp = session.post(loginurl, data=data,headers=headers)
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
# json_file_path = 'S:\PORTAL ORDER UPDATION\output_data.json'
#Query_JSON(json_file_path)
#---------------------------------------------------------------------------------------#

json_file_path = 'S:\Portal Order Updation App script\output_data.json'
def main():
    while True:
        Query_JSON(json_file_path)
            
if __name__ == '__main__':main()
