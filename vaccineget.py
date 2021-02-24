import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import pprint
import vacdiscord

# zocdoc - https://www.zocdoc.com/vaccine/search/IL?flavor=state-search
# cvs - https://www.cvs.com/immunizations/covid-19-vaccine
# walmart - https://www.walmart.com/pharmacy/clinical-services/immunization/scheduled?imzType=covid&action=PswdReset&rm=x
# sam's club - https://www.samsclub.com/pharmacy/immunization?imzType=covid
# walgreens - https://www.walgreens.com/findcare/vaccination/covid-19/location-screening
# uic - https://mychart-openscheduling.et1085.epichosted.com/MyChart/SignupAndSchedule/EmbeddedSchedule?id=30301&dept=10127001&vt=1055
# costco #1 - https://book-costcopharmacy.appointment-plus.com/cttc019c/?e_id=5439#/
# costco #2 - https://book-costcopharmacy.appointment-plus.com/cttb5n42/?e_id=5435#/ 
# jewel-osco - https://www.mhealthappointments.com/covidappt
# mariano's - https://www.marianos.com/rx/covid-eligibility

#Check for vaccines, send message through discord

vacdiscord = vacdiscord.VaccineNotification()
driver = webdriver.FirefoxProfile()
driver.set_preference('dom.webdriver.enabled',False)
driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver',firefox_profile=driver)

def zocdocCheck():
    driver.get("https://www.zocdoc.com/vaccine")
    Select(driver.find_element_by_xpath('//*[@id="main"]/div/div[1]/section/div/div/div/div/div/div/select')).select_by_visible_text('Illinois')
    driver.find_element_by_xpath('//*[@id="main"]/div/div[1]/section/div/div/div/div/button').click()
    driver.find_element_by_xpath('//*[@id="age-input"]').send_keys('50')
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[1]/button').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[2]/div[1]/div[2]/div[1]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[2]/div[2]/div[2]/div[1]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[2]/div[3]/div[2]/div[1]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[2]/button').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[6]/div[1]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[6]/div[2]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[6]/div[3]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[6]/div[4]/div[2]/div[2]/label/span[1]/input').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[6]/button').click()
    driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/div/div[8]/button').click()

    # Cycling through all providers in ZocDoc
    for articleNumber in range(1,18):
        path = '//*[@id="main"]/div[1]/main/div/div[2]/div/div/div/div/section/article[' + str(articleNumber) + ']/div/div[2]/div/div'
        if driver.find_element_by_xpath(path).text != "No upcoming appointments available":
            driver.quit()
            return True

    driver.find_element_by_xpath('//*[@id="main"]/div[1]/main/div/nav/span[2]/a').click()
    time.sleep(2)
    if driver.find_element_by_xpath('//*[@id="main"]/div[1]/main/div/div[2]/div/div/div/div/section/article/div/div[2]/div/div').text != "No upcoming appointments available":
        driver.quit()
        return True
    # driver.quit()
    return False

def cvsCheck():
    driver.get("https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine")
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/content/div/div/div/div[3]/div/div/div[2]/div/div[5]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div[1]/ul/li[11]/div/a/span').click()
    if driver.find_element_by_xpath('/html/body/div[2]/div/div[17]/div/div/div/div/div/div[1]/div[2]/div/div/div[2]/div/div[6]/div/div/table/tbody/tr[2]/td[2]/span').text != "Fully Booked":
        driver.quit()
        return True
    driver.quit()
    return False

def walmartCheck():
    return None

def samsclubCheck():
    return None

def walgreensCheck():
    return None

def uicCheck():
    return None

def costcooneCheck():
    return None

def costcotwoCheck():
    return None

def jeweloscoCheck():
    return None

def marianosCheck():
    return None

def run():
    while True:
        if zocdocCheck() == True:
            vacdiscord.sendNotification("https://www.zocdoc.com/vaccine/search/IL?flavor=state-search")
            print("ZocDoc Ran")
        if cvsCheck() == True:
            vacdiscord.sendNotification("https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine")
            print("CVS Ran")
        time.sleep(120)

run()