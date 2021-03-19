#External imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains 
from datetime import datetime
from datetime import timedelta
from fake_useragent import UserAgent
import multiprocessing
import discord
import random
import time

#Internal imports
import config
import analytics

#Check for vaccines, send message through discord, add to sheets data

def zocdoc_check(driver):
    """
    Goes through 3 pages of https://www.zocdoc.com/vaccine, looks for no availibility string to
    return a false or true boolean. zocdoc - https://www.zocdoc.com/vaccine/search/IL?flavor=state-search
    """
    driver.get("https://www.zocdoc.com/vaccine/")
    Select(driver.find_element_by_xpath('//*[@id="main"]/div/div[1]/section/div/div/div/div/div/div/select')).select_by_visible_text('Illinois')
    driver.find_element_by_xpath('//*[@id="main"]/div/div[1]/section/div/div/div/div/button').click()
    #First Page
    driver.find_element_by_xpath('//*[@id="age-input"]').send_keys('70')
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[1]/button').click()
    #Second Page
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[11]/div[1]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[11]/div[2]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[11]/div[3]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[11]/div[4]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[11]/button').click()
    #Third Page
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[13]/div/div[1]/div/label/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[13]/button').click()
    # Availability Page
    # Cycling through all providers in ZocDoc
    for articleNumber in range(1,18):
        path = f'//*[@id="main"]/div[1]/main/div/div[2]/div/div/div/div/section/article[{str(articleNumber)}]/div/div[2]/div/div'
        if driver.find_element_by_xpath(path).text != "No upcoming appointments available":
            print("ZocDoc Ran")
            analytics.sheets("Zocdoc")         
            return True
    print("ZocDoc Ran")
    return False

def cvs_check(driver):
    """
    Checks for fully booked string for illinois availability.
    """
    driver.get("https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine")
    driver.find_element_by_xpath('/html/body/content/div/div/div/div[3]/div/div/div[2]/div/div[5]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div[1]/ul/li[11]/div/a/span').click()
    if driver.find_element_by_xpath('/html/body/div[2]/div/div[17]/div/div/div/div/div/div[1]/div[2]/div/div/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[2]/span').text != "Fully Booked":
        print("CVS Ran")
        analytics.sheets("CVS")
        return True
    print("CVS Ran")
    return False

def walmart_check(driver):
    """
    *Needs firefox profile with walmart login to function.
    Checks Chicago area for avaiable vaccine appointments.
    """
    driver.get('https://www.walmart.com/pharmacy/clinical-services/immunization/scheduled?imzType=covid')
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/article/section[3]/section/div[2]/div/div[2]/div[2]/label/span').click()
    driver.find_element_by_xpath('/html/body/div/div/div[1]/article/section[4]/button').click()
    try:
        driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/article/div/div[2]')
    except Exception:
        print('Walmart Ran')
        analytics.sheets("Walmart")
        return True
    print('Walmart Ran')
    return False
    # driver.find_element_by_xpath('/html/body/div/div/div[1]/article/section[2]/section[10]/label').click()
    # driver.find_element_by_xpath('/html/body/div/div/div[1]/article/section[3]/button[2]').click()
    # driver.find_element_by_xpath('/html/body/div/div/div[1]/article/section[3]/button').click()

    # if driver.find_element_by_xpath('/html/body/div/div/div[1]/article/div/div[3]/span').text != "There are no appointments available for this store right now. Please try another store.":
    #         print('Walmart Ran')
    #         analytics.sheets("Walmart")
    #         return True
    # for slot_number in range(1,18):
    #     driver.find_element_by_xpath(f'/html/body/div/div/div[1]/article/div/div[2]/div/div/button[{slot_number}]').click()
    #     if driver.find_element_by_xpath('/html/body/div/div/div[1]/article/div/div[3]/span').text != "There are no appointments available for this store right now. Please try another store.":
    #         print('Walmart Ran')
    #         analytics.sheets("Walmart")
    #         return True
    # print('Walmart Ran')
    # return False

