from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from BrandBridge.models import Sponsor, Influencer
from flask_login import current_user


class RegistrationForm(FlaskForm):
    company_name = StringField("Company Name", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    industry = StringField("Industry", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    budget = StringField("Budget", 
                           validators=[DataRequired(), Length(min=1, max=15)])
    password = PasswordField("Password",
                           validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                           validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_company_name(self, company_name):
        sponsor = Sponsor.query.filter_by(company_name=company_name.data).first()
        if sponsor:
            raise ValidationError('This Company Name is taken. Please choose a different one')
    
    def validate_email(self, email):
        sponsor = Sponsor.query.filter_by(email=email.data).first()
        if sponsor:
            raise ValidationError('This email is taken. Please choose a different one')

class RegistrationFormINF(FlaskForm):
    name = StringField("Name", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    niche = StringField("Niche (Eg: Technology, Sports, Banking)", 
                           validators=[DataRequired(), Length(min=2, max=100)])
    reach = StringField("Reach (No. of Followers)", 
                           validators=[DataRequired(), Length(min=1, max=15)])
    password = PasswordField("Password",
                           validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                           validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_name(self, name):
        influencer = Influencer.query.filter_by(name=name.data).first()
        if influencer:
            raise ValidationError('This Name is taken. Please choose a different one')
    
    def validate_email(self, email):
        influencer = Influencer.query.filter_by(email=email.data).first()
        if influencer:
            raise ValidationError('This email is taken. Please choose a different one')     


class LoginForm(FlaskForm):
    who = SelectField(u'Who are you?', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer'), ('admin', 'Admin') ])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                           validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountFormSponsor(FlaskForm):
    company_name = StringField("Company Name", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    industry = StringField("Industry", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    budget = StringField("Budget", 
                           validators=[DataRequired(), Length(min=1, max=15)])
    picture = FileField('Update Profile Picture: ', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_company_name(self, company_name):
        if company_name.data != current_user.company_name:
            sponsor = Sponsor.query.filter_by(company_name=company_name.data).first()
            if sponsor:
                raise ValidationError('This Company Name is taken. Please choose a different one')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            sponsor = Sponsor.query.filter_by(email=email.data).first()
            if sponsor:
                raise ValidationError('This email is taken. Please choose a different one')

class UpdateAccountFormInfluencer(FlaskForm):
    name = StringField("Name", 
                           validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    niche = StringField("Niche", 
                           validators=[DataRequired(), Length(min=2, max=100)])
    reach = StringField("Reach", 
                           validators=[DataRequired(), Length(min=1, max=15)])
    picture = FileField('Update Profile Picture: ', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_name(self, name):
        if name.data != current_user.name:
            influencer = Influencer.query.filter_by(name=name.data).first()
            if influencer:
                raise ValidationError('This Name is taken. Please choose a different one')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            influencer = Influencer.query.filter_by(email=email.data).first()
            if influencer:
                raise ValidationError('This email is taken. Please choose a different one')

        

class PostCampaign(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start-Date', validators=[DataRequired()])
    end_date = DateField('End-Date', validators=[DataRequired()])
    budget = StringField('Budget', validators=[DataRequired()])
    goals = StringField('Goals', validators=[DataRequired()])
    submit = SubmitField('Post')

class AdRequestForm(FlaskForm):
    messages = TextAreaField('Goals', validators=[DataRequired()], render_kw={"placeholder": "Your Goals here"}, default="Agree to your goals")
    requirements = TextAreaField('Requirements', validators=[DataRequired()], render_kw={"placeholder": "Specify your requirements"}, default="No additional requirements")
    payment_amount = IntegerField('Payment Amount (Rs.)', validators=[DataRequired()], render_kw={"placeholder": "Enter the amount in Rs."}, default=0)
    submit = SubmitField('Submit')
