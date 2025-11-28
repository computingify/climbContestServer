from sqlalchemy.dialects.postgresql import insert
from climb_contest.models import Climber, Bloc, climber_category_bloc

def populate_bloc(google_sheet, db):
    sheet_name = 'Plan'
    plan_lines_range = "D28:Y"  # get all google sheet Plan line, in each line we have: zone letter | bloc number in this zone | difficulty color | bloc color | is for Cat 1 | empty | is for Cat 2 .... | bloc id

    # Fetch data from Google Sheet
    plan_lines, success_plan_lines = google_sheet.get_google_sheet_data(plan_lines_range, sheet_name)

    if success_plan_lines:
        if not plan_lines:
            print(f'Invalid or empty data fetched from Google Sheet. \nplan_lines={plan_lines}')
            return
        # Extract the category list from the first line of plan_lines
        categories = plan_lines[0][0:14]
        # Start processing from the second element of plan_lines
        plan_lines = plan_lines[1:]
        
        for line in plan_lines:
            if 17 <= len(line):   # The google sheet line shall have 22 element because the 17th is the bloc id which mendatory in other case that's because the qr_code isn't associated to a bloc_id
                # Extract qr_code by concatenating the 1st and last values to have the zone + the bloc id
                #  Zone letter (M) + number (J19)
                qr_code = line[0] + line[16]

                # Extract bloc_id as the latest value in the array
                #       Number in result sheet (54)
                bloc_id = line[-1]
                
                # print(f'qr_code = {qr_code} | bloc_id = {bloc_id}')
                
                # Handle Bloc creation
                if qr_code and bloc_id:
                    bloc = Bloc.query.filter_by(tag=qr_code, number=bloc_id).first()
                    if not bloc:
                        bloc = Bloc(tag=qr_code, number=bloc_id)
                        db.session.add(bloc)
                        
                    # Handle climber_category_bloc association table creation
                    for idx in range(5, 14):
                        is_associated_to_category = line[idx]
                        if is_associated_to_category:
                            category = categories[idx]
                            if category:
                                # 1. Définir les valeurs pour Filles (F)
                                insert_f = insert(climber_category_bloc).values(category=category + " F", bloc_id=bloc_id)
                                # 2. Appliquer ON CONFLICT DO NOTHING
                                on_conflict_f = insert_f.on_conflict_do_nothing(index_elements=[climber_category_bloc.c.category, climber_category_bloc.c.bloc_id])
                                db.session.execute(on_conflict_f)

                                # 3. Définir les valeurs pour Garçons (H)
                                insert_h = insert(climber_category_bloc).values(category=category + " H", bloc_id=bloc_id)
                                # 4. Appliquer ON CONFLICT DO NOTHING
                                on_conflict_h = insert_h.on_conflict_do_nothing(index_elements=[climber_category_bloc.c.category, climber_category_bloc.c.bloc_id])
                                db.session.execute(on_conflict_h)
                else:
                    print(f'Error in googleSheet extraction data of qr_code = {qr_code} | bloc_id = {bloc_id}')
                
        db.session.commit()
        
        print("LevelBlocs populated successfully.")
    else:
        print("Failed to fetch data from Google Sheet.")
        
def populate_climbers(google_sheet, db):
    OFFSET_READ = '2'
    sheet_name = 'Listes'
    lines_range = f'F{OFFSET_READ}:K'

    lines, success_read = google_sheet.get_google_sheet_data(lines_range, sheet_name)
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
        