#Firefox should have ad and tracker blockers to help bypass bot detection
def walgreens_check(driver,city):
    """
    Checks Chicago availability by checking if vaccine not avaible
    element exists. Uses Exception to return True statement. Use 
    low implicit time.
    """
    driver.get('https://www.walgreens.com/login.jsp?ru=%2Ffindcare%2Fvaccination%2Fcovid-19%2Feligibility-survey%3Fflow%3Dcovidvaccine%26register%3Drx')
    try:
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="user_name"]').click()
        actions1 = ActionChains(driver)
        actions1.send_keys(config.walgreensuser)
        actions1.perform()
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="user_password"]').click()
        actions2 = ActionChains(driver)
        actions2.send_keys(config.walgreenspass)
        actions2.perform()
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="submit_btn"]').click()
        time.sleep(10)
    except Exception:
        driver.get('https://www.walgreens.com/findcare/vaccination/covid-19?ban=covid_scheduler_brandstory_main_March2021')
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="userOptionButtons"]/a/span').click()      
    if driver.current_url[0:50] == 'https://www.walgreens.com/profile/verify_identity.':
        driver.find_element_by_xpath('//*[@id="radio-security"]').click()
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="optionContinue"]').click()
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="secQues"]').send_keys(config.walgreenssec)
        time.sleep(random.uniform(0.5,1.5))
        driver.find_element_by_xpath('//*[@id="validate_security_answer"]').click()
    time.sleep(random.uniform(0.5,1.5))
    driver.find_element_by_xpath('//*[@id="inputLocation"]').click()
    driver.find_element_by_xpath('//*[@id="inputLocation"]').clear()
    time.sleep(random.uniform(0.5,1.5))
    driver.find_element_by_xpath('//*[@id="inputLocation"]').send_keys(city)
    time.sleep(random.uniform(0.5,1.5))
    driver.find_element_by_xpath('//*[@id="wag-body-main-container"]/section/section/section/section/section[2]/div/span/button').click()
    try:
        driver.find_element_by_xpath('//*[@id="wag-body-main-container"]/section/section/section/section/section[1]/p')
    except NoSuchElementException:
        print(f'Walgreens {city} Ran')
        analytics.sheets(f"{city} Walgreens")
        return True
    print(f'Walgreens {city} Ran')
    return False

def uic_check(driver):
    """
    Checks one page of UIC vaccine schedule.
    """
    driver.get('https://mychart-openscheduling.et1085.epichosted.com/MyChart/SignupAndSchedule/EmbeddedSchedule?id=30301&dept=10127001&vt=1055')
    try:
        driver.find_element_by_xpath('//*[@id="D6F73C26-7627-4948-95EA-2C630C25C5E9_scheduleOpenings_OpeningsData"]/div/span/span[2]')
    except NoSuchElementException:
        print('UIC Health Ran')
        analytics.sheets("UIC Health")
        return True
    print('UIC Health Ran')
    return False

def costco_one_check(driver):
    """
    Checks against vaccine not availabe element to return true
    or false. Raises Exception: Page not loaded, when page does
    not load in time. Checks first costco location.
    """
    driver.get('https://book-costcopharmacy.appointment-plus.com/cttc019c/?e_id=5439#/')
    time.sleep(2)
    if driver.find_element_by_xpath("/html/body").text == "" or driver.find_element_by_xpath("/html/body").text == None:
        raise Exception('Page not loaded')
    driver.find_element_by_xpath('//*[@id="page-content"]/div/div[2]/div[3]/ul/li/a').click()
    time.sleep(2)
    if driver.find_element_by_xpath("/html/body").text == "" or driver.find_element_by_xpath("/html/body").text == None:
        raise Exception('Page not loaded')
    try:
        driver.find_element_by_xpath('//*[@id="page-content"]/div/div[2]/div/div[3]/div')
    except NoSuchElementException:
        print('Costco 1 Ran')
        analytics.sheets("Costco One")
        return True 
    print('Costco 1 Ran')
    return False 

