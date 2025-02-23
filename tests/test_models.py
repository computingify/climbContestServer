import unittest
from datetime import datetime
from src.models import db, Climber
from src.main import create_app
import os

class TestModels(unittest.TestCase):
    def setUp(self):
        """Configuration de l'environnement de test"""
        self.app = create_app('testing')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        """Nettoyage après les tests"""
    #    db.session.remove()
    #    db.drop_all()
    #    self.ctx.pop()
    #    # Supprime le fichier de la base de données de test
    #    if os.path.exists('test.db'):
    #        os.remove('test.db')

    def test_create_climber(self):
        """Test l'ajout d'un grimpeur dans la base de données"""
        # Création d'un nouveau grimpeur
        climber = Climber(
            name="John Doe",
            bib=1,
            club="Club A",
            category="SNH"
        )

        # Ajout et validation dans la base de données
        db.session.add(climber)
        db.session.commit()

        # Récupération du grimpeur depuis la base de données
        saved_climber = Climber.query.filter_by(name="John Doe").first()

        # Vérifications
        self.assertIsNotNone(saved_climber)
        self.assertEqual(saved_climber.name, "John Doe")
        self.assertEqual(saved_climber.bib, 1)
        self.assertEqual(saved_climber.club, "Club A")
        self.assertEqual(saved_climber.category, "SNH")

if __name__ == '__main__':
    unittest.main()