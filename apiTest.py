from dotenv import load_dotenv
import os
from fastapi.testclient import TestClient
from fastapi.responses import Response
from api import api
from mongoConnection import *
from api import City
import json

# ORTAM HÂZIRLIĞI:
# 'secret.env' isimli dosyadaki gizli bilgileri çevre değişkeni olarak yükle:
load_dotenv('secret.env')
# Bağlantı metnini al:
connectionStr = os.environ["connectionStr"]# Bağlantı metnini çevre değişkeni
# Yönetici API anahtarını al:
adminKey = os.environ["adminKey"]
# Tükenmiş API anahtarını al:
consumedKey = os.environ["consumedKey"]
# Şehir bilgilerini al, sunucudan gelen şehir bilgileriyle aynı formata çevir:
cities = getCitiesFromDB()
for i in cities:
    del i['_id']
# Bir şehir için plaka kodunu al (test değeri olarak):
plateCode = cities[0]["plateCode"]
# Bir şehir için şehir ismini al (test değeri olarak):
name = cities[0]["name"]
# Veritabanında olmayan bir şehir ismi uydur (test değeri olarak):
nameOfNonExistedCity = "aaa"
# Yeni şehir eklenmesi için şehir nesnesi (test değeri olarak):
cityAsDict = {"plateCode": 1, "name": "Adana",
"info": "Sanayi ve tarım şehridir; sıcaktır; trafiği çetrefillidir."}
city = City(**cityAsDict)

# TEST UYGULAMASINI BAŞLATMA:
testClient = TestClient(api)

# GET TEST FONKSİYONLARI:
# API anahtarı al: Pozitif Test
def testGetAPIKey():
    resp = testClient.get("/key")
    assert resp.status_code == 200
    assert resp.json() is not None
    key = resp.json()["key"]
    assert (key is not None) and (len(key) == 24)
# Tüm şehirleri kullanılabilir API anahtarıyla al: Pozitif Test: 200
def testGetCitiesWithUsableAPIKey():
    resp = testClient.get(f"/cities?spec={adminKey}")
    assert resp.status_code == 200
    assert resp.json() is not None
    assert resp.json() == cities
# Tüm şehirleri API anahtarı olmadan al: Negatif Test: 422
def testGetCitiesWithoutAPIKey():
    resp = testClient.get("/cities")
    assert resp.status_code == 422
# Tüm şehirleri tükenmiş bir API anahtarıyla al: Negatif Test: 429
def testGetCitiesWithConsumedAPIKey():
    resp = testClient.get(f"/cities?spec={consumedKey}")
    assert resp.status_code == 429
# Vâr olan bir şehri kullanılabilir bir API anahtarıyla al: Pozitif Test: 200
def testGetExistedCityWithUsableAPIKey():
    resp = testClient.get(f"/cities/{plateCode}?spec={adminKey}")
    assert resp.status_code == 200
    res = resp.json()
    assert (res is not None) and (res["plateCode"] == plateCode)
# Vâr olan bir şehri şehir ismini kullanarak kullanılabilir bir API anahtarıyla al: 200
def testGetExistedCityByCityNameWithUsableKey():
    resp = testClient.get(f"/cities/{name}?spec={adminKey}")
    assert resp.status_code == 200
    res = resp.json()
    assert (res is not None) and (res["name"] == name)
# Vâr olmayan şehri kullanılabilir bir API anahtarıyla al: Negatif Test: 404
def testGetNonExistedCityWithUsableAPIKey():
    resp = testClient.get(f"/cities/{nameOfNonExistedCity}?spec={adminKey}")
    assert resp.status_code == 404
# Vâr olan bir şehri tükenmiş bir API anahtarıyla al: Negatif Test: 429
def testGetExistedCityWithConsumedAPIKey():
    resp = testClient.get(f"/cities/{plateCode}?spec={consumedKey}")
    assert resp.status_code == 429
# Vâr olmayan bir şehri tükenmiş bir API anahtarıyla al: Negatif Test: 429
def testGetNonExistedCityWithConsumedAPIKey():
    resp = testClient.get(f"/cities/{plateCode}?spec={consumedKey}")
    assert resp.status_code == 429

# POST, PUT ve DELETE TEST FONKSİYONLARI:
# Yönetici API anahtarıyla yeni şehir ekle: Pozitif Test: 201
def testPostAddCityWithAdminKey():
    resp = testClient.post(f"/cities/{city.plateCode}?spec={adminKey}", content=json.dumps(cityAsDict, ensure_ascii=False))
    assert resp.status_code == 201
    fetched = getCityByPlateCode(city.plateCode)
    assert fetched is not None
    assert fetched["plateCode"] == city.plateCode
    assert fetched["name"] == city.name
    assert fetched["info"] == city.info
# Yönetici olmayan API anahtarıyla yeni şehir ekle: Negatif test: 400
def testPostAddCityWithNonAdminKey():
    resp = testClient.post(f"/cities/{city.plateCode}?spec={consumedKey}", content=json.dumps(cityAsDict, ensure_ascii=False))
    assert resp.status_code == 400
# Yönetici API anahtarıyla şehir bilgisini tazele: Pozitif test: 204
def testPutUpdateCityWithAdminKey():# Başarılı bir (sadece bir kez) 'testPostAddCityWithAdminKey' fonksiyonu çalıştırıldıktan sonra bu fonksiyon çalıştırılmalı
    resp = testClient.put(f"/cities/{city.plateCode}?spec={adminKey}",
                           headers={"content-type": "application/json"},
                           json="Adana hakkında yeni bilgiler..")
    fetched = getCityByPlateCode(city.plateCode)
    assert resp.status_code == 204
    assert fetched is not None
    assert fetched["info"] == "Adana hakkında yeni bilgiler.."
# Yönetici olmayan API anahtarıyla şehir bilgisini tazele: Negatif test: 400
def testPutUpdateCityWithNonAdminKey():# Başarılı bir (sadece bir kez) 'testPostAddCityWithAdminKey' fonksiyonu çalıştırıldıktan sonra bu fonksiyon çalıştırılmalı
    resp = testClient.put(f"/cities/{city.plateCode}?spec={consumedKey}",
                           headers={"content-type": "application/json"},
                           json="Adana hakkında yeni bilgiler..")
    assert resp.status_code == 400
# Yönetici API anahtarıyla şehir sil: Pozitif test: 200
def testDeleteDeleteCityWithAdminKey():# Başarılı bir (sadece bir kez) 'testPostAddCityWithAdminKey' fonksiyonu çalıştırıldıktan sonra bu fonksiyon çalıştırılmalı
    resp = testClient.delete(f"/cities/{city.plateCode}?spec={adminKey}")
    assert resp.status_code == 200
# Yönetici olmayan API anahtarıyla şehir sil: Negatif test: 400
def testDeleteDeleteCityWithNonAdminKey():# Başarılı bir (sadece bir kez) 'testPostAddCityWithAdminKey' fonksiyonu çalıştırıldıktan sonra bu fonksiyon çalıştırılmalı
    resp = testClient.delete(f"/cities/{city.plateCode}?spec={consumedKey}")
    assert resp.status_code == 400






