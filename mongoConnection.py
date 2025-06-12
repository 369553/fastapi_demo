from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os
import json

connectionStr = ""
connext = None

def startSystem():
    # 'secret.env' isimli dosyadaki gizli bilgileri çevre değişkeni olarak yükle:
    load_dotenv('secret.env')
    # Bağlantı metnini al:
    connectionStr = os.environ["connectionStr"]# Bağlantı metnini çevre değişkeni olarak al
    # Bağlantı oluştur:
    connext = MongoClient(connectionStr)
    dbs = connext.list_database_names()
    isCreated = False
    for i in dbs:
        if i == 'geodb':
            isCreated = True
    # Sistem kurulmadıysa, sistemi kur:
    if not isCreated:# Veritabanı oluşturulmadıysa
        buildSystem(connext)
    # Bağlantıyı kapat:
    connext.close()


def buildSystem(connext):
    # Veritabanı referansı oluştur:
    db = connext["geodb"]# Veritabanı referansı
    
    # Koleksiyonlar için referans oluştur:
    cities = db["cities"]# Veri koleksiyonu
    apiKeys = db["apikeys"]# API anahtar bilgileri koleksiyonu
    
    
    ## API anahtarları için indeks oluştur:
    #apiKeys.create_index('key', unique=True)# Münferid API anahtarı için ve performans için indeks oluşturuyoruz
    
    # Veriler için indeksler oluştur:
    cities.create_index('plateCode', unique=True)# Münferid plaka kodu için ve performans için indeks oluşturuyoruz
    cities.create_index('name')# Performans için isim alanı üzerinde indeks oluşturuyoruz
        
    
    # JSON dosyasını oku, verileri veritabanına aktar:
    data = None
    with open('data.json', encoding='utf8') as file:
        data = json.load(file)
    if data is None:
        raise ValueError('data.json dosyasında veri aktarımı başarısız!')
    for i in data:
        cities.insert_one(i)
    adminKey = os.environ["adminKey"]
    apiKeys.insert_one({"_id": ObjectId(adminKey), "limit":100})

# Tüm şehirleri veritabanından çek:
def getCitiesFromDB():
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    cities = con["geodb"]["cities"]
    cursor = cities.find({})
    citiesData = []
    for i in cursor:
        citiesData.append(i)
    return citiesData

# Plaka numarasına göre sorgulama:
def getCityByPlateCode(plateCode: int):
    if (plateCode is None) or (type(plateCode) is not int):
        return None
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    cities = con["geodb"]["cities"]
    return cities.find_one({"plateCode": plateCode})

# Şehir ismine göre sorgulama:
def getCityByName(name: str):
    if (name is None) or (type(name) is not str):
        return None
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    cities = con["geodb"]["cities"]
    return cities.find_one({'name': name})

# API anahtarı bilgisini çekme:
def getAPIKey(apiKey: str):
    if (apiKey is None) or (type(apiKey) is not ObjectId):
        return None
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    apiKeys = con["geodb"]["apikeys"]
    return apiKeys.find_one({'key': key})

def saveAPIKey(apiKey: str):
    if (apiKey is None) or (type(apiKey) is not ObjectId):
        return None
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    data = {}
    data["_id"] = apiKey# Koleksiyon birincil anahtarı aynı zamânda API anahtarı
    data["limit"] = 5
    apiKeys = con["geodb"]["apikeys"]
    try:
        result = apiKeys.insert_one(data)
        return True
    except:
        return False

def validateLimit(apiKey: ObjectId):
    if (apiKey is None) or (type(apiKey) is not ObjectId):
        return None
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    apiKeys = con["geodb"]["apikeys"]
    try:
        res = apiKeys.find_one({'_id': apiKey})
        if res is None:# İlgili API anahtarı yoksa False döndür
            return False
        return res["limit"] > 0# API anahtarı için limit yoksa False döndür
    except:
        pass
    
def validateIsAdmin(apiKey: ObjectId):
    if (apiKey is None) or (type(apiKey) is not ObjectId):
        return False
    return (str(apiKey) == os.environ["adminKey"])

def decreaseLimit(apiKey: ObjectId):
    if (apiKey is None) or (type(apiKey) is not ObjectId):
        return None
    if str(apiKey) == os.environ["adminKey"]:
        return
    connectionStr = os.environ["connectionStr"]
    con = MongoClient(connectionStr)
    apiKeys = con["geodb"]["apikeys"]
    try:
        apiKeys.update_one({'_id': apiKey}, {'$inc': {'limit': -1}})
    except:
        pass

def insertNewCity(city: dict):
    if city is None:
        return False
    con = None
    try:
        connectionStr = os.environ["connectionStr"]
        con = MongoClient(connectionStr)
        cities = con["geodb"]["cities"]
        res = cities.insert_one(city)
        if res is None:
            return False
        return res.acknowledged
    except:
        return False
    finally:
        if con is not None:
            con.close()
def updateCityInfo(plateCode: int, info: str):
    if (plateCode is None) or (type(plateCode) is not int):
        return False
    if (info is None) or (type(info) is not str):
        return False
    con = None
    try:
        connectionStr = os.environ["connectionStr"]
        con = MongoClient(connectionStr)
        cities = con["geodb"]["cities"]
        res = cities.update_one({"plateCode": plateCode}, {"$set": {"info": info}})
        if res is None:
            return False
        return res.acknowledged
    except:
        return False
    finally:
        if con is not None:
            con.close()
def deleteCityFromDB(plateCode: int):
    if (plateCode is None) or (type(plateCode) is not int):
        return False
    con = None
    try:
        connectionStr = os.environ["connectionStr"]
        con = MongoClient(connectionStr)
        cities = con["geodb"]["cities"]
        res = cities.delete_one({"plateCode": plateCode})
        if res is None:
            return False
        return res.acknowledged
    except:
        return False
    finally:
        if con is not None:
            con.close()









