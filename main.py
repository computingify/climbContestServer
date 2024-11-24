from flask import Flask, request, jsonify
from models import db, Climber, Bloc, UUIDMapping
from google_sheets import update_google_sheet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/api/v1/contest/climber', methods=['POST'])
def register_climber():
    data = request.get_json()
    climber_name = data.get('id')
    uuid = data.get('uuid')

    if not (climber_name and uuid):
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    climber = Climber.query.filter_by(name=climber_name).first()
    if not climber:
        climber = Climber(name=climber_name)
        db.session.add(climber)

    mapping = UUIDMapping.query.filter_by(uuid=uuid).first()
    if not mapping:
        mapping = UUIDMapping(uuid=uuid, climber_name=climber_name)
        db.session.add(mapping)
    elif not mapping.climber_name:
        mapping.climber_name = climber_name
    else:
        return jsonify({'success': False, 'message': 'wrong UUID'}), 400

    db.session.commit()
    
    try_to_update_google_sheet(mapping)
    
    return jsonify({'success': True, 'message': 'Climber registered successfully'}), 201

@app.route('/api/v1/contest/bloc', methods=['POST'])
def register_bloc():
    data = request.get_json()
    bloc_id = data.get('id')
    uuid = data.get('uuid')

    if not (bloc_id and uuid):
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    bloc = Bloc.query.filter_by(bloc_id=bloc_id).first()
    if not bloc:
        bloc = Bloc(bloc_id=bloc_id)
        db.session.add(bloc)

    mapping = UUIDMapping.query.filter_by(uuid=uuid).first()
    if not mapping:
        mapping = UUIDMapping(uuid=uuid, bloc_id=bloc_id)
        db.session.add(mapping)
    elif not mapping.bloc_id:
        mapping.bloc_id = bloc_id
    else:
        return jsonify({'success': False, 'message': 'wrong UUID'}), 400
    
    db.session.commit()
    
    try_to_update_google_sheet(mapping)
    
    return jsonify({'success': True, 'message': 'Bloc registered successfully'}), 201

def try_to_update_google_sheet(mapping):
    if mapping.bloc_id and mapping.climber_name:
        climber = Climber.query.filter_by(name=mapping.climber_name).first()
        bloc = Bloc.query.filter_by(bloc_id=mapping.bloc_id).first()
        # Update Google Sheet
        result, state = update_google_sheet(climber.id, bloc.id, climber.name, bloc.bloc_id)

        if state is True:
            # Remove entries from the database after successful update
            if climber:
                db.session.delete(climber)
            if bloc:
                db.session.delete(bloc)
            if mapping:
                db.session.delete(mapping)
            db.session.commit()
        
# Launch the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.config["DEBUG"] = True
    app.run(host='0.0.0.0', port=5007)