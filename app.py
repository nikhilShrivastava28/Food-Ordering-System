from flask import Flask
from flask import url_for, redirect, request, make_response,flash, session, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from datetime import datetime
# Creates the application object 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jfos.db'
db = SQLAlchemy(app)

## Models

class Customer(db.Model):
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cname = db.Column(db.String(250), nullable=False)
    cmail = db.Column(db.String(250), unique=True, nullable=False)
    cmobile = db.Column(db.Integer, nullable=False)
    caddress = db.Column(db.String(250), nullable=False)
    cpassword = db.Column(db.String(250), nullable=False)
    
    def __repr__(self):
        return "customer id : "+ str(self.cid)


class Restadmin(db.Model):
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rname = db.Column(db.String(250), nullable=False)
    rmail = db.Column(db.String(250), unique=True, nullable=False)
    rmobile = db.Column(db.Integer, nullable=False)
    raddress = db.Column(db.String(250), nullable=False)
    rpassword = db.Column(db.String(250), nullable=False)
    
    

class Admin(db.Model):
    amail = db.Column(db.String(250), primary_key=True) 
    apassword = db.Column(db.String(250), nullable=False)

class Items(db.Model):
	iid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	iname = db.Column(db.String(250), nullable=False)
	iprice = db.Column(db.Integer, nullable=False)
	ilimit = db.Column(db.Integer,nullable=False)
	rid = db.Column(db.Integer, db.ForeignKey('restadmin.rid'), nullable=False)

    

# class Orders(db.Model):
#     oid = db.Column(db.Integer,primary_key=True, autoincrement=True)
#     cid = db.Column(db.Integer, db.ForeignKey('customer.cid'), nullable=False)
#     rid = db.Column(db.Integer, db.ForeignKey('restadmin.rid'), nullable=False)
#     items = db.Column(db.String(250), nullable=False)
#     totalprice=db.Column(db.Integer, nullable=False)
#     ostatus = db.Column(db.String(20), nullable=False)
    
db.create_all()

## Routes

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/menucard')
def menucard():
    return render_template('menucard.html', allrest = Restadmin.query.all())


@app.route('/uregister')
def uregister():
	return render_template('uregister.html')


@app.route('/uregisterNext', methods = ['GET','POST'])
def uregisterNext():
    if request.method == "GET":
        cmail = request.args.get("cmail")
        cpassword = request.args.get("cpassword")

    elif request.method == "POST":
        cmail = request.form['cmail']
        cpassword = request.form['cpassword']
        customercheck = Customer.query.filter(and_(Customer.cmail == cmail, Customer.cpassword == cpassword)).first()
        if customercheck :

            return render_template('uregister.html', cmsg = "User already exists, try logging in.")
        else:
            customer = Customer(cname=request.form["cname"], cmail=request.form["cmail"], cmobile=request.form["cmobile"], caddress=request.form["caddress"], cpassword=request.form['cpassword'])
            db.session.add(customer)
            db.session.commit()

            return render_template('userlogin.html',cusmsg="Registered Succcessfully...! \n Please Login To Continue")


@app.route('/ulogin')
def login():
	return render_template('userlogin.html')


@app.route('/uloginNext',methods=['GET','POST'])
def uloginNext():

	if request.method == "GET":
		cmail = request.args.get("cmail")
		cpassword = request.args.get("cpassword")
	
	elif request.method == "POST":
		cmail = request.form['cmail']
		cpassword = request.form['cpassword']

		
		customer  = Customer.query.filter(and_(Customer.cmail == cmail, Customer.cpassword == cpassword)).first()


		if customer :
			session['cmail'] = request.form['cmail']
			return redirect(url_for('uhome'))
			
		return render_template('userlogin.html',cusname="Uh oh!...\n Please enter valid username and password!")


@app.route('/ulogout')
def ulogout():
	session.pop('cmail',None)
	session.clear()
	return redirect(url_for('index'))


@app.route('/uhome',methods=['GET','POST'])
def uhome():
	if not session.get('cmail'):
		return redirect(request.url_root)
	cmail=session['cmail']
	customer  = Customer.query.filter(Customer.cmail == cmail).first()

	return render_template('uhome.html',cusname=customer.cname)



@app.route('/umenucard', methods = ['GET', 'POST'])
def umenucard():
    if request.method == 'GET':
        return render_template('umenucard.html', allrest = Restadmin.query.all())
    else:
        rname = request.form['restname']
        rlist = Restadmin.query.filter(Restadmin.rname == rname)
        return render_template('umenuf.html', rlist = rlist)



