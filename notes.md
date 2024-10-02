#####
1. database gis
2. daphne
3. rest
4. swagger
5. debug
6. cors
7. simplejwt
8. channels


celery -A core.celery beat --loglevel=info
celery -A core worker --loglevel=info


python3 manage.py migrate --database=location


########
GDAL_LIBRARY_PATH="/opt/homebrew/opt/gdal/lib/libgdal.dylib"
GEOS_LIBRARY_PATH = '/opt/homebrew/opt/geos/lib/libgeos_c.dylib'

#########
# settings.py

GDAL_LIBRARY_PATH = config("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = config("GEOS_LIBRARY_PATH")

#####
# libraries
GEOS, GDAL GeoIP, PROJ.4, postgis
https://realpython.com/location-based-app-with-geodjango-tutorial/




##### USER CREDIT ANALYSIS
user credit model 
    -  USER
    - credit as seeker
    - credit as provider

after each txn, provider owes platform 10% credit
after each txn, platform gets from provider 10% credit

lets see
we have digital wallet after each txn
which is basically useless

model needed: (the total balance need to be zero)
    sheet that has what provider has earned per txn, platform fee (DIGITAL WALLET in transaction app)
    sheet that has what seeker has transacted with provider
    sheet that has what seeker has earned with ads

    sheet that has what the comapny earns from provider
        upto date what the company earned
        
there need to be 
    ledger



