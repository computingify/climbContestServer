from climb_contest.results.processor import processor
from climb_contest.extensions import db
from climb_contest.models import Climber, Bloc, Success, climber_category_bloc

def test_process(complete_database):
    climbers = Climber.query.filter(Climber.id.in_(complete_database["climber_ids"])).all()

    categories_to_update = {c.category for c in climbers}
    
    try:
        for cat in categories_to_update:
            ranking = processor.run(cat)
            
            print(f"Ranking for category {cat}: {ranking}")
            
            if cat == "U16 H":
                assert ranking[0]["name"] == "Climber One"
                assert ranking[0]["score"] == 1000
            if cat == "U16 F":
                assert ranking[0]["name"] == "Climber Three"
                assert ranking[0]["score"] == 1500
                assert ranking[0]["category"] == "U16 F"
                assert ranking[1]["name"] == "Climber Two"
                assert ranking[1]["score"] == 500
                assert ranking[1]["category"] == "U16 F"
    except Exception as e:
        print(f"Processor failed: {e}")
        assert False, f"Processor failed: {e}"