@app.route('/userupdate', methods = ['GET', 'POST'])
def userupdate():
    if not session.get('cmail'):
        return redirect(request.url_root)

	
    cmail=session['cmail']
    customer=Customer.query.filter(Customer.cmail==cmail).first()
    if request.method == 'GET':
        return render_template('updateuser.html',cusname=customer.cname,cusinfo = customer)
    else:
        cmail = session['cmail']
        customer=Customer.query.filter(Customer.cmail==cmail).first()
        upname = request.form['cid']
        customer.cid = upname
        customer.cname = request.form['cname']
        customer.cmail = cmail
        customer.cmobile = request.form['cmobile']
        customer.caddress = request.form['caddress']
        customer.cpassword = request.form['cpassword']
        db.session.commit()
        updatedcust = Customer.query.filter(Customer.cmail==cmail).first()

        return render_template('updateuser1.html',cusinfo = updatedcust) 




@app.route('/deleteuser')
def deleteuser():
    if not session.get('cmail'):
        return redirect(request.url_root)

    cmail = session['cmail']
    todel = Customer.query.filter(Customer.cmail == cmail).first()
    db.session.delete(todel)
    db.session.commit()

    return render_template('index.html')


@app.route('/userorders',methods=['GET','POST'])
def userorders():
	if not session.get('cmail'):
		return redirect(request.url_root)
	cmail=session['cmail']
	customer  = Customer.query.filter(Customer.cmail == cmail).first()
	cid=customer.cid
	myorders = Orders.query.filter(Orders.cid == cid)
		
	return render_template('userorders.html',cusname=customer.cname,restadmin = customer.query.all(), myorders=myorders)



def mergedicts(dict1, dict2):
	if isinstance(dict1, list) and isinstance(dict2, list):
		return dict1 + dict2
	elif isinstance(dict1, dict) and isinstance(dict2, dict):
		return dict(list(dict1.items()) + list(dict2.items()))
	return False


total = 0

@app.route('/addCart', methods = ['POST'])
def addCart():
	global total
	try:
		item_id = request.form['item_id']
		quant = request.form['quantity']
		item = Items.query.filter(Items.iid == item_id).first()

		total = total + (int(item.iprice) * int(quant))
		item.ilimit -= int(quant)
		db.session.commit()

		if  item_id and quant and request.method == 'POST':
			itemdict = 	{item_id:{'name': item.iname, 'price': item.iprice,'quantity':quant, 'limit':item.ilimit}}
			if 'FoodCart' in session:
				print(session['FoodCart'])

				if item_id in session['FoodCart']:
					print("This is already in Cart")
				else:
					session['FoodCart'] = mergedicts(session['FoodCart'], itemdict)
					redirect(url_for('umenucard'))
			else:
				session['FoodCart'] = itemdict
				return redirect(url_for('umenucard'))
	except Exception as e:
		print(e)
	finally:
		return redirect(url_for('umenucard'))


@app.route('/cart')
def cart():
	if 'FoodCart' not in session:
		return redirect(request.referrer)
	total = 0
	for key, item in session['FoodCart'].items():
		total += float(item['price']) * float(item['quantity'])
	
	return render_template('cart.html', total = total)


@app.route('/updatecart/<int:ikey>', methods = ['POST'])
def updatecart(ikey):
	if 'FoodCart' not in session and len(session['FoodCart']) <= 0:
		return redirect(url_for('uhome'))
	if request.method == 'POST':
		quantity = request.form['quantity']
		upQuantity = request.form['upQuantity']
		limit = request.form['limit']
	try:
		session.modified = True
		for key, item in session['FoodCart'].items():
			if int(key) == ikey:
				item['quantity'] = upQuantity
				newLimit = int(limit) - int(upQuantity) + int(quantity)
				item['limit'] = newLimit
				updateItem = Items.query.filter(Items.iid == key).first()
				updateItem.ilimit = newLimit
				db.session.commit()

				return redirect(url_for('cart'))
	except Exception as e:
		print(e)
		return redirect(url_for('cart'))



@app.route('/deleteincart/<int:ikey>/<int:quant>', methods = ['POST'])
def deleteincart(ikey,quant):
	if 'FoodCart' not in session and len(session['FoodCart']) <= 0:
		return redirect(url_for('uhome'))

	if request.method == 'POST':
		quantity = int(quant)

	try:
		session.modified = True
		for key, item in session['FoodCart'].items():
			if int(key) == ikey:
				session['FoodCart'].pop(key, None)
				updateItem = Items.query.filter(Items.iid == key).first()
				updateItem.ilimit += quantity
				db.session.commit()

				return redirect(url_for('cart'))
	except Exception as e:
		print(e)
		return redirect(url_for('cart'))



@app.route('/emptycart')
def emptycart():
	try:
		session.clear()
		return redirect(url_for('uhome'))
	except Exception as e:
		print(e)


@app.route('/pay')
def pay():
	return render_template("pay.html")



