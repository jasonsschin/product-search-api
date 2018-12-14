from flask import Flask, request
from flask_restful import Api, Resource

import os
import csv

app = Flask(__name__)
api = Api(app)

class Product(Resource):
    PRODUCT_FIELD_NAMES = ['description','asin','price','category','rank']

    def _readOutputFileIfAny(self,outputFileName):

        if os.path.exists(outputFileName):
            with open(outputFileName, 'r') as file:
                self.previouslySearchedProducts = list(p['asin'] for p in csv.DictReader(file,self.PRODUCT_FIELD_NAMES))

            print("Reading searched ASIN's ({})".format(len(self.previouslySearchedProducts))) 
        else:
            print("{} does not exist".format(self.outputFileName))
    
    def _getAppendOrWrite(self, outputFileName):

        if os.path.exists(outputFileName):
            append_write = 'a'
            print("Opening {} for append...".format(outputFileName))
        else:
            append_write = 'w'
            print("Opening {} for write...".format(outputFileName))

        return append_write

    def _storeAsin(self, product):

        append_write = self._getAppendOrWrite(self.outputFileName)
    
        ## Open output file for writing
        with open(self.outputFileName, append_write) as file:
            writer = csv.DictWriter(file, fieldnames=self.PRODUCT_FIELD_NAMES)
            writer.writerow(product)

    def get(self, asin):
        print(asin)
        if asin in self.previouslySearchedProducts:
            return asin, 200
        return "asin not found", 404

    def post(self, asin):
        product = request.get_json(force=True)

        if product['asin'] in self.previouslySearchedProducts:
            return "asin already exists", 400

        self._storeAsin(product)

        return None, 201, {'Location': asin, 'Custom': 'key'}

    def put(self, asin):
        return "Not implmented", 501

    def delete(self, asin):
        deleted = False

        with open(self.outputFileName , 'r+') as f:
            writer = csv.DictWriter(f,fieldnames=self.PRODUCT_FIELD_NAMES)
            reader = csv.DictReader(f)
            productList = list(reader)
            f.seek(0)

            updatedProductList = [p for p in productList if p['asin'] != asin]
            writer.writerows(updatedProductList)

            if not any(p.get('asin', None) == asin for p in productList):
                deleted = True

            f.truncate()
        
        if deleted:
            return "Deleted", 200
        else:
            return "Not found", 404
        #return "Not implmented", 501

    def __init__(self):
        self.previouslySearchedProducts = []
        self.outputFileName = 'product_search_asins.csv'
        self._readOutputFileIfAny(self.outputFileName)

api.add_resource(Product, "/product/<string:asin>")

app.run(debug=True)