def costco_two_check(driver):
    """
    Checks against vaccine not availabe element to return true
    or false. Raises Exception: Page not loaded, when page does
    not load in time. Checks second costco location.
    """
    driver.get('https://book-costcopharmacy.appointment-plus.com/cttb5n42/?e_id=5435#/')
    time.sleep(2)
    if driver.find_element_by_xpath("/html/body").text == "" or driver.find_element_by_xpath("/html/body").text == None:
        raise Exception('Page not loaded')
    driver.find_element_by_xpath('//*[@id="page-content"]/div/div[2]/div[3]/ul/li/a').click()
    time.sleep(2)
    if driver.find_element_by_xpath("/html/body").text == "" or driver.find_element_by_xpath("/html/body").text == None:
        raise Exception('Page not loaded')
    try:
        driver.find_element_by_xpath('//*[@id="page-content"]/div/div[2]/div/div[3]')
    except NoSuchElementException:
        print('Costco 2 Ran')
        analytics.sheets("Costco Two")
        return True
    print('Costco 2 Ran')
    return False
    
def jewel_osco_check(driver):
    """
    Bypasses captcha to look for vaccines at jewel osco. Cycles 
    through calendar to check for dates at jewel osco locations.
    Needs captcha solved in firefox profile to work consistently.
    """
    driver.get('https://www.mhealthappointments.com/covidappt')
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="covid_vaccine_search_input"]').click()
    actions= ActionChains(driver)
    actions.send_keys("60607")
    actions.perform()
    driver.find_element_by_xpath('//*[@id="fifteenMile-covid_vaccine_search"]').click()
    driver.find_element_by_xpath('//*[@id="covid_vaccine_search"]/div[2]/div[2]/button').click()   
    driver.find_element_by_xpath('//*[@id="attestation_1002"]').click()
    actions.send_keys(Keys.TAB + Keys.TAB + Keys.TAB + Keys.TAB + Keys.TAB + Keys.TAB + Keys.TAB + " ")
    actions.perform()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="covid_vaccine_search_questions_submit"]/div/button').click()
    Select(driver.find_element_by_xpath('//*[@id="appointmentType-type"]')).select_by_visible_text('COVID Vaccine Dose 1 Appt')
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="covid19-reg-v2"]/div/div[1]/div/div[2]/div/div[4]/div[2]/div[1]/div/button').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="covid19-reg-v2"]/div/div[2]/div/div[2]/div/div[4]/div[2]/div[1]/div/button').click()
    checkstring = 'There is no availability at this time. Please try a different search or check back later as more availability may open.'
    time.sleep(2)
    if driver.find_element_by_xpath('//*[@id="covid19-reg-v2"]/div/div[3]/div/div[2]/div/div[3]/div/div/form/div[2]/div[4]/div/p').text != checkstring:
        print('Jewel-Osco Ran')
        analytics.sheets("Jewel-Osco")
        return True
    for i in range(1,6):
        Select(driver.find_element_by_xpath('//*[@id="item-type"]')).select_by_index(i)
        time.sleep(0.8)
        if driver.find_element_by_xpath('//*[@id="covid19-reg-v2"]/div/div[3]/div/div[2]/div/div[3]/div/div/form/div[2]/div[4]/div/p').text != checkstring:
            print('Jewel-Osco Ran')
            analytics.sheets("Jewel-Osco")
            return True
    return False

