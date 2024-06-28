from flask import Flask, request, jsonify
from jose import jwt
from Crypto.Hash import SHA256
import datetime
import json
import sqlite3

app = Flask(__name__)

# Define your API key (this is just a simple example, in production use environment variables or a more secure method)
API_SECRET = '4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2'


# Decorator function to check API key
def require_api_key(view_func):
    def decorated_function(*args, **kwargs):
        con = sqlite3.connect("velociraptor_orgs")
        db = con.cursor()
        db.execute("SELECT * FROM orgs_keys;")
        keys = db.fetchall()
        api_key = request.headers.get('Authorization')
        found = False

        for key in keys:
            if key[1] == api_key:
                found = True

        header = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9"
        token = header + "." + api_key

        if found:
            res = jwt.decode(token,key=API_SECRET)
            print(res)
        else:
            return jsonify(message='Unauthorized access'), 401
        if request.headers.get('Authorization') == API_KEY:
            return view_func(*args, **kwargs)
        else:
            return jsonify(message='Unauthorized access'), 401

    return decorated_function


# Example endpoint that requires API key
@app.route('/api/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    id = data["id"].encode()
    name = data["name"].encode()
    
    # Set the access expiration time, it's set to expire in 1 year
    access_expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8760)
    hash = SHA256.new(id).hexdigest()

    payload = {
    'exp': access_expiration,
    'api-client-id': hash,
    }
    
    api_key = jwt.encode(payload,algorithm='HS512',key=API_SECRET)
    api = api_key.split(".")[1:]
    api_key = ".".join(api) 

    con = sqlite3.connect("velociraptor_orgs")
    db = con.cursor()
    db.execute("INSERT INTO orgs VALUES(?,?)",(id,name))
    da = con.cursor()
    da.execute("INSERT INTO orgs_keys VALUES(?,?)",(id,api_key))
    db.close()
    da.close()
    con.close()

    return jsonify(key=api_key)

@app.route('/', methods=['POST'])
@require_api_key
def action():
    payload = request.data
    payload = json.loads(payload)
    print(payload)
    return jsonify(message="submited successfully")
    


if __name__ == '__main__':
    app.run(debug=True)
