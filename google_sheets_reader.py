from google_sheets import get_google_sheet_data
# from models import db, Climber, Level, Bloc, LevelBlocs, ClimberBlocsReference
from models import db, Climber, Bloc

def populate_bloc():
    sheet_name = 'Plan'
    plan_lines_range = "D29:T"  # get all google sheet Plan line, in each line we have: zone letter | bloc number in this zone | difficulty color | bloc color | is for Cat 1 | empty | is for Cat 2 .... | bloc id

    # Fetch data from Google Sheet
    plan_lines, success_plan_lines = get_google_sheet_data(plan_lines_range, sheet_name)

    if success_plan_lines:
        if not plan_lines:
            print(f'Invalid or empty data fetched from Google Sheet. \nplan_lines={plan_lines}')
            return
        
        for line in plan_lines:
            if 17 == len(line):   # The google sheet line shall have 17 element because the 17th is the bloc id which mendatory in other case that's because the qr_code isn't associated to a bloc_id
                # Extract qr_code by concatenating the 1st and last values to have the zone + the bloc id
                qr_code = line[0] + line[-1]

                # Extract bloc_id as the latest value in the array
                bloc_id = line[-1]
                
                # print(f'qr_code = {qr_code} | bloc_id = {bloc_id}')
                
                if qr_code and bloc_id:
                    bloc = Bloc.query.filter_by(tag=qr_code, number=bloc_id).first()
                    if not bloc:
                        bloc = Bloc(tag=qr_code, number=bloc_id)
                        db.session.add(bloc)
                else:
                    print(f'Error in googleSheet extraction data of qr_code = {qr_code} | bloc_id = {bloc_id}')
                
        db.session.commit()
        
        print("LevelBlocs populated successfully.")
    else:
        print("Failed to fetch data from Google Sheet.")
        
def populate_climbers():
    OFFSET_READ = '2'
    sheet_name = 'Listes'
    lines_range = f'F{OFFSET_READ}:K'

    lines, success_read = get_google_sheet_data(lines_range, sheet_name)
    # print(f'lines = {lines}')
    
    if success_read and lines:
        for idx, line in enumerate(lines):
            # print(f'line = {line}')
            if line and 6 == len(line):
                climber_name = line[0]
                bib = line[1] if line[1] else None
                club_name = line[4] if line[4] else None
                category = line[5] if line[5] else None
                
                if climber_name:
                    climber = Climber.query.filter_by(name=climber_name).first()
                    if not climber:
                        climber = Climber(name=climber_name, bib=bib, club=club_name, category=category)
                        db.session.add(climber)
                        
        db.session.commit()
        print("Climbers populated successfully.")
    else:
        print("Failed to populate climbers.")
        
"""
def populate_levels():
    sheet_name = 'Listes'
    range_level = "A5:A"  # Range for levels
    range_circuit = "B5:B"
    values_level, success = get_google_sheet_data(range_level, sheet_name)
    values_circuit, success_circuit = get_google_sheet_data(range_circuit, sheet_name)
    if success and success_circuit and values_level and values_circuit:
        for idx, level_row in enumerate(values_level):
            if level_row:  # Ensure the row isn't empty
                level_name = level_row[0]
                circuit_name = values_circuit[idx][0].strip() if idx < len(values_circuit) and values_circuit[idx] and values_circuit[idx][0].strip() else None
                
                level = Level.query.filter_by(name=level_name, circuit=circuit_name).first()
                if not level:
                    level = Level(name=level_name, circuit=circuit_name)
                    db.session.add(level)
            else:  # At the first empty, store all level in DB and finish
                db.session.commit()
                print("Levels populated successfully.")
                return
    else:
        print("Failed to populate levels.")

def populate_level_blocs():
    sheet_name = 'Plan'
    level_names_range = "J28:S28"  # Level names range
    bloc_ids_range = "T29:T"  # Bloc IDs range
    level_blocs_range = "J29:S"  # Level-bloc matrix range (1 if the bloc is required for the level)

    # Fetch data from Google Sheet
    level_names, success_level_names = get_google_sheet_data(level_names_range, sheet_name)
    bloc_ids, success_bloc_ids = get_google_sheet_data(bloc_ids_range, sheet_name)
    level_blocs, success_level_blocs = get_google_sheet_data(level_blocs_range, sheet_name)

    # print('Level name - bloc id - level bloc')
    # for idx, bloc_id in enumerate(bloc_ids):
    #     print(f'{level_names[idx]} - {bloc_id} - {level_blocs[idx]}')
    # return

    if success_level_names and success_bloc_ids and success_level_blocs:
        if not level_names or not bloc_ids or not level_blocs:
            print(f'Invalid or empty data fetched from Google Sheet. level_names={level_names}, bloc_ids={bloc_ids}, level_blocs={level_blocs}')
            return

        # Flatten level names row
        level_names = level_names[0]
        
        # Process each bloc-row in the level-bloc matrix
        for idx_line, bloc_id_row in enumerate(bloc_ids):
            if not bloc_id_row:  # Skip empty rows
                continue
            bloc_id = bloc_id_row[0]  # Bloc ID is the first (and only) element in the row
            level_bloc_row = level_blocs[idx_line]  # Get the level-bloc data for this bloc

            for idx_level, is_required in enumerate(level_bloc_row):
                if is_required == '1':  # If this level requires the bloc
                    if idx_level < len(level_names):
                        circuit = level_names[idx_level]
                        # print(f'Bloc {bloc_id} is required for level {circuit}')
                        # Ensure the bloc exists in the database
                        bloc = Bloc.query.filter_by(bloc_id=bloc_id).first()
                        if not bloc:
                            bloc = Bloc(bloc_id=bloc_id)
                            db.session.add(bloc)
                            # print(f'Write in bloc db = {bloc}')
                            
                        # Check if the level is already stored
                        levels = Level.query.filter_by(circuit=circuit)
                        for idx, level in enumerate(levels):
                            # print(f'for circuit: {circuit} level.name = {level.name}')
                            # Check if the association already exists
                            existing_association = LevelBlocs.query.filter_by(level_id=level.id, bloc_id=bloc.id).first()
                            if not existing_association:
                                # Add the level-bloc association
                                level_bloc = LevelBlocs(level_id=level.id, bloc_id=bloc.id)
                                db.session.add(level_bloc)
                    else:
                        print(f'Warning: No matching level name for index {idx_level}. Check your data consistency.')
                
        db.session.commit()
        print("LevelBlocs populated successfully.")
    else:
        print("Failed to fetch data from Google Sheet.")
        
def populate_climber_blocs():
    # Query both ID and Level ID of all climbers
    climbers = Climber.query.with_entities(Climber.id, Climber.level_id).all()

    if not climbers:
        print(f"Error: Climber data base is empty")
        return []
    
    # Loop through each result
    for climber_id, level_id in climbers:
        level_blocs = LevelBlocs.query.filter_by(level_id=level_id).all()
        
        # Extract all bloc_ids
        bloc_ids = [lb.bloc_id for lb in level_blocs]
        if not bloc_ids:
            print(f"Error: bloc ID associate to climb: {climber_id} and circuit: {level_id}")
            return []
        
        for bloc_id in bloc_ids:
            climber_blocs = ClimberBlocsReference(climber_id=climber_id, bloc_id=bloc_id)
            db.session.add(climber_blocs)
            
    db.session.commit()
    print("ClimberBlocsReference populated successfully.")
"""
    