@app.route('/restmenu', methods = ['GET','POST'])
def restmenu():
	if not session.get('cmail'):
		return redirect(request.url_root)

	if request.method == "GET":
		restid = request.args.get("restid")
	
	elif request.method == "POST":
		restid = request.form['restid']

	items = Items.query.filter(Items.rid == restid).all()
	restad = Restadmin.query.filter(Restadmin.rid == restid).first()
	return render_template('restmenu.html',rest=restad, restitems=items)


## Restaurant

@app.route('/restlogin')
def restlogin():
	return render_template('restlogin.html')


@app.route('/restloginNext',methods=['GET','POST'])
def restloginNext():

	if request.method == "GET":
		rmail = request.args.get("rmail")
		rpassword = request.args.get("rpassword")
	
	elif request.method == "POST":
		rmail = request.form['rmail']
		rpassword = request.form['rpassword']

		
		restadmin  = Restadmin.query.filter(and_(Restadmin.rmail == rmail, Restadmin.rpassword == rpassword)).first()


		if restadmin :
			session['rmail'] = request.form['rmail']
			return redirect(url_for('resthome'))

		return render_template('restlogin.html',restname="Login failed...\n Please enter valid username and password!")


@app.route('/resthome',methods=['GET','POST'])
def resthome():
	if not session.get('rmail'):
		return redirect(request.url_root)
	rmail=session['rmail']
	restadmin  = Restadmin.query.filter(Restadmin.rmail == rmail).first()
	rid = restadmin.rid
	return render_template('resthome.html',restname=restadmin.rname)



@app.route('/restupdate', methods = ['GET', 'POST'])
def restupdate():
    if not session.get('rmail'):
        return redirect(request.url_root)

	
    rmail=session['rmail']
    restaurant = Restadmin.query.filter(Restadmin.rmail==rmail).first()
    if request.method == 'GET':
        return render_template('restupdate.html',restname=restaurant.rname,restinfo = restaurant)
    else:
        rmail = session['rmail']
        restaurant = Restadmin.query.filter(Restadmin.rmail==rmail).first()
        upname = request.form['rid']
        restaurant.rid = upname
        restaurant.rname = request.form['rname']
        restaurant.rmail = rmail
        restaurant.rmobile = request.form['rmobile']
        restaurant.raddress = request.form['raddress']
        restaurant.rpassword = request.form['rpassword']
        db.session.commit()
        updatedrest = Restadmin.query.filter(Restadmin.rmail==rmail).first()

        return render_template('restupdate1.html',restinfo = updatedrest)


@app.route('/viewrestmenu',methods=['GET','POST'])
def viewrestmenu():
	if not session.get('rmail'):
		return redirect(request.url_root)
	rmail=session['rmail']
	restaurant  = Restadmin.query.filter(Restadmin.rmail == rmail).first()
	restid = restaurant.rid
	items = Items.query.filter(Items.rid == restid).all()


	return render_template('viewrestmenu.html',restaurant=restaurant, items=items)


@app.route('/addrestitem')
def addrestitem():
	if not session.get('rmail'):
		return redirect(request.url_root)
	rmail=session['rmail']
	restaurant  = Restadmin.query.filter(Restadmin.rmail == rmail).first()

	return render_template('addrestitem.html', restaurant = restaurant)


@app.route('/addrestitemNext',methods = ['GET','POST'])
def addrestitemNext():
	if not session.get('rmail'):
		return redirect(request.url_root)
	if request.method == "GET":
		iname = request.args.get("iname")
		iprice = request.args.get("iprice")
		ilimit = request.args.get("ilimit")
	
	elif request.method == "POST":
		iname = request.form['iname']
		iprice = request.form['iprice']
		ilimit = request.form['ilimit']

	
	rmail=session['rmail']
	rest = Restadmin.query.filter(Restadmin.rmail == rmail).first()
	restid=rest.rid

	items = Items(iname=request.form["iname"], iprice=request.form["iprice"], ilimit = request.form["ilimit"], rid=restid)
	db.session.add(items)
	db.session.commit()
	
	return redirect(url_for('viewrestmenu'))


@app.route('/updaterestitem',methods = ['GET','POST'])
def updateitem():
	if not session.get('rmail'):
		return redirect(request.url_root)
	return render_template('updaterestitem.html')


@app.route('/updaterestitemNext',methods = ['GET','POST'])
def updaterestitemNext():
	if not session.get('rmail'):
		return redirect(request.url_root)
	if request.method == "GET":
		iid = request.args.get("iid")
		iname = request.args.get("iname")
		iprice = request.args.get("iprice")
		ilimit = request.args.get("ilimit")
	
	elif request.method == "POST":
		iid = request.form['iid']
		iname = request.form['iname']
		iprice = request.form['iprice']
		ilimit = request.form['ilimit']

	
	rmail=session['rmail']
	restad  = Restadmin.query.filter(Restadmin.rmail == rmail).first()
	restid=restad.rid

	item = Items.query.filter(and_(Items.iid ==iid,Items.rid==restid)).first()

	if item :
		item.iname = iname
		item.iprice = iprice
		item.ilimit = ilimit
		db.session.commit()

		return redirect(url_for('viewrestmenu'))
	else :		
		return render_template('updaterestitem.html',errmsg="UH OH ! Looks like that is not your menu item !")


