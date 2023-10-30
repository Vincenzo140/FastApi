import pymongo 

client = pymongo.MongoClient("mongodb://vincenzo:12345@localhost:27017/")

print(client.admin.command('ping'))