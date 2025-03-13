from flask import Flask, request, jsonify, Blueprint, render_template
from climb_contest import db
from climb_contest.google_sheets import google_sheet
from climb_contest.database_handler import handler
from climb_contest.google_sheets_reader import populate_climbers
import threading

main = Blueprint("main", __name__)  # Create a Blueprint named main

# Use to check if the climber bib is already registered in the database
@main.route('/api/v2/contest/climber/name', methods=['POST'])
def check_climber():
    data = request.get_json()
    climber_bib = data.get('id')
    
    if not (climber_bib):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    try:
        try:
            climber = handler.get_climber_by_bib(climber_bib)
        except ValueError as message:
            print(f'climber_id = {climber_bib} not present in DB, try to refresh it')
            # In that case pull the google sheet again to check if it's added in the meantime
            populate_climbers(google_sheet, db)
            try:
                climber = handler.get_climber_by_bib(climber_bib)
            except ValueError as message:
                print(message)
                return jsonify({'success': False, 'message': message}), 400
            
        print(f'Check climber bib = {climber.bib}, name = {climber.name}')
            
        return jsonify({
            'success': True,
            'message': 'Climber registered successfully',
            'id': climber.name
        }), 201
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'}), 400
    
# Use to check if the bloc tag is already registered in the database
@main.route('/api/v2/contest/bloc/name', methods=['POST'])
def check_bloc_tag():
    data = request.get_json()
    bloc_tag = data.get('id')
    
    if not (bloc_tag):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    print(f'Check bloc tag = {bloc_tag}')
    
    try:
        try:
            bloc = handler.get_bloc_by_tag(bloc_tag)
        except ValueError as message:
            print(message)
            return jsonify({'success': False, 'message': message}), 400
        
        return jsonify({
            'success': True,
            'message': 'Bloc registered successfully',
            'id': bloc.tag
            }), 201

    except Exception as e:
        db.session.rollback()
        message = "An error occurred: {e}"
        print(message)
        return jsonify({'success': False, 'message': 'An error occurred'}), 400

# Use by application to register a success of a climber on a bloc (the only API that write)
@main.route('/api/v2/contest/success', methods=['POST'])
def register_success():
    data = request.get_json()
    climber_bib = data.get('bib')
    bloc_tag = data.get('bloc')
    
    if not (climber_bib and bloc_tag):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    try:
        try:
            climber = handler.get_climber_by_bib(climber_bib)
            bloc = handler.get_bloc_by_tag(bloc_tag)
        except ValueError as message:
            print(message)
            return jsonify({'success': False, 'message': message}), 400
            
        print(f'===> Success climber: {climber.name} | {climber.bib} | {bloc_tag}')

        update_google_sheet(climber, bloc)
        
        handler.add_success(climber, bloc)
        
        return jsonify({
            'success': True,
            'message': 'Well done'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        message = f'An error occurred: {e}'
        print(message)
        return jsonify({'success': False, 'message': 'An error occurred'}), 400

def update_google_sheet(climber, bloc):
    if not climber or not bloc or not climber.bib or not bloc.number:
        print('Error missing argument')
        
    # Update Google Sheet
    thread = threading.Thread(target=google_sheet.update_google_sheet, args=(climber.bib, int(bloc.number), climber.bib, bloc.number))
    thread.start()

@app.route('/test')
def test_page():
    """Page web pour tester les 3 endpoints."""
    return render_template('test_api.html')

@app.route('/api/v2/contest/options', methods=['GET'])
def get_options():
    """Retourne la liste des climbers (name + bib) et blocs (tag) pour remplir les dropdowns."""
    try:
        climbers = Climber.query.all()
        blocs = Bloc.query.all()
        climbers_list = [{'name': c.name, 'bib': c.bib} for c in climbers]
        blocs_list = [{'tag': b.tag} for b in blocs]
        return jsonify({'climbers': climbers_list, 'blocs': blocs_list}), 200
    except Exception as e:
        print(f"An error occurred while getting options: {e}")
        return jsonify({'climbers': [], 'blocs': []}), 500
    
@app.route('/')
def index():
    return render_template('index.html')

