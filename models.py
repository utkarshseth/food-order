from blog import db, login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='food.jpg')

    def __repr__(self):
        return f"Items('{self.itemname}','{self.category}','{self.price}','{self.image_file}')"


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    itemscart = db.relationship('Itemscart', backref='buyer', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Itemscart(db.Model):
    i = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # count_of= db.relationship('Count', backref='count_of', lazy=True)


    def __repr__(self):
        return f"ItemsCart('{self.id}')"

class Count(db.Model):
    i=db.Column(db.Integer,primary_key=True,nullable=False)
    id = db.Column(db.Integer,nullable=False)
    item_id=db.Column(db.Integer,nullable=False)
    count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Count('{self.id}','{self.count}')"