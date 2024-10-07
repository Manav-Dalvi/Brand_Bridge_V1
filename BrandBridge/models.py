from datetime import datetime
from pytz import timezone
from BrandBridge import db, login_manager
from flask_login import UserMixin
from flask import session

@login_manager.user_loader
def load_user(user_id):
    who = session.get('who')
    if who=='sponsor':
        return Sponsor.query.get(int(user_id))
    elif who=='influencer':
        return Influencer.query.get(int(user_id))

    

class Sponsor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    company_name = db.Column(db.String(40), unique=True, nullable=False)
    industry = db.Column(db.String(40), nullable=False)
    budget = db.Column(db.String(15), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default_company.png')
    password = db.Column(db.String(60), nullable=False)
    campaigns = db.relationship('Campaign', backref='owner', lazy=True)

    def is_admin(self):
        return False

    def is_sponsor(self):
        return True

    def is_influencer(self):
        return False
    
    # How our objects are to be printed
    def __repr__(self):
        return f"Sponsor('{self.company_name}', '{self.industry}','{self.image_file}')"
       

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone("Asia/Kolkata")))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.String(15), nullable=False)
    goals = db.Column(db.Text, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    
    # How our objects are to be printed
    def __repr__(self):
        return f"Campaign('{self.title}', '{self.date_posted}', '{self.start_date}', '{self.end_date}', '{self.goals}')"

class Influencer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    niche = db.Column(db.String(40), nullable=False)
    reach = db.Column(db.Integer, nullable=False)  # e.g., number of followers
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

    def is_admin(self):
        return False

    def is_sponsor(self):
        return False

    def is_influencer(self):
        return True
        

    def __repr__(self):
        return f"Influencer('{self.name}', '{self.niche}', '{self.reach}', '{self.image_file}')"

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False, default='None')
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'


    def __repr__(self):
        return f"AdRequest('{self.campaign_id}', '{self.influencer_id}', '{self.status}', '{self.payment_amount}')"   