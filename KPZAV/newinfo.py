import requests
import zipfile
#завантажує нові версії бази даних
def update():
    url = 'https://data.gov.ua/dataset/3f5c6632-cef0-409e-a526-a9a4edebd110/resource/06b3934d-1709-4f08-9928-d727d92bf9de/download'
    r = requests.get(url, allow_redirects=True)
    open('vehicles.zip', 'wb').write(r.content)

            
    fantasy_zip = zipfile.ZipFile('F:\\KPZAV\\vehicles.zip')
    fantasy_zip.extractall('F:\\KPZAV')
    
    fantasy_zip.close()