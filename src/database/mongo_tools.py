# mongo_tools.py
from pymongo import MongoClient

def get_db(db_name):
    client = MongoClient('mongodb://db:27017/')
    db = client[db_name]
    return db

def create_document(collection, data):
    result = collection.insert_one(data)
    return result.inserted_id

def read_document(collection, query):
    result = collection.find_one(query)
    return result

def update_document(collection, query, new_data):
    result = collection.update_one(query, {'$set': new_data})
    return result.modified_count

def delete_document(collection, query):
    result = collection.delete_one(query)
    return result.deleted_count
