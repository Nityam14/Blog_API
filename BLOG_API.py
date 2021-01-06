from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request, Flask
from flask_pymongo import PyMongo

#using flask web framework 
app = Flask(__name__)
app.secret_key = "secret key"

#connecting to database 
app.config["MONGO_URI"] = "mongodb://localhost:27017/Blogs"
mongo = PyMongo(app)

#adding new Blog in the database using Post method 
@app.route('/add', methods=['POST'])
def add_blog():
	_json = request.json

	#inserting title,subtitle and content of the blog  
	_btitle = _json['btitle']
	_bsbtitle = _json['bsbtitle']
	_bcontent = _json['bcontent']
	
	#checking if all three things are inserted by user or not
	#And checking whether requested method is POST or not
	if _btitle and _bsbtitle and _bcontent and request.method == 'POST':
		
		#inserting values in blog_c collection
		id = mongo.db.blog_c.insert({'btitle': _btitle, 'bsbtitle': _bsbtitle, 'bcontent': _bcontent , 'comment' : ' '})
		resp = jsonify('Blog added successfully!')
		return resp
	else:
		#if above condition got false then redirect user to not_found
		return not_found()

		
#Showing all the blogs which are currently present in the database
@app.route('/blogs')
def blogs():
	blogs = mongo.db.blog_c.find()

	#using dumps to convert the cursor into list 
	resp = dumps(blogs)
	return resp



#Adding comment to the previously stored blogs in database  
b={}
#passing object_id(unique id) to find specific blog
@app.route('/comment/<id>', methods=['PUT'])
def add_comments(id):
	_id = id
	_json = request.json
	_bname = _json['bname']
	_bcomment = _json['bcomment']
	if _id:
		blog = mongo.db.blog_c.find_one({'_id': ObjectId(id)})

		#iterating to find the specific blog
		for k,v in blog.items():
			if k=="btitle":
				_btitle=v
			if k=="bsbtitle":
				_bsbtitle=v
			if k=="bcontent":
				_bcontent=v

		b[_bname] = _bcomment
		
		#Storing comments in the form of Array or list 
		l=[]
		for k,v in b.items():
			l.append([k,v])

		#updating all the comments in the blog
		mongo.db.blog_c.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'btitle': _btitle, 'bsbtitle': _bsbtitle, 'bcontent': _bcontent, 'comment': l}})
		resp = jsonify('comment added successfully!')
		return resp
	else:
		return not_found()


#for approving and rejecting the comments which are posted by the visitors 
@app.route('/AppRej', methods=['POST','PUT'])
def comment_App_rej():

	#checking for admin using POST Method
	if request.method=='POST':
		_json = request.json
		_name = _json['name']
		_email = _json['email']
		_admin = _json['admin']
		present = mongo.db.login.find({},{"name":1})
		present1 = mongo.db.login.find({},{"email":1})
		v=dumps(present)
		v1=dumps(present1)
		if _name in v and _email in v1 :
			resp=jsonify("Login successfully")
			return resp
		else:
			return jsonify("Invlaid user")

	#After checking, deleting comments
	if request.method=='PUT':
		_json = request.json
		title = _json['btitle']
		_bname = _json['bname']
		f=0
		blog = mongo.db.blog_c.find()
		for t in blog:
			for k,v in t.items():
				if k=="btitle":
					_btitle=v
					if v==title:
						f=1
				if k=="bsbtitle" and f==1:
					_bsbtitle=v
				if k=="bcontent" and f==1:
					_bcontent=v
				if f==1:
					if k=="comment":
						_comment=v
	
		l1=[]
		for k in _comment:
			if _bname in k:
				pass
			else:
				l1.append(k) 

		mongo.db.blog_c.update_one({'btitle': _btitle}, {'$set': {'btitle': _btitle, 'bsbtitle': _bsbtitle, 'bcontent': _bcontent, 'comment': l1}})
		resp = jsonify('comments updated successfully!')
		return resp

	else:
		return not_found()				


#For login Page 
@app.route('/login', methods=['POST'])
def login():
	_json = request.json
	_name = _json['name']
	_email = _json['email']
	_admin = _json['admin']

	#checking whether the name and emailid are there or not in the database  
	present = mongo.db.login.find({},{"name":1})
	present1 = mongo.db.login.find({},{"email":1})
	v=dumps(present)
	v1=dumps(present1)
	if _name in v and _email in v1:
		resp=jsonify("Login successfully")
	else:
		resp=jsonify("Inavlid email! Try again")	
	return resp



#To update the content of previously stored blogs 
@app.route('/update/<id>', methods=['PUT'])
def update_user(id):
	_id = id
	_json = request.json
	_btitle = _json['btitle']
	_bsbtitle = _json['bsbtitle']
	_bcontent = _json['bcontent']		
	if _btitle and _bsbtitle and _bcontent and _id and request.method == 'PUT':
		mongo.db.blog_c.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'btitle': _btitle, 'bsbtitle': _bsbtitle, 'bcontent': _bcontent}})
		resp = jsonify('Blog updated successfully!')
		return resp
	else:
		return not_found()
		
#For deleting the specific blog
@app.route('/delete/<id>', methods=['DELETE'])
def delete_blog(id):
	mongo.db.blog_c.delete_one({'_id': ObjectId(id)})
	resp = jsonify('blog deleted successfully!')
	return resp
		
#Error 
#if the request is not processed correctly then it will redirect the user to this
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    return resp

if __name__ == "__main__":
    app.run()
