from flask import Blueprint, render_template, request, redirect, session, flash
from ..repositories.user_repo import user_has_profile
from ..repositories.profile_repo import insert_profile, fetch_profile_with_role
from ..repositories.vendor_repo import fetch_vendor

vendor_bp = Blueprint('vendor', __name__)

@vendor_bp.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    if not session.get('logged_in'):
        return redirect('/')
    user_id = session.get('user_id')
    if user_has_profile(user_id):
        return redirect('/feed')
    if request.method == 'POST':
        bio = request.form.get('bio') or None
        location = request.form.get('location') or None
        avatar_url = request.form.get('avatar_url') or None
        if insert_profile(user_id, bio, location, avatar_url):
            return redirect('/feed')
        flash('Could not save profile.')
    return render_template('profile.html')

@vendor_bp.route('/profile')
def own_profile():
    if not session.get('logged_in'):
        return redirect('/')
    user_id = session.get('user_id')
    data = fetch_profile_with_role(user_id)
    if not user_has_profile(user_id):
        return redirect('/complete_profile')
    return render_template('view_profile.html', user=data)

@vendor_bp.route('/profile/<int:vendor_id>')
def vendor_profile(vendor_id: int):
    vendor = fetch_vendor(vendor_id)
    if not vendor:
        flash('Vendor not found.')
        return redirect('/feed')
    return render_template('view_profile.html', user=vendor)