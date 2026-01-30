from flask import Blueprint, request, jsonify, render_template, current_app, make_response
from models import db, Entry
from scripts.import_initial_csv import normalize_handle

# Import draw controller and auth helpers
from Controllers.draw import drawWinners, resetSelection
from Controllers.auth import login_and_get_token, jwt_required


main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)


@main_bp.route('/')
def index():
    # Render the public landing / entry page
    try:
        return render_template('index.html')
    except Exception:
        # Fallback to a simple JSON message if templates are missing
        return jsonify({'message': 'Welcome to the event entry app'})


@main_bp.route('/submit', methods=['POST'])
def submit_entry():
    """Accept a new entry (form or JSON). Expected fields:
    - instagram_handle (string, required)
    - c1..c4 (booleans or values convertable to bool)
    """
    data = request.get_json() if request.is_json else request.form
    raw_handle = data.get('instagram_handle') or ''
    handle = normalize_handle(raw_handle)
    if not handle:
        return jsonify({'error': 'instagram_handle required'}), 400

    # Check for existing entry
    existing = Entry.query.filter_by(instagram_handle=handle).first()
    if existing:
        return jsonify({'message': 'already registered', 'handle': handle}), 200

    # New entry
    e = Entry(
        fname=data.get('fname', ''),
        lname=data.get('lname', ''),
        instagram_handle=handle,
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({'message': 'entry saved', 'handle': handle}), 201


@main_bp.route('/winners')
def winners_page():
    try:
        return render_template('winners.html')
    except Exception:
        return jsonify({'message': 'Winners page not available'}), 200


@main_bp.route('/api/winners')
def api_winners():
    winners = Entry.query.filter(Entry.is_selected == True).all()
    out = [{'handle': w.instagram_handle} for w in winners]
    return jsonify(out)


@main_bp.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'})


@admin_bp.route('/')
def admin_page():
    # Serve admin login/control panel
    try:
        return render_template('admin.html')
    except Exception:
        return jsonify({'message': 'Admin page not available'}), 200


@admin_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or request.form or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    token = login_and_get_token(username, password)
    if not token:
        return jsonify({'error': 'invalid credentials'}), 401
    resp = jsonify({'access_token': token})
    # set cookie for convenience (HttpOnly)
    resp.set_cookie('access_token', token, httponly=True, samesite='Lax')
    return resp


@admin_bp.route('/draw', methods=['POST'])
@jwt_required
def admin_draw():
    # Run the draw and return winners as JSON
    winners = drawWinners()
    out = [{'name': f"{w.fname} {w.lname}", 'handle': w.instagram_handle} for w in winners]
    return jsonify({'winners': out})


@admin_bp.route('/reset', methods=['POST'])
@jwt_required
def admin_reset():
    # Reset all selections so another draw can be run
    resetSelection()
    return jsonify({'message': 'Selection reset'})


@admin_bp.route('/clear-all', methods=['POST'])
@jwt_required
def admin_clear_all():
    # Delete ALL entries from the database - requires special password
    data = request.get_json() or {}
    password = data.get('password')
    
    # Check the special clear password
    clear_password = current_app.config.get('CLEAR_DB_PASSWORD')
    if password != clear_password:
        return jsonify({'error': 'Invalid clear password'}), 403
    
    try:
        Entry.query.delete()
        db.session.commit()
        return jsonify({'message': 'All entries deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/attendees', methods=['GET'])
@jwt_required
def admin_attendees():
    # Return all entries as JSON for admin UI
    entries = Entry.query.order_by(Entry.entered_at.desc()).all()
    out = [{
        'fname': e.fname,
        'lname': e.lname,
        'handle': e.instagram_handle,
        'is_selected': e.is_selected
    } for e in entries]
    return jsonify({'entries': out})


@admin_bp.route('/export', methods=['GET'])
@jwt_required
def admin_export():
    # Export all entries as CSV for audit
    import csv, io
    cols = ['id', 'fname', 'lname', 'instagram_handle', 'entered_at', 'is_selected']
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(cols)
    for e in Entry.query.order_by(Entry.id).all():
        writer.writerow([e.id, e.fname, e.lname, e.instagram_handle, e.entered_at, e.is_selected])
    output = make_response(si.getvalue())
    output.headers['Content-Type'] = 'text/csv'
    output.headers['Content-Disposition'] = 'attachment; filename=entries.csv'
    return output
