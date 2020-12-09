from flask import Flask, jsonify,request
import mybackend

app = Flask(__name__)
database = mybackend.Database()


@app.route('/',methods = ['GET'])
def search():
   startlocation = request.args.get('startlocation', None)
   timeduration = request.args.get('timeduration', None)
   k = int(request.args.get('k', None))
   if startlocation.find('+'):
      startlocation = startlocation.replace('+', ' ')
   res = database.search(startlocation, timeduration, k)
   return jsonify(res) # use redirect?


if __name__ == '__main__':
   app.run(debug = True)