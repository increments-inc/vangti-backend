## Vangti App
 - App for vangti transaction

### Sockets
look for message.txt for reference

### Location stored in Database
 - user locations are stored as Point(longitude, latitude)
 - polyline points are stored as Point(latitude, longitude)


## Version 1
### Core libraries
- database gis 
- daphne 
- rest 
- swagger
- debug 
- cors 
- simplejwt
- channels


### Location libraries
- GEOS
- GDAL 
- GeoIP
- PROJ.4
- postgis
- https://realpython.com/location-based-app-with-geodjango-tutorial/


### Commands
    source venv/bin/activate
    python3 manage.py runserver 0.0.0.0:8000
    celery -A core.celery beat --loglevel=info
    celery -A core worker --loglevel=info


### Migrations
    python3 manage.py migrate
    python3 manage.py migrate --database=location
    python3 manage.py migrate --database=credits


### GEOS and GDAL (for location)
##### In env (mac)
- GDAL_LIBRARY_PATH="/opt/homebrew/opt/gdal/lib/libgdal.dylib"
- GEOS_LIBRARY_PATH = '/opt/homebrew/opt/geos/lib/libgeos_c.dylib'



## Version 2
### USER CREDIT ANALYSIS
user credit model 
-  USER
- credit as seeker
- credit as provider





### 