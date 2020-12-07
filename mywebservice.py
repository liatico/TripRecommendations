from flask import Flask, jsonify,redirect, url_for, request
import mybackend

app = Flask(__name__)
database = mybackend.Database()


@app.route('/search/<startlocation>/<timeduration>/<k>',methods = ['GET'])
def search(startlocation, timeduration, k):
   if startlocation.find('+'):
      startlocation = startlocation.replace('+', ' ')
   return jsonify(database.search(startlocation, timeduration, k)) # use redirect?


if __name__ == '__main__':
   app.run(debug = True)