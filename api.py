from fastapi import FastAPI, Query, Path, Body, Header
from fastapi.responses import JSONResponse, RedirectResponse
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field
from datetime import datetime, time, timedelta, date
from uuid import UUID
from typing import Annotated, Optional
from mongoConnection import *
from bson.objectid import ObjectId
from fastapi import status

startSystem()
api = FastAPI()

# MODELLER:
class City(BaseModel, extra = 'allow'):
    def __init__(self, **kwargs):
        super().__init__()
        for key in kwargs:
            self.__setattr__(key, kwargs[key])
class CityAtAdding(BaseModel):
    model_config = {'extra' : 'forbid'}
    plateCode: int = Field(6, gt=0, lt=82)
    name: str
    info: Optional[str] = None

# DOĞRULAMA FONKSİYONLARI:
def validatePlateCode(id):
    asInt = None
    try:
        asInt = int(id)
    except:
        return id
    if asInt <= 0 or asInt > 81:
        raise ValueError("Plaka kodu [0, 81] aralığında olmalıdır.")
    else:
        return asInt

# GET İSTEĞİ İÇİN UÇ NOKTALAR:
# API anahtarı alma noktası:
@api.get('/key/')
def getNewAPIKey():
    key = ObjectId()
    if saveAPIKey(key):
        return {"key": str(key)}
    else:
        return {"key": None}
# API köküne erişim noktası:
@api.get("/")# Buradaki 'get' bağlantı tipini belirtmektedir
def root():
    resp = RedirectResponse(url='/docs/')
    return resp
# API hakkında bilgi almak için erişim noktası:
@api.get("/apiInfo")
def getInfo():
    json = {}
    json["usableCountries"] = ['Türkiye']
    return json
# Tüm şehir bilgilerini almak için erişim noktası
@api.get('/cities/', response_model_exclude_unset = True,
         response_model_exclude_none = True)
def getCities(spec: Annotated[str, Query(
        min_length = 24,
        max_length = 24
        )]):
    if not validateLimit(ObjectId(spec)):# API doğrulaması veyâ API limit doğrulaması başarısızsa
        return getResponseForTooManyRequests()
    citiesData = getCitiesFromDB()
    cities = []
    for i in citiesData:
        cities.append(City(**i))
    decreaseLimit(ObjectId(spec))# API anahtarının erişim limitini azalt
    return cities
# Müşahhas bir şehir bilgisi almak için erişim noktası
@api.get('/cities/{nameOrPlateCode}')
def getCityByNameOrPlateCode(nameOrPlateCode: Annotated[str, Path(
        max_length=16,
        description="Plaka kodu veyâ şehir ismi"),
        AfterValidator(validatePlateCode)],
        spec: Annotated[str, Query(
            min_length = 24,
            max_length = 24
            )]):
    if not validateLimit(ObjectId(spec)):# API doğrulaması veyâ API limit doğrulaması başarısızsa
        return getResponseForTooManyRequests()
    city = None
    if type(nameOrPlateCode) is int:
        city = getCityByPlateCode(nameOrPlateCode)
    else:
        city = getCityByName(nameOrPlateCode)
    decreaseLimit(ObjectId(spec))# API anahtarının erişim limitini azalt
    if city is not None:
        return City(**city)
    else:
        extra = None
        if type(nameOrPlateCode) is int:
            extra = {"plaka": nameOrPlateCode}
        else:
            extra = {"isim": nameOrPlateCode}
        return getResponseForCityNotFound(extra)

# VERİ EKLEME İÇİN ERİŞİM NOKTALARI
@api.post('/cities/{plateCode}', status_code=201)
def addCity(plateCode: int, city: Annotated[CityAtAdding, Body(
        include_in_schema=True,
        is_required = True,
        description = "Şehir bilgisi, nesne olarak",
        #media_type="application/json",
        example = {# Örnek belirtirken JSON biçimine uyulmalı
            "plateCode" : "6",
            "name" : "Ankara",
            "info" : "Ankara hakkında bilgiler"
            }
        )], spec: Annotated[str, Query(
            min_length = 24,
            max_length = 24
            )]):
    if not validateIsAdmin(ObjectId(spec)):
        return getBadRequestForPostPut()
    res = insertNewCity(city.__dict__)
    if res is True:
        return {"info": "Şehir ekleme işlemi başarılı"}
    else:
        return getBadRequestForPostPut()
    

# VERİ TAZELEME İÇİN ERİŞİM NOKTALARI
@api.put('/cities/{plateCode}', status_code=204)
def updateCity(plateCode: int,
               info: Annotated[str, Body()],
               spec: Annotated[str, Query(
                   min_length = 24,
                   max_length = 24
                   )]):
    if not validateIsAdmin(ObjectId(spec)):
        return getBadRequestForPostPut()
    res = updateCityInfo(plateCode, info)
    if res is True:
        return {"info": "Şehir bilgisi değiştirme işlemi başarılı"}
    else:
        return getBadRequestForPostPut()

# VERİ SİLME İŞLEMİ İÇİN ERİŞİM NOKTALARI:
@api.delete('/cities/{plateCode}')
def deleteCity(plateCode: int,
               spec: Annotated[str, Query(
                   min_length = 24,
                   max_length = 24
                   )]):
    if not validateIsAdmin(ObjectId(spec)):
        return getBadRequestForPostPut()
    res = deleteCityFromDB(plateCode)
    if res is True:
        return {"info": "Şehir, veritabanından silindi"}
    else:
        return getBadRequestForPostPut()

# DİĞER ARKAPLAN İŞLEM YÖNTEMLERİ:
def getResponseForTooManyRequests():# API anahtarının limiti tükenmiş cevâbı
    data = {"info": "Verilen API anahtarı kayıtlı değil veyâ limiti tükenmiş."}
    resp = JSONResponse(content=data, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    return resp
def getResponseForCityNotFound(city = None):
    data = {}
    if city is not None:
        data["city"] = city
    data["info"] = "Verilen bilgilere bağlı bir şehir bulunamadı"
    resp = JSONResponse(content=data, status_code=status.HTTP_404_NOT_FOUND)
    return resp
def getBadRequestForPostPut(info: str = "Verilen bilgilerle ilgili işlem yapılamıyor."):
    data = {"info": info}
    resp = JSONResponse(content=data, status_code=status.HTTP_400_BAD_REQUEST)
    return resp