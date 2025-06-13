### Depo Hakkında

- Bu depoda şehirlerle ilgili bilgilerin bir API anahtarıyla sunucudan erişilebilindiği bir API uygulaması sunulmaktadır.

- Kullanılan teknolojiler: **Python**, **MongoDB**, **FastAPI**

## Ortamın Kurulması

#### Ön şartlar

- Bu uygulamayı yerel bilgisayarınızda çalıştırmak için bilgisayarınızda Python ve MongoDB veritabanının yüklü olması gerekiyor.

- MongoDB veritabanınızın hizmet olarak çalışıyor olması gerekiyor.

- MongoDB veritabanı sunucunuzda (yanî kendi bilgisayarınız) "geodb" isimli bir veritabanının olmaması gerekiyor.

#### Ortamın Hâzırlanması

- Öncelikle `git clone` komutunu kullanarak depoyu yerel bilgisayarınıza indirin:

- Yerel bilgisayarınızda MongoDB veritabanı yüklü değilse, kurmalısınız.

- Ardından bir özel bir Python geliştirme ortamı kurmak için depoyu indirdiğiniz dizine gidin ve bu dizinde bir komut satırı (uç birim) açın ve çalıştırın (Windows için üstteki, Linux için alttakini çalıştırın):
  
  ```py
  py -3 -m venv .env1
  python3 -m venv .env1
  ```

- Sanal ortamı aktive edin (Windows için üstteki, Linux için alttaki):
  
  ```py
  .\.env1\Scripts\activate
  ./.env1/Scripts/activate
  ```

- Ardından gerekli kütüphâneleri kurun:
  
  ```shell
  pip install fastapi pymongo
  ```

- Eğer MongoDB'yi bir yapılandırma yapmadan kurduysanız ve 27017 portunu başka bir servis kullanmıyorsa şimdiki işlemi yapmanıza gerek yok; diğer türlü dizin içerisindeki "**secret.env**" isimli dosyayı bir metîn düzenleyicisiyle açıp ve oradaki `connectionStr` ifâdesinin karşısına veritabanı bağlantı metninizi çift tırnak içerisinde belirtmeniz gerekiyor. 

- Her şey yolunda gittiyse uygulama çalıştırılmak için hâzır demektir.

### Uygulamayı Çalıştırma

- Uygulamayı öğrenme amaçlı olarak kuruyorsanız, geliştirme modunda çalıştırabilirsiniz. Bunun için şu komutu kullanın:
  
  ```py
  fastapi dev api.py
  ```

- Eğer farklı bir yapılandırma veyâ port çakışması yoksa, FastAPI uygulamanız "http://127.0.0.1:8000" adresinde hizmet veriyor olmalıdır. Uygulama ilk çalıştırıldığında bulunduğunuz dizindeki "data.json" dosyasındaki veriler MongoDB veritabanına kaydedilir. Ayrıca bir yönetici anahtarı da bu dosyaya kaydedilir.

- Uygulamayı kullanabilmeniz için bir API anahtarı edinmeniz gerekmektedir. Bunu şu adresi ziyâret ederek edinebilirsiniz:
  `http://127.0.0.1:8000/key`
  (basitlik açısından herhangi bir üyelik vs. kayıt kontrolü yapılmamaktadır)

- Her API anahtarının 5 adet kullanım limiti vardır; basitlik açısından dakîkadaki istek sayısına veyâ günlük istek sayısına göre değil, adede göre bir kısıtlama konulmuştur. Bu limiti "mongoConnection.py" dosyası içerisindeki `saveAPIKey()` fonksiyonundaki `data["limit"]` değişkenine başka bir değer atayarak değiştirebilirsiniz. Aynı API anahtarıyla 20'den fazla istek atıldığında size aşırı istek attığınızı belirten bir HTTP koduyla olumsuz bir cevâp döndürülecektir. 

- Uygulamayı test etmek için hangi erişim noktalarını nasıl deneyeceğiniz kılavuzda yer almaktadır, bunun için şurayı ziyâret edin: `http://127.0.0.1:8000/docs`

- Uygulamaya yeni bir şehir için bilgi eklemek istediğinizde veyâ mevcut bir şehir için bilgi değiştirmek istediğinizde **POST** ve **PUT** metodlarını **yönetici API anahtarıyla** kullanmanız gerekmektedir. Yönetici anahtarı proje dizinindeki "secret.env" isimli dosyada "adminKey" ismiyle tutulmaktadır. API anahtarıyla yapılan işlemlerde işlem adedi kısıtlaması yoktur.

- NOT: Şehir bilgileri ve özellikleri göstermelik bilgilerdir, üç tâne şehir için eklenmiştir; bu şehirler de "data.json" dosyasından alınmıştır; API'yi test etmeden evvel mevcut şehirlerin bilgisine bakınız. Dosya üzerinde değişiklikler yapıp, uygulamayı sıfırdan çalıştırdığınızda veri çekiminde bir sorun olmayacaktır; sadece veri eklerken belirtilen 3 özellik için ekleme yapılır; onu da `CityAtAdding` pydantic modelini değiştirerek ayarlayabilirsiniz.

### Otomatik Test

- Projede otomatik test için "apiTest.py" dosyası vardır. Şu adımları tâkip ederek otomatik testi çalıştırabilrsiniz
  
  - Otomatik test için `pytest` kitâplığını kurun;
  
  - Sistemi yayına alın
  
  - Proje dizininde komut satırı (uç birim) açın ve şu komutu çalıştırın: `pytest apiTest.py`


