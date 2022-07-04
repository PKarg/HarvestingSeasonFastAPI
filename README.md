###Harvesting Season API v1 - FastAPI
API made using python FastAPI framework for managing data related to seasonal fruit harvests. <br />
Allows for management of data describing seasonal harvests, employees and expenses.

Features: <br/>
* Secure documentation - automatic OpenAPI/SwaggerUI docs secured with HTTP Basic Auth,
* User authentication system using OAuth2 with JWT,
* Admin-level endpoints with user authorization checking,
* Unit tests using dedicated separate sqlite testing database,
* Automatic exception logging,
* SQLAlchemy ORM,
* In multiple endpoints possibility to get data as csv reports
* Possibility to get both shorter and extended data about certain objects
* Script for automatic database population with randomized values for testing
* 