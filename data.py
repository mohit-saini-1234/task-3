from flask import Flask, jsonify, abort, request
from flask_pymongo import PyMongo
import datetime
import uuid
from bson import ObjectId
from bson.json_util import dumps


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://main:fYOpqtsmGKmSMtcc@cluster0.lkdcc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route('/add_todo', methods=["POST"])

def add_todo():
    if not request.json:
        abort(500)

    title = request.json.get("title", None)
    desc = request.json.get("description", "")

    due = request.json.get("due", None)

    if due is not None:
        due = datetime.datetime.strptime(due, "%d-%m-%Y")
    else:
        due = datetime.datetime.now()

    current_user = uuid.uuid4().hex
    user_id = ""
    if current_user is not None and "id" in current_user:
        user_id = current_user["id"]

    # use insert_one to do insert operations. id is auto generated    
    ret = mongo.db.tasks.insert_one({
        "title": title,
        "description": desc,
        "done": False,
        "due": due,
        "user":  user_id
    }).inserted_id

    # fetch the inserted id and convert it to string before sending it in response
    return jsonify(str(ret))




@app.route("/up_todo/<string:id>", methods=['PUT'])
def update_todo(id):

    if not request.json:
        abort(500)

    title = request.json.get("title", None)
    desc = request.json.get("description", "")

    if title is None:
        return jsonify(message="Invalid Request"), 500

    update_json = {}
    if title is not None:
        update_json["title"] = title

    if desc is not None:
        update_json["description"] = desc


    # match with Object ID
    ret = mongo.db.tasks.update({
        "_id": ObjectId(id)
    }, {
        "$set": update_json
    }, upsert=False)

    return jsonify(str(ret))




@app.route("/rd_todo/<string:id>, methods=["GET"])
@app.route('/rd_todo/<string:direction>', methods=["GET"])

def todo(direction=None):
    # direction is optional
    current_user = uuid.uuid4().hex
    if direction == "ASC":
        direction = 1
    else:
        direction = -1

    if direction is not None:
        if current_user is not None and "id" in current_user:
            if current_user["role"] == "normal":
                ret = mongo.db.tasks.find(
                    {"user": current_user["id"]}).sort("due", direction)
        else:
            ret = mongo.db.tasks.find({"user": ""}).sort(
                "due", direction).limit(5)
    else:
        if current_user is not None and "id" in current_user:
            ret = mongo.db.tasks.find(
                {"user": current_user["id"]})
        else:
            ret = mongo.db.tasks.find({"user": ""}).limit(5)

    tasks = []
    for doc in ret:
        doc["_id"] = str(doc["_id"])
        tasks.append(doc)
    return jsonify(tasks) 




@app.route("/del_todo/<string:id>", methods=["DELETE"])
def delete_todo(id):

    ret = mongo.db.tasks.remove({
        "_id" : ObjectId(id)
    })

    return jsonify(str(ret))  


if __name__ == "__main__":
    app.run(debug=True)
