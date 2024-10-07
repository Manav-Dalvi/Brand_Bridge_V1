from BrandBridge.models import Sponsor, Campaign, Influencer, AdRequest
from PIL import Image
import secrets
import os
from flask import session
from BrandBridge import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from BrandBridge.forms import RegistrationForm, LoginForm, UpdateAccountFormSponsor, \
    PostCampaign, RegistrationFormINF, UpdateAccountFormInfluencer, AdRequestForm
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps


#Decorator
@app.route('/')
@app.route('/home')
def home():
    print("home_page")
    page=request.args.get('page', 1, type=int)
    campaigns = Campaign.query.order_by(Campaign.date_posted.desc()).paginate(page=page, per_page=5)
    campaigns_page = Campaign.query.all()
    return render_template('home.html', campaigns=campaigns, count=len(campaigns_page))

    
@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        sponsor = Sponsor(company_name=form.company_name.data, 
                          industry=form.industry.data, 
                          budget=form.budget.data,
                          email=form.email.data, 
                          password=hashed_password)
        db.session.add(sponsor)
        db.session.commit() 
        flash('Your account has been created! You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/register_influencer', methods=['GET', 'POST'])
def register_influencer():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationFormINF()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        influencer = Influencer(name=form.name.data, 
                          niche=form.niche.data, 
                          reach=form.reach.data,
                          email=form.email.data, 
                          password=hashed_password)
        db.session.add(influencer)
        db.session.commit() 
        flash('Your account has been created! You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register_influencer.html', title='Influencer Registeration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        who = form.who.data
        session['who'] = who
        if who=='sponsor':
            sponsor = Sponsor.query.filter_by(email=form.email.data).first()
            if sponsor and bcrypt.check_password_hash(sponsor.password, form.password.data):
                flash('Logged in successfully', 'success')
                login_user(sponsor, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful! Please try again', 'danger')
        elif who=='influencer':
            influencer = Influencer.query.filter_by(email=form.email.data).first()
            if influencer and bcrypt.check_password_hash(influencer.password, form.password.data):
                flash('Logged in successfully', 'success')
                login_user(influencer, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful! Please try again', 'danger')
        elif who=='admin':
            if form.email.data=='admin@admin.com' and form.password.data=='admin':
                flash('Logged in successfully', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login Unsuccessful! Please try again', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():

    influencers = db.session.query(Influencer).all()
    sponsors = db.session.query(Sponsor).all()
    campaigns = db.session.query(Campaign).all()

    return render_template('admin_dashboard.html', 
                           influencers=influencers, 
                           sponsors=sponsors,
                           campaigns=campaigns)

@app.route('/admin/flag_item', methods=['POST'])
def flag_item():
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id', type=int)

    if item_type == 'influencer':
        influencer = db.session.query(Influencer).get(item_id)
        if influencer:
            # Delete associated ad_requests
            AdRequest.query.filter_by(influencer_id=item_id).delete()
            # Delete the influencer
            db.session.delete(influencer)
            db.session.commit()
    elif item_type == 'sponsor':
        sponsor = db.session.query(Sponsor).get(item_id)
        if sponsor:
            # Delete associated campaigns
            campaigns = Campaign.query.filter_by(sponsor_id=item_id).all()
            for campaign in campaigns:
                # Delete associated ad_requests
                AdRequest.query.filter_by(campaign_id=campaign.id).delete()
                # Delete the campaign
                db.session.delete(campaign)
            # Delete the sponsor
            db.session.delete(sponsor)
            db.session.commit()
    elif item_type == 'campaign':
        campaign = db.session.query(Campaign).get(item_id)
        if campaign:
            # Delete associated ad_requests
            AdRequest.query.filter_by(campaign_id=item_id).delete()
            # Delete the campaign
            db.session.delete(campaign)
            db.session.commit()

    return redirect(url_for('admin_dashboard'))




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def sponsor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_sponsor():
            flash('Access restricted to sponsors only.', 'danger')
            return redirect(url_for('home'))  # Redirect to a suitable page
        return f(*args, **kwargs)
    return decorated_function

def influencer_required(f):
    @wraps(f)
    def decorated_function_2(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_influencer():
            flash('Access restricted to influencers only.', 'danger')
            return redirect(url_for('home'))  # Redirect to a suitable page
        return f(*args, **kwargs)
    return decorated_function_2


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size=(125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_sponsor():
        form = UpdateAccountFormSponsor()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.company_name = form.company_name.data
            current_user.industry = form.industry.data
            current_user.budget = form.budget.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        elif request.method == 'GET':
            form.company_name.data = current_user.company_name
            form.industry.data = current_user.industry
            form.budget.data = current_user.budget
            form.email.data = current_user.email
        
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
        ad_requests = AdRequest.query.filter(AdRequest.campaign_id.in_([c.id for c in campaigns])).all()
        return render_template('account.html', title='Account', image_file=image_file, form=form, ad_requests=ad_requests)
    
    elif current_user.is_influencer():
        form = UpdateAccountFormInfluencer()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.niche = form.niche.data
            current_user.reach = form.reach.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        elif request.method == 'GET':
            form.name.data = current_user.name
            form.email.data = current_user.email
            form.niche.data = current_user.niche
            form.reach.data = current_user.reach

        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
        total_earnings = sum(ad_request.payment_amount for ad_request in ad_requests if ad_request.status == 'Accepted')
        
        return render_template('account.html', title='Account', image_file=image_file, form=form, ad_requests=ad_requests, total_earnings=total_earnings)
    
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))


@app.route("/post/newcampaign", methods=['GET', 'POST'])
@login_required
@sponsor_required
def new_campaign():
    form = PostCampaign()
    if form.validate_on_submit():
        campaign = Campaign(title=form.title.data,
                            desc=form.desc.data,
                            start_date=form.start_date.data,
                            end_date=form.end_date.data,
                            budget=form.budget.data,
                            goals=form.goals.data,
                            owner=current_user)
        db.session.add(campaign)
        db.session.commit()
        flash('Your Campaign has been created!', 'successs')
        return redirect(url_for('home'))
    return render_template('new_campaign.html', 
                           title='New Campaign', 
                           form=form, 
                           legend='New Campaign')

@app.route("/post/<int:campaign_id>")
@login_required
def campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()

    return render_template('campaign.html', title=campaign.title, campaign=campaign, ad_requests=ad_requests)



@app.route("/post/<int:campaign_id>/update", methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user:
        abort(403)
    form = PostCampaign()
    if form.validate_on_submit():
        campaign.title = form.title.data
        campaign.desc = form.desc.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.goals = form.goals.data
        db.session.commit()
        flash('Your Campaign has been Updated!', 'success')
        return redirect(url_for('campaign', campaign_id=campaign.id))
    
    elif request.method == 'GET':
        form.title.data = campaign.title
        form.desc.data = campaign.desc
        form.start_date.data = campaign.start_date
        form.end_date.data = campaign.end_date
        form.budget.data = campaign.budget
        form.goals.data = campaign.goals
    return render_template('new_campaign.html', 
                           title='Update Campaign', 
                           form=form,
                           legend='Update Campaign')

@app.route("/post/<int:campaign_id>/delete", methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user:
        abort(403)
    db.session.delete(campaign)
    db.session.commit()
    flash('Your Campaign has been Deleted!', 'success')
    return redirect(url_for('home'))
    

@app.route('/sponsor/<string:company_name>')
def sponsor_campaigns(company_name):
    page=request.args.get('page', 1, type=int)
    sponsor = Sponsor.query.filter_by(company_name=company_name).first_or_404()
    campaigns = Campaign.query.filter_by(owner=sponsor)\
        .order_by(Campaign.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('sponsor_campaigns.html', campaigns=campaigns, sponsor=sponsor)



@app.route("/adrequest/<int:ad_request_id>/accept", methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if current_user.is_sponsor() and ad_request.campaign.owner == current_user:
        ad_request.status = 'Accepted'
        db.session.commit()
        flash('Ad request accepted!', 'success')
    else:
        flash('You are not authorized to perform this action.', 'danger')
    return redirect(url_for('campaign', campaign_id=ad_request.campaign_id))

@app.route("/adrequest/<int:ad_request_id>/reject", methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if current_user.is_sponsor() and ad_request.campaign.owner == current_user:
        ad_request.status = 'Rejected'
        db.session.commit()
        flash('Ad request rejected!', 'success')
    else:
        flash('You are not authorized to perform this action.', 'danger')
    return redirect(url_for('campaign', campaign_id=ad_request.campaign_id))

@app.route('/adrequest/<int:ad_request_id>/cancel', methods=['POST'])
@login_required
def cancel_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.id:
        abort(403)  # Forbidden
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request has been canceled.', 'success')
    return redirect(url_for('account'))

@app.route('/request_ad/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
@influencer_required
def request_ad(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    form = AdRequestForm()
    
    if form.validate_on_submit():
        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=current_user.id,
            messages=form.messages.data,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status='Pending'
        )
        
        db.session.add(ad_request)
        db.session.commit()
        flash('Your ad request has been submitted!', 'success')
        return redirect(url_for('home'))
    return render_template('request_ad.html', title='Request Ad', form=form, campaign=campaign)

@app.route('/update_ad_request_status/<int:ad_request_id>/<action>', methods=['POST'])
@login_required
def update_ad_request_status(ad_request_id, action):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if current_user.is_sponsor() and ad_request.campaign.owner == current_user:
        if action == 'accept':
            ad_request.status = 'Accepted'
        elif action == 'reject':
            ad_request.status = 'Rejected'
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('account'))

        db.session.commit()
        flash(f'Ad request has been {ad_request.status.lower()}.', 'success')
    else:
        flash('You are not authorized to perform this action.', 'danger')
    
    return redirect(url_for('account'))

@app.route('/search_sponsors', methods=['GET'])
def search_sponsors():
    query = request.args.get('query', '')
    if query:
        sponsors = Sponsor.query.filter(Sponsor.company_name.ilike(f'%{query}%')).all()
    else:
        sponsors = []
    return render_template('search_results.html', results=sponsors, query=query, type='Sponsors')

@app.route('/search_influencers', methods=['GET'])
def search_influencers():
    query = request.args.get('query', '')
    if query:
        influencers = Influencer.query.filter(Influencer.name.ilike(f'%{query}%')).all()
    else:
        influencers = []
    return render_template('search_results.html', results=influencers, query=query, type='Influencers')

@app.route('/search_campaigns', methods=['GET'])
def search_campaigns():
    query = request.args.get('query', '')
    if query:
        campaigns = Campaign.query.filter(Campaign.title.ilike(f'%{query}%')).all()
    else:
        campaigns = []
    return render_template('search_results.html', results=campaigns, query=query, type='Campaigns')

@app.route('/influencer_profile/<int:influencer_id>')
def influencer_profile(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    accepted_ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id, status='Accepted').all()
    return render_template('influencer_profile.html', influencer=influencer, ad_requests=accepted_ad_requests)