@app.route('/removerestitem',methods = ['GET','POST'])
def deleteitem():
	if not session.get('rmail'):
		return redirect(request.url_root)
	return render_template('removerestitem.html')	


@app.route('/removerestitemNext',methods = ['GET','POST'])
def removerestitemNext():
	if not session.get('rmail'):
		return redirect(request.url_root)
	if request.method == "GET":
		iid = request.args.get("iid")
	
	elif request.method == "POST":
		iid = request.form['iid']
	
	rmail=session['rmail']
	restaurant  = Restadmin.query.filter(Restadmin.rmail == rmail).first()
	restid = restaurant.rid

	item = Items.query.filter(and_(Items.iid ==iid,Items.rid==restid)).first()
	if item :
		
		db.session.delete(item)
		db.session.commit()

		return redirect(url_for('viewrestmenu'))
	else :
		return render_template('removerestitem.html',errmsg="UH OH! Looks like that is not your menu item ! ")



@app.route('/restlogout')
def restlogout():
	session.pop('rmail',None)
	return redirect(url_for('index'))


@app.route('/deleterest')
def deleterest():
    if not session.get('crmail'):
        return redirect(request.url_root)

    rmail = session['rmail']
    todel = Restadmin.query.filter(Restadmin.rmail == rmail).first()
    db.session.delete(todel)
    db.session.commit()

    return render_template('index.html')


@app.route('/adminlogin')
def adminlogin():

	return render_template('adminlogin.html')


@app.route('/adminloginNext',methods=['GET','POST'])
def adminloginNext():
	
	if request.method == "GET":
		amail = request.args.get("amail")
		apassword = request.args.get("apassword")

	elif request.method == "POST":
		amail = request.form['amail']
		apassword = request.form['apassword']


		admin  = Admin.query.filter(and_(Admin.amail == amail, Admin.apassword == apassword)).first()


		if admin :
			session['amail'] = request.form['amail']
			return redirect(url_for('adminhome'))

		return render_template('adminlogin.html',errmsg = "Login failed...\n Please enter valid username and password!")



@app.route('/adminhome',methods=['GET','POST'])
def adminhome():
	if not session.get('amail'):
		return redirect(request.url_root)
	amail = session['amail']
	admin  = Admin.query.filter(Admin.amail == amail).first()

	return render_template('adminhome.html')
  
@app.route('/regrestadmin', methods = ['GET','POST'])
def regrestadmin():
	if not session.get('amail'):
		return redirect(request.url_root)	
	if request.method == "GET":
		rmail = request.args.get("rmail")
		rmobile = request.args.get("rmobile")

	elif request.method == "POST":
		rmail = request.form['rmail']
		rmobile = request.form['rmobile']

	

	restadmin = Restadmin.query.filter(or_(Restadmin.rmail == rmail, Restadmin.rmobile == rmobile)).first()

	if restadmin:
		return render_template('adminhome.html', errmsg="Restaurant Already Exists in DB")

	else:
		newrest = Restadmin(rname=request.form["rname"], rmail=request.form["rmail"], rmobile=request.form["rmobile"], raddress=request.form["raddress"], rpassword=request.form['rpassword'])
	
		db.session.add(newrest)
		db.session.commit()
	
		return render_template('adminhome.html', successmsg="Restaurant Registered Succcessfully...!")


@app.route('/viewallrestadmin')
def viewallrestadmin():
	if not session.get('amail'):
		return redirect(request.url_root)	
	return render_template('viewallrestadmin.html',allrest = Restadmin.query.all())


@app.route('/adminrestmenu', methods = ['GET','POST'])
def adminrestmenu():
	if not session.get('amail'):
		return redirect(request.url_root)

	if request.method == "GET":
		restid = request.args.get("restid")
	
	elif request.method == "POST":
		restid = request.form['restid']

	items = Items.query.filter(Items.rid == restid).all()
	restad = Restadmin.query.filter(Restadmin.rid == restid).first()
	return render_template('adminrestmenu.html',restad=restad, restadmin=items)	


@app.route('/adminlogout')
def adminlogout():
	session.pop('amail',None)
	return redirect(url_for('index'))

        
        





app.secret_key = 'Nikhildec28'
## To Run
if __name__ == "__main__":
    app.run(debug=True)