def marianos_check(driver):
    driver.get('https://www.marianos.com/rx/covid-eligibility')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li/div/div[2]/div[2]/div/div/div/button[1]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[3]/div/div[2]/div[2]/div/div/div/button[2]').click()
    Select(driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[5]/div/div[2]/div[2]/div/div/div/select')).select_by_visible_text('IL')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[6]/div/div[2]/div[2]/div/div/div/button[2]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[8]/div/div[2]/div[2]/div/div/div/button[2]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[1]/input').send_keys('01011970')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[2]/button').click()
    Select(driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[11]/div/div[2]/div[2]/div/div/div/select')).select_by_visible_text('Manufacturing')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[12]/div/div[2]/div[2]/div/div/div/button').click()
    driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[2]/form/div/div[1]/div').click()
    actions = ActionChains(driver)
    actions.send_keys('Chicago')
    actions.perform()
    driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[2]/form/button').click()
    if driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[3]/div/span').text != 'None of the locations in your search currently offer COVID-19 vaccines, please try another Zip Code, City, or State':
        print("Marianos Ran")
        analytics.sheets("Marianos")
        return True
    print("Marianos Ran")
    return False
    
# Crystal Lake Vaccination Checks

def marianos_check_crystal_lake(driver):
    driver.get('https://www.marianos.com/rx/covid-eligibility')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li/div/div[2]/div[2]/div/div/div/button[1]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[3]/div/div[2]/div[2]/div/div/div/button[2]').click()
    Select(driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[5]/div/div[2]/div[2]/div/div/div/select')).select_by_visible_text('IL')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[6]/div/div[2]/div[2]/div/div/div/button[2]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[8]/div/div[2]/div[2]/div/div/div/button[2]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[1]/input').send_keys('01011970')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[2]/button').click()
    Select(driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[11]/div/div[2]/div[2]/div/div/div/select')).select_by_visible_text('Manufacturing')
    driver.find_element_by_xpath('//*[@id="content"]/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[12]/div/div[2]/div[2]/div/div/div/button').click()
    driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[2]/form/div/div[1]/div').click()
    actions = ActionChains(driver)
    actions.send_keys('Crystal Lake')
    actions.perform()
    driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[2]/form/button').click()
    if driver.find_element_by_xpath('//*[@id="step1"]/div/div/div/div[3]/div/span').text != 'None of the locations in your search currently offer COVID-19 vaccines, please try another Zip Code, City, or State':
        print("Marianos Crystal Lake Ran")
        analytics.sheets("Marianos Crystal Lake")
        return True
    print("Marianos Crystal Lake Ran")
    return False

def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        #Main starts here
        while True:
            if  "01:30:00" <= datetime.now().strftime("%H:%M:%S") <= "06:30:00":
                time.sleep(18000)
            sitelist = [x for x in range(1,7)]
            ua = UserAgent()
            userAgent = ua.random
            preferences = webdriver.FirefoxProfile(config.firefoxprofpath)
            preferences.set_preference('dom.webdriver.enabled',False)
            preferences.set_preference('marionette.enabled',False)
            preferences.set_preference("general.useragent.override", userAgent)
            driver = webdriver.Firefox(executable_path=config.geckopath,firefox_profile=preferences)
            driver.implicitly_wait(15)
            while sitelist != []:
                site = random.choice(sitelist)
                if site == 1:
                    sitelist.remove(1)
                    #ZocDoc
                    try:
                        if zocdoc_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://www.zocdoc.com/vaccine/search/IL?flavor=state-search")
                    except Exception:
                        print('ZocDoc Error')
                        await client.guilds[0].channels[7].send(f"ZocDoc error {datetime.now().strftime('%H:%M:%S')}")
                if site == 2:
                    sitelist.remove(2)
                    #CVS
                    try:
                        if cvs_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine")
                    except Exception:
                        print('CVS Error')
                        await client.guilds[0].channels[7].send(f"CVS error {datetime.now().strftime('%H:%M:%S')}")
                if site == 3:
                    sitelist.remove(3)
                    #Walmart
                    try:
                        if walmart_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://www.walmart.com/pharmacy/clinical-services/immunization/scheduled?imzType=covid")
                    except Exception:
                        print('Walmart Error')
                        await client.guilds[0].channels[7].send(f"Walmart error {datetime.now().strftime('%H:%M:%S')}")
                if site == 4:
                    sitelist.remove(4)
                    #UIC
                    driver.implicitly_wait(4)
                    try:
                        if uic_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://mychart-openscheduling.et1085.epichosted.com/MyChart/SignupAndSchedule/EmbeddedSchedule?id=30301&dept=10127001&vt=1055")
                    except Exception:
                        print('UIC Error')
                        await client.guilds[0].channels[7].send(f"UIC error {datetime.now().strftime('%H:%M:%S')}")
                    driver.implicitly_wait(15)
                if site == 5:
                    sitelist.remove(5)
                    #Costco one
                    driver.implicitly_wait(6)
                    try:
                        if costco_one_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://book-costcopharmacy.appointment-plus.com/cttc019c/?e_id=5439#/")
                    except Exception:
                        print('Costco One Error')
                        await client.guilds[0].channels[7].send(f"Costco one error {datetime.now().strftime('%H:%M:%S')}")
                if site == 6:
                    sitelist.remove(6)
                    #Costco two
                    try:
                        if costco_two_check(driver) == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://book-costcopharmacy.appointment-plus.com/cttb5n42/?e_id=5435#/")
                    except Exception:
                        print('Costco Two Error')
                        await client.guilds[0].channels[7].send(f"Costco two error {datetime.now().strftime('%H:%M:%S')}")
            driver.quit()
            time.sleep(65)
            try:
                driver.quit()
            except Exception:
                pass
        #Main ends here
    client.run(config.discordbotapikey)

def walgreens_main():
    client = discord.Client()

    @client.event
    async def on_ready():
        #Main starts here
        while True:
            if  "01:30:00" <= datetime.now().strftime("%H:%M:%S") <= "06:30:00":
                time.sleep(18000)
            sitelist = [x for x in range(1,2)]
            ua = UserAgent()
            userAgent = ua.random
            preferences = webdriver.FirefoxProfile(config.firefoxprofpath)
            preferences.set_preference('dom.webdriver.enabled',False)
            preferences.set_preference('marionette.enabled',False)
            preferences.set_preference("general.useragent.override", userAgent)
            driver = webdriver.Firefox(executable_path=config.geckopath,firefox_profile=preferences)
            driver.implicitly_wait(15)
            while sitelist != []:
                site = random.choice(sitelist)
                if site == 1:
                    sitelist.remove(1)
                    #Walgreens
                    driver.implicitly_wait(6)
                    try:
                        if walgreens_check(driver,'Chicago') == True:
                            await client.guilds[0].channels[2].send(f"**Vaccine Found!**\nhttps://www.walgreens.com/findcare/vaccination/covid-19/location-screening")
                    except Exception:
                        print('Walgreens Chicago Error')
                        await client.guilds[0].channels[7].send(f"Walgreens error {datetime.now().strftime('%H:%M:%S')}")
                    driver.implicitly_wait(15)
                # if site == 2:
                #     sitelist.remove(2)
                #     #Walgreens romeoville
                #     driver.implicitly_wait(4)
                #     try:
                #         if walgreens_check(driver,'Berwyn') == True:
                #             await client.guilds[0].channels[6].send(f"**Vaccine Found!**\nhttps://www.walgreens.com/findcare/vaccination/covid-19/location-screening")
                #     except Exception:
                #         print('Walgreens Berwyn Error')
                #         await client.guilds[0].channels[7].send(f"Walgreens Berwyn error {datetime.now().strftime('%H:%M:%S')}")
            driver.quit()
            time.sleep(random.randint(200,230))
            try:
                driver.quit()
            except Exception:
                pass
        #Main ends here
    client.run(config.discordbotapikey)

if __name__ == '__main__':
    run_walgreens = True
    if run_walgreens == True:
        p1 = multiprocessing.Process(target=main)
        p2 = multiprocessing.Process(target=walgreens_main)
        p1.start()
        p2.start()
        p1.join()
        p2.join()   
    else:
        p1 = multiprocessing.Process(target=main)
        p1.start()
        p1.join()