from flask import Flask, request, jsonify
from models import db, Climber, Bloc, UUIDMapping
from google_sheets import update_google_sheet
from google_sheets_reader import populate_bloc, populate_climbers
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/api/v1/contest/climber', methods=['POST'])
def register_climber():
    data = request.get_json()
    climber_id = data.get('id')
    uuid = data.get('uuid')
    
    if not (climber_id and uuid):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400

    try:
        climber = Climber.query.filter_by(bib=climber_id).first()
        if not climber.bib:
            message = 'Unregistered climber bib'
            print(message)
            return jsonify({'success': False, 'message': message}), 400
        
        print(f'climber_id = {climber.name} | uuid = {uuid}')

        mapping = UUIDMapping.query.filter_by(uuid=uuid).first()
        if not mapping:
            mapping = UUIDMapping(uuid=uuid, climber_bib=climber.bib)
            db.session.add(mapping)
        else:
            mapping.climber_bib = climber.bib

        db.session.commit()
        
        try_to_update_google_sheet(mapping)
        
        return jsonify({
            'success': True,
            'message': 'Climber registered successfully',
            'id': climber.name
        }), 201
    
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'}), 400

@app.route('/api/v1/contest/bloc', methods=['POST'])
def register_bloc():
    data = request.get_json()
    bloc_id = data.get('id')
    uuid = data.get('uuid')
    
    print(f'bloc_id = {bloc_id} | uuid = {uuid}')

    if not (bloc_id and uuid):
        message = 'Missing data'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    bloc = Bloc.query.filter_by(tag=bloc_id).first()
    if not bloc or not bloc.tag:
        message = 'Unregistered bloc tag'
        print(message)
        return jsonify({'success': False, 'message': message}), 400
    
    # try:
    mapping = UUIDMapping.query.filter_by(uuid=uuid).first()
    if not mapping:
        mapping = UUIDMapping(uuid=uuid, bloc_number=bloc.number)
        db.session.add(mapping)
    else:
        mapping.bloc_number = bloc.number
        
    db.session.commit()
    
    try_to_update_google_sheet(mapping)
    
    return jsonify({
        'success': True,
        'message': 'Bloc registered successfully',
        'id': bloc.tag
        }), 201

    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     db.session.rollback()
    #     return jsonify({'success': False, 'message': 'An error occurred'}), 400
    

def try_to_update_google_sheet(mapping):
    if mapping and mapping.bloc_number and mapping.climber_bib:
        climber = Climber.query.filter_by(bib=mapping.climber_bib).first()
        bloc = Bloc.query.filter_by(number=mapping.bloc_number).first()
        
        if not climber or not bloc or not climber.bib or not bloc.number:
            print('ERROR')
            
        print(f'climber = {climber.name}   Bloc = {bloc.tag}')
        
        # Update Google Sheet
        thread = threading.Thread(target=write_google_sheet, args=(climber, bloc, mapping))
        thread.start()
                
def write_google_sheet(climber, bloc, mapping):
    # Update Google Sheet
    result, state = update_google_sheet(climber.bib, int(bloc.number), climber.bib, bloc.number)

    if state is True:
        # Remove entries from the database after successful update
        with app.app_context():
            if mapping:
                db.session.delete(mapping)
            db.session.commit()
            
def sync_data_from_google_sheet():
    with app.app_context():
        populate_bloc()
        populate_climbers()

# Launch the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    sync_data_from_google_sheet()
    
    # Path to your SSL certificate and private key
    ssl_context = ('security/cert.pem', 'security/key.pem')
    app.config["DEBUG"] = True
    app.run(host='0.0.0.0', port=5007, ssl_context=ssl_context)