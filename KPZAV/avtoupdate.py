import json
import codecs
import datetime
import random
import schedule
import time
import newinfo
import mysql.connector
#Фунуція оновлює базу даних
def fill():
  newinfo.update()
  mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="gospavto"
  )
  n = 0
  with codecs.open('vehicle.json', 'r', encoding='utf-8-sig') as f:
    templates = json.load(f)
    mycursor = mydb.cursor()
    sql = "delete from Item"
    mycursor.execute(sql)
    mydb.commit()
    for p in templates:
      sql = "INSERT INTO item (ID, OKPOCode, carrierName, licStatus, licIssueDate, licStartDate, licEndDate, vhclNum," + \
      " vhclType, vhclStatus, vhclVendorID, vhclModel, vhclWt, loadCap, vchlManufYear, vchlNumSeats, vchlVIN," + \
      " certTypeID, vhclSerie, docNum, certSeries, certNum, certDateFrom, certDateTo, taxMark, taxType, taxSeries) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
      val = (str(n), p['OKPOCode'], p['carrierName'], p['licStatus'], p['licIssueDate'], p['licStartDate'], p['licEndDate'], p['vhclNum'], p['vhclType'], 
      p['vhclStatus'], p['vhclVendorID'], p['vhclModel'], p['vhclWt'], p['loadCap'], p['vchlManufYear'], p['vchlNumSeats'], p['vchlVIN'], p['certTypeID'], 
      p['vhclSerie'], p['docNum'], p['certSeries'], p['certNum'], p['certDateFrom'], p['certDateTo'], p['taxMark'], p['taxType'], p['taxSeries'])
      mycursor.execute(sql, val)
      mydb.commit()
      n += 1
      x = datetime.datetime.now()
      print(x)