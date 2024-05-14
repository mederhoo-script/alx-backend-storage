#!/usr/bin/env python3
"""
a script that lists all databases in MongoDB.
"""
import pymongo
from pymongo import MongoClient


def list_all(mongo_collection):
    """
    script that lists all databases in MongoDB.
    """
    if not mongo_collection:
        return []
    documents = mongo_collection.find()
    return [post for post in documents]


if __name__ == "__main__":
    client = MongoClient('mongodb://127.0.0.1:27017')
    school_collection = client.my_db.school
    schools = list_all(school_collection)
    for school in schools:
        print("[{}] {}".format(school.get('_id'), school.get('name')))
