import couchdb
import ssl


couch = couchdb.Server()


couch = couchdb.Server('http://admin:1234@localhost:5984/')

db = couch.create('test') # newly created