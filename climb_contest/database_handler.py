from .extensions import db
from climb_contest.models import Climber, Bloc, Success
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
    
    def is_bloc_for_this_climber(self, climber_bib, bloc_tag):
        """Check if a climber bib should do a bloc based on climber category"""
        try:
            climber = self.get_climber_by_bib(climber_bib)
            bloc = self.get_bloc_by_tag(bloc_tag)
            return climber in bloc.categories
            
        except ValueError as message:
            print(message)
            return False
        
    def get_all_climbers_categories(self):
        """Get all climbers categories from the database and orders them"""
        categories = db.session.query(Climber.category).distinct().order_by(Climber.category).all()
        return [category[0] for category in categories]

    def get_all_blocs(self):
        """Get all blocs from the database"""
        return Bloc.query.all()
    
    def get_all_climbers(self):
        """Get all climbers from the database"""
        return Climber.query.order_by(Climber.name).all()
    
    def get_all_climbers_for_category(self, category):
        """Get all climbers associated to a category to fill dropdowns."""
        climbers = Climber.query.filter_by(category=category).order_by(Climber.name).all()
        return climbers
    
    def get_all_blocs_for_climber(self, climber_bib):
        """Get all blocs associated to a climber to fill dropdowns."""
        climber = self.get_climber_by_bib(climber_bib)
        return climber.blocs
    
handler = DatabaseHandler()