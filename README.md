# zaya_assignment  

Backend for Cab booking Application  



## Installation  

requirement: python 3.64, PIP  
then open a terminal  

```
    pip install pipenv
    pipenv install
    pipenv run migrate
    pipenv run collectstatic
    pipenv run runserver
```

## Design asthetics  

### Stack:  

```
Technology used: Django
database: sqllite3
cache: Redis
Geoposition: Redis(GEO feature)
Authentication: social-auth, JWT auth
code linting: according to PEP8
resful: djangorestframework
```

### Data Base Schema:  

![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525041357/er1.jpg)

### Cache:  

Redis is used to cache storage and retrieve geo distance between location  

Documents:  

1. value Type: hashMap, key: pool(contains driver seats information)  
2. value Type: geospatial, key: <city_name>(contains information for driver location with key city name and sub key driver name)  

## API Structure  

## Authentications  
Type supported: Social Auth(Google +), JWT token Auth

### Social Auth(google +)  
REQUEST:  
URL: /auth/login/google-oauth2/?next=/api/social_auth/complete/?param=longitude,latitude,city,type     
METHOD: ['GET']  
here

Request:

```
   param:longitude,latitude,city,type
    were
   longitude: your longitude
   latitute: your latitude
   city: city name
   type: user type (driver / rider)

   example: /auth/login/google-oauth2/?next=/api/social_auth/complete/?param=19.84321,72.85432,mumbai,driver
```

### JWT Auth
#### Create User

To create new driver or rider

driver:

Request:

```
  URL: /api/driver/
  Method: ['POST']    
  here    
   REQUEST PARAMETER:
    {
   "user": {
       username: name of user
       password: string password
       lat: your latitude
       long: your long
       city: city name
       }
   }
```

![Alt Text](http://res.cloudinary.com/dnp9yrx92/image/upload/v1524924398/driver_create.gif)

Rider:

Request:
```
  URL: /api/rider/   
  Method: ['POST']    
  here   
   REQUEST PARAMETER:
   {
   "user": {
       username: name of user
       password: string password
       lat: your latitude
       long: your long
       city: city name
       }
   }

```

![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1524924399/rider_create.gif)

#### Authenticate JWT

To get JWT based token

Request:

```
  URL: /api/token   
  Method: ['POST']   
  here   
   REQUEST PARAMETER:    
   username: name of user   
   password: string password
```
Response:
```
{
    "token": <token>
}
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1524924398/jwtauthenticate.gif)


#### NOTE: Token
This token is necessary for all the request ahead and needed to be passed in header of request in format mention below

```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023368/auth_token.png)


## Driver Side APIs

### Driver Profile API:

URL: /api/driver/profile

*METHOD == GET:*
API to retrieve driver rides

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
```
Response:
```
    {
        "status": "success" / "fail"
        "error": "if any error"
        "msg": "msg"
        "bookings": [
             {
                "from_lat_position": String,
                "from_long_position": string",
                "to_long_position": string,
                "to_lat_position": string,
                "status": "start" / "end" / "wait",
                "distance": <float>,
                "fair": <float>,
                "seats": <integer>,
                "created_at": <date>,
                "rider": <string>
            }
        ]
        "current_booking": [{
                "from_lat_position": String,
                "from_long_position": string",
                "to_long_position": string,
                "to_lat_position": string,
                "status": "start" / "end" / "wait",
                "distance": <float>,
                "fair": <float>,
                "seats": <integer>,
                "created_at": <date>,
        }],
        "current_rider": [{
           "user": {
               username: name of user
               password: string password
               lat: your latitude
               long: your long
               city: city name
           }
        }]
    }

```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023368/driver_profile.png)

METHOD == PUT:
API to update location, city

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "long": <decimal with 5 digits after .>
        "lat": <decimal with 5 digits after .>
        "city": <string>
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```

### Driver Start Service Api
URL: /api/driver/book/

METHOD == POST:
put driver in queue to find rides

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "long": <decimal with 5 digits after .> or none(if none then last longitude saved in database will be used)
        "lat": <decimal with 5 digits after .>(if none then last latitude saved in database will be used)
        "city": <string>
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```

![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023368/driver_book.png)

### Driver Complete ride Api
URL: /api/driver/complete/

METHOD == POST:
complete driver ride with ridername
Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "ridername": <string>(ridername)(only if pool ride to specify rider name for which pool need to end)
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error",
        "fair": "float"
    }
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023367/driver_complete.png)


### Driver Stop Service Api
URL: /api/driver/stop/

METHOD == POST:
remove driver from queue. So no ride be assign to driver

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```

## Rider Services


### Rider Profile API:

URL: /api/rider/profile

*METHOD == GET:*
API to retrieve rider bookings

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
```
Response:
```
    {
        "status": "success" / "fail"
        "error": "if any error"
        "msg": "msg"
        "bookings": [
             {
                "from_lat_position": String,
                "from_long_position": string",
                "to_long_position": string,
                "to_lat_position": string,
                "status": "start" / "end" / "wait",
                "distance": <float>,
                "fair": <float>,
                "seats": <integer>,
                "created_at": <date>,
                "rider": <string>
            }
        ]
        "current_booking": {
                "from_lat_position": String,
                "from_long_position": string",
                "to_long_position": string,
                "to_lat_position": string,
                "status": "start" / "end" / "wait",
                "distance": <float>,
                "fair": <float>,
                "seats": <integer>,
                "created_at": <date>,
                "rider": <string>
        }
    }
```

![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023369/rider_profile.png)

METHOD == PUT:
API to update location, city

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "long": <decimal with 5 digits after .>
        "lat": <decimal with 5 digits after .>
        "city": <string>
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```



### Rider book a cab Service Api
URL: /api/rider/book/

METHOD == POST:
Book a cab

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "to_long": <decimal with 5 digits after .>
        "to_lat": <decimal with 5 digits after .>
        "city": <string>
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525037922/book_full.png)


### Rider book pool cab Service Api
URL: /api/rider/book/pool

METHOD == POST:
Book a cab pool

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"
    body: {
        "to_long": <decimal with 5 digits after .>
        "to_lat": <decimal with 5 digits after .>
        "city": <string>
    }
```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error"
    }
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023368/rider_book_pool.png)

### rider Complete ride Api
URL: /api/rider/complete/


METHOD == POST:
Complete rider ride with driver

Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"

```

Response:
```
    {
        "status": "success"/"fail",
        "msg": "if any message",
        "error": "if and error",
        "fair": "float"
    }
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525023368/rider_complete.png)


## Get driver/rider details Api
URL: /api/user/


METHOD == GET:
GET driver/rider details
Request:
```
    header:
    content-type: "application/json",
    Authorization: "JWT <token>"

```

Response:
```
    {
       username: name of user
       password: string password
       lat: your latitude
       long: your long
       city: city name
       on_rider: boolean field show True if on ride
    }
```
![Alt Text](https://res.cloudinary.com/dnp9yrx92/image/upload/v1525037922/get_detail.png)
