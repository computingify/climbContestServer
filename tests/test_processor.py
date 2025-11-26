from climb_contest.results.processor import Processor


def test_process(complete_database, app):
    processor = Processor(app)
    categories_to_update = {"U16 F", "U16 H"}
    
    for cat in categories_to_update:
        ranking = processor.calculate(cat)
        
        # print(f"Ranking for category {cat}: {ranking}")
        
        if cat == "U16 H":
            assert ranking[0]["name"] == "Climber One"
            assert ranking[0]["score"] == 2000
            assert ranking[0]["category"] == "U16 H"
        if cat == "U16 F":
            assert ranking[0]["name"] == "Climber Three"
            assert ranking[0]["score"] == 2500
            assert ranking[0]["category"] == "U16 F"
            assert ranking[1]["name"] == "Climber Two"
            assert ranking[1]["score"] == 500
            assert ranking[1]["category"] == "U16 F"

def test_process_multiple_categories(complete_database, app):
    processor = Processor(app)
    categories_to_update = {"U16 F", "U16 H"}
    
    ranking = processor.calculate(categories_to_update)
    
    # print(f"Ranking for category {categories_to_update}: {ranking}")
    
    assert ranking[0]["name"] == "Climber Three"
    assert ranking[0]["score"] == 1833
    assert ranking[0]["category"] == "U16 F"
    assert ranking[1]["name"] == "Climber One"
    assert ranking[1]["score"] == 833
    assert ranking[1]["category"] == "U16 H"
    assert ranking[2]["name"] == "Climber Two"
    assert ranking[2]["score"] == 333
    assert ranking[2]["category"] == "U16 F"

def test_process_scratch(complete_database, app):
    processor = Processor(app)
    ranking = processor.calculate('scratch')
    
    # print(f"Ranking for category SCRATCH: {ranking}")
    
    assert ranking[0]["name"] == "Climber Three"
    assert ranking[0]["score"] == 1333
    assert ranking[0]["category"] == "U16 F"
    assert ranking[1]["name"] == "Climber One"
    assert ranking[1]["score"] == 833
    assert ranking[1]["category"] == "U16 H"
    assert ranking[2]["name"] == "Climber Four"
    assert ranking[2]["score"] == 500
    assert ranking[2]["category"] == "U11 H"
    assert ranking[3]["name"] == "Climber Two"
    assert ranking[3]["score"] == 333
    assert ranking[3]["category"] == "U16 F"