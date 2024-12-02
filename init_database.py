from google_sheets import get_google_sheet_data
from models import db, Climber, Level, Bloc, LevelBlocs

OFFSET_READ = '2'

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
        
def populate_climbers():
    sheet_name = 'Listes'
    climber_range = f'F{OFFSET_READ}:F'  # Range for climber names
    level_range = f'K{OFFSET_READ}:K'  # Range for climber levels
    club_range = f'J{OFFSET_READ}:J'

    climbers, success_climbers = get_google_sheet_data(climber_range, sheet_name)
    levels, success_levels = get_google_sheet_data(level_range, sheet_name)
    clubs, success_clubs = get_google_sheet_data(club_range, sheet_name)
    
    if success_climbers and success_levels and success_clubs and climbers and levels and clubs:
        for idx, climber_row in enumerate(climbers):
            if climber_row and climber_row[0].strip():  # Ensure the climber row isn't empty
                climber_name = climber_row[0]
                club_name = clubs[idx][0].strip() if idx < len(clubs) and clubs[idx] and clubs[idx][0].strip() else None
                
                level_name = levels[idx][0].strip() if idx < len(levels) and levels[idx] and levels[idx][0].strip() else None

                if climber_name and level_name:
                    level = Level.query.filter_by(name=level_name).first()
                    if not level:
                        print(f"Level '{level_name}' does not exist, skipping climber '{climber_name}'.")
                        continue

                    climber = Climber.query.filter_by(name=climber_name).first()
                    if not climber:
                        climber = Climber(name=climber_name, level=level, club=club_name)
                        db.session.add(climber)
                        
        db.session.commit()
        print("Climbers populated successfully.")
    else:
        print("Failed to populate climbers.")

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
                        print(f'Bloc {bloc_id} is required for level {level_names[idx_level]}')
                    else:
                        print(f'Warning: No matching level name for index {idx_level}. Check your data consistency.')
            
        #     bloc_id = bloc_ids[idx][0].strip() if idx < len(bloc_ids) and bloc_ids[idx][0].strip() else None
        #     if not bloc_id:
        #         print(f"Skipping empty Bloc ID at row {idx + 29}.")
        #         continue

        #     # Check for each level column if this bloc is required
        #     for col_idx, cell_value in enumerate(bloc_row[:len(level_names)]):
        #         if cell_value == "1":  # If "1", this bloc is associated with the corresponding level
        #             level_name = level_names[col_idx]

        #             # Ensure the level exists in the database
        #             level = Level.query.filter_by(circuit=level_name).first()
        #             if not level:
        #                 print(f"Level '{level_name}' does not exist. Skipping association for Bloc ID '{bloc_id}'.")
        #                 continue
        #             else:
        #                 print(f'success {level_name}')

        #             # Ensure the bloc exists in the database
        #             bloc = Bloc.query.filter_by(bloc_id=bloc_id).first()
        #             if not bloc:
        #                 bloc = Bloc(bloc_id=bloc_id)
        #                 db.session.add(bloc)
        #                 db.session.commit()

        #             # Check if the association already exists
        #             existing_association = LevelBlocs.query.filter_by(level_id=level.id, bloc_id=bloc.id).first()
        #             if not existing_association:
        #                 # Add the level-bloc association
        #                 level_bloc = LevelBlocs(level_id=level.id, bloc_id=bloc.id)
        #                 db.session.add(level_bloc)
        
        # db.session.commit()
        print("LevelBlocs populated successfully.")
    else:
        print("Failed to fetch data from Google Sheet.")
