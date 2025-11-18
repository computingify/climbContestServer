from climb_contest.results import processor
from climb_contest.extensions import db
from climb_contest.models import Climber, Bloc, Success

processor = processor.Processor({"db": db})

def test_process(app):
    with app.app_context():
        # Create a new climber
        climber1_U16H = Climber(
            name="John Doe",
            bib=1,
            club="Club A",
            category="U16 H"
        )
        climber2_U16H = Climber(
            name="Serge Doe",
            bib=2,
            club="Club B",
            category="U16 H"
        )
        climber3_U16F = Climber(
            name="Alce Smith",
            bib=5,
            club="Club A",
            category="U16 F"
        )
        
        bloc = Bloc(tag="A1", number="1")

        # Add and commit to the database
        db.session.add_all({climber1_U16H, climber2_U16H, climber3_U16F, bloc})
        db.session.commit()
        
        success = Success(
            climber_id=climber1_U16H.id,
            bloc_id=bloc.id,
        )

        # Add and commit to the database
        db.session.add(success)
        db.session.commit()
        
        categories_to_update = {"U16 F", "U16 H"}
        try:
            processor.run(categories_to_update)
        except Exception as e:
            print(f"Processor failed: {e}")
            assert False, f"Processor failed: {e}"

        # Vérification simple : il y a bien des grimpeurs pour chaque catégorie
        for cat in categories_to_update:
            climbers = Climber.query.filter_by(category=cat).all()
            assert len(climbers) > 0, f"No climber found for category {cat}"