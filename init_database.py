from google_sheets import get_google_sheet_data
from models import db, Climber, Level

OFFSET_READ = '2'

def populate_levels():
    range_ = "A5:A"  # Range for levels
    values, success = get_google_sheet_data(range_)
    if success and values:
        for row in values:
            if row:  # Ensure the row isn't empty
                level_name = row[0]
                level = Level.query.filter_by(name=level_name).first()
                if not level:
                    level = Level(name=level_name)
                    db.session.add(level)
            else:  # At the first empty, store all level in DB and finish
                db.session.commit()
                print("Levels populated successfully.")
                return
    else:
        print("Failed to populate levels.")
        
def populate_climbers():
    climber_range = f'F{OFFSET_READ}:F'  # Range for climber names
    level_range = f'K{OFFSET_READ}:K'  # Range for climber levels
    club_range = f'J{OFFSET_READ}:J'

    climbers, success_climbers = get_google_sheet_data(climber_range)
    levels, success_levels = get_google_sheet_data(level_range)
    clubs, success_clubs = get_google_sheet_data(club_range)
    
    if success_climbers and success_levels and success_clubs and climbers and levels and clubs:
        for idx, climber_row in enumerate(climbers):
            if climber_row and climber_row[0].strip():  # Ensure the climber row isn't empty
                climber_name = climber_row[0]
                club_name = clubs[idx][0].strip() if idx < len(levels) and clubs[idx] and clubs[idx][0].strip() else None
                
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
