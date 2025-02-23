from src.models import db, Climber, Bloc

"""Database handler: used to handle database operations"""
class DatabaseHandler:

    def add_success(self, climber, bloc):
        """Add success in the database"""
        db.session.add_all([climber, bloc])
        db.session.commit()
        
    def get_bloc_by_tag(self, bloc_tag):
        """Get bloc by tag"""
        bloc = Bloc.query.filter_by(tag=bloc_tag).first()
        if not bloc or not bloc.tag:
            raise ValueError(f"Bloc with tag {bloc_tag} not found")
        return bloc
    
    def get_climber_by_bib(self, climber_bib):
        """Get climber by bib"""
        climber = Climber.query.filter_by(bib=climber_bib).first()
        if not climber or not climber.name:
            if(not climber):
                raise ValueError(f"Climber bib = {climber_bib} not present in DB")
            else:
                raise ValueError(f"Climber bib = {climber_bib} Doesn\'t have setted name")
        return climber
    