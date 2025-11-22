from flask import Flask, request, jsonify, Blueprint, render_template
from climb_contest import db
from climb_contest.google_sheets import google_sheet
from climb_contest.database_handler import handler
from climb_contest.google_sheets_reader import populate_climbers
from climb_contest.results.processor import processor
import threading

main = Blueprint("main", __name__)  # Create a Blueprint named main

# Get all climbers for the contest
@main.route('/api/v2/contest/climber/all', methods=['GET'])
def get_climber_all():
    """Retourne la liste des climbers (name + bib) pour remplir les dropdowns."""
    try:
        climbers = handler.get_all_climbers()
        climbers_list = [{'name': c.name, 'bib': c.bib} for c in climbers]
        return jsonify({'climbers': climbers_list}), 200
    except Exception as e:
        print(f"An error occurred while getting all climbers: {e}")
        return jsonify({'climbers': []}), 500

# Use to check if the climber bib is already registered in the database
# {
#     "id": "11"
# }
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

# Get the ranking of a specific climber based on their bib
# /api/v2/contest/climber/ranking?bib=11
@main.route('/api/v2/contest/climber/ranking', methods=['GET'])
def get_climber_classement():
    try:
        climber_bib = request.args.get('bib')
        # Récupère toutes les catégories présentes dans la base
        climber_category = handler.get_climber_by_bib(climber_bib).category

        results = processor.run(climber_category)
        
        # Find the specific climber in the results
        for result in results:
            if int(result['bib']) == int(climber_bib):
                result['rank'] = results.index(result) + 1
                return jsonify(result), 200

        return jsonify({"warning", "No result for climber bib: {climber_bib}"}), 400

    except (ValueError, TypeError, KeyError):
        print(f"Error converting bib to int or missing key")
        return jsonify({"error": "Invalid bib format"}), 400
    except Exception as e:
        print(f"An error occurred while computing climber_ranking: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Use to check if a climber can do a bloc
# {
#     "bib": "11",
#     "bloc": "Z1"
# }
@main.route('/api/v2/contest/climber/bloc', methods=['POST'])
def check_climber_bloc():
    data = request.get_json()
    climber_bib = data.get('bib')
    bloc_tag = data.get('bloc')
    
    if not (climber_bib and bloc_tag):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    print(f'Check climber bib = {climber_bib} for bloc tag = {bloc_tag}')
    
    is_ok = handler.is_bloc_for_this_climber(climber_bib, bloc_tag)
    
    print(f'is_ok = {is_ok}')
            
    return jsonify({
        'success': True if is_ok else False,
        'message': f'The bloc {bloc_tag} is for the climber ‘{climber_bib}’' if is_ok else f'The bloc {bloc_tag} is not for the climber ‘{climber_bib}’'
    }), 201 if is_ok else 400

# Use to get all blocs associated to a climber to fill dropdowns
# /api/v2/contest/climber/blocs?bib=11
@main.route('/api/v2/contest/climber/blocs', methods=['GET'])
def get_climber_blocs():
    """Return all bloc associated to a climber to fill dropdowns."""
    bib = request.args.get('bib')
    if not bib:
        return jsonify({'error': 'Missing bib parameter'}), 400
    try:
        blocs = handler.get_all_blocs_for_climber(bib)
        blocs_list = [{'tag': b.tag} for b in blocs]
        return jsonify(blocs_list), 200
    except Exception as e:
        print(f"Error in get_climber_blocs: {e}")
        return jsonify({'error': str(e)}), 400


# Get all blocs for the contest
@main.route('/api/v2/contest/bloc/all', methods=['GET'])
def get_bloc_all():
    """Retourne la liste des blocs (tag) pour remplir les dropdowns."""
    try:
        blocs = handler.get_all_blocs()
        blocs_list = [{'tag': b.tag} for b in blocs]
        return jsonify({'blocs': blocs_list}), 200
    except Exception as e:
        print(f"An error occurred while getting all blocs: {e}")
        return jsonify({'blocs': []}), 500

# Use to check if the bloc tag is already registered in the database
# {
#     "id": "Z1"
# }
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


# Use this API endpoint to get all available categories for the contest
@main.route('/api/v2/contest/categories/all', methods=['GET'])
def get_all_categories():
    """Return all available categories for the contest."""
    try:
        categories = handler.get_all_climbers_categories()
        return jsonify({'categories': categories}), 200
    except Exception as e:
        print(f"An error occurred while getting all categories: {e}")
        return jsonify({'categories': []}), 500

# Use this API endpoint to get all climbers associate to a category in alphabetic order
# /api/v2/contest/category/climbers?category=U11 F
@main.route('/api/v2/contest/categories/climbers', methods=['GET'])
def get_all_climbers_for_category():
    """Return all climbers for a given category in alphabetic order."""
    category = request.args.get('category')
    if not category:
        return jsonify({'error': 'Missing category parameter'}), 400
    try:
        climbers = handler.get_all_climbers_for_category(category)
        climbers_list = [{'name': c.name, 'bib': c.bib} for c in climbers]
        return jsonify({'climbers': climbers_list}), 200
    except Exception as e:
        print(f"Error in get_all_climbers_for_category: {e}")
        return jsonify({'error': str(e)}), 400

# Use by application to register a success of a climber on a bloc (the only API that write)
# {
#     "bib": "11",
#     "bloc": "Z1"
# }
@main.route('/api/v2/contest/success', methods=['POST'])
def register_success():
    data = request.get_json()
    climber_bib = data.get('bib')
    bloc_tag = data.get('bloc')
    
    if not (climber_bib and bloc_tag):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    ok = handler.is_bloc_for_this_climber(climber_bib, bloc_tag)
    if not ok:
        message = f'The bloc {bloc_tag} is not for the climber ‘{climber_bib}’'
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

# Get all the contest ranking for all categories
@main.route('/api/v2/contest/ranking_by_categories', methods=['GET'])
def get_ranking_by_categories():
    try:
        classement = {}
        # Récupère toutes les catégories présentes dans la base
        categories = handler.get_all_climbers_categories()

        for category in categories:
            # Appelle la fonction run pour chaque catégorie
            results = processor.run(category)
            classement[category] = results

        return jsonify(classement), 200

    except Exception as e:
        print(f"An error occurred while computing ranking_by_categories: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

    
    
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/results')
def results_page():
    return render_template('results.html')

@main.route('/test')
def test_page():
    """Page web pour tester les 3 endpoints."""
    return render_template('test_api.html')

def update_google_sheet(climber, bloc):
    if not climber or not bloc or not climber.bib or not bloc.number:
        print('Error missing argument')
        
    # Update Google Sheet
    thread = threading.Thread(target=google_sheet.update_google_sheet, args=(climber.bib, int(bloc.number), climber.bib, bloc.number))
    thread.start()

