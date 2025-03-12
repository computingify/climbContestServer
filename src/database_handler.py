from src import db
from src.models import Climber, Bloc, Success
from datetime import datetime

"""Database handler: used to handle database operations"""
class DatabaseHandler:

    def add_success(self, climber, bloc):
        """Add success in the database"""
        if self.is_bloc_tag_exist(bloc.tag) and self.is_climber_bib_exist(climber.bib):
            try:
                success = Success(
                    climber_id=climber.id,
                    bloc_id=bloc.id,
                    timestamp=datetime.now(),
                )
                db.session.add(success)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Failed to record success: {e}")
        
    def is_bloc_tag_exist(self, bloc_tag):
        """Check if the bloc tag is already registered in the database"""
        try: 
            bloc = self.get_bloc_by_tag(bloc_tag)
            return True
        except ValueError as message:
            print(message)
            return False
        
    def get_bloc_by_tag(self, bloc_tag):
        """Get bloc by tag"""
        bloc = Bloc.query.filter_by(tag=bloc_tag).first()
        if not bloc or not bloc.tag:
            raise ValueError(f"Bloc with tag {bloc_tag} not found")
        return bloc
    
    def is_climber_bib_exist(self, climber_bib):
        """Check if the climber bib is already registered in the database"""
        try:
            climber = self.get_climber_by_bib(climber_bib)
            return True
        except ValueError as message:
            print(message)
            return False
    
    def get_climber_by_bib(self, climber_bib):
        """Get climber by bib"""
        climber = Climber.query.filter_by(bib=climber_bib).first()
        if not climber or not climber.name:
            if(not climber):
                raise ValueError(f"Climber bib = {climber_bib} not present in DB")
            else:
                raise ValueError(f"Climber bib = {climber_bib} Doesn\'t have setted name")
        return climber
