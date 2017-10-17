import unittest
from flasktasks import db
from flasktasks.tests.flasktasks_testcase import FlaskTasksTestCase
from flasktasks.models import Color, Tag, Storyline, Status


class StorylinesTest(FlaskTasksTestCase):
    def setUp(self):
        super(StorylinesTest).setUp()
        self.valid_tag = Tag('valid tag', Color.BLUE)
        db.session.add(self.valid_tag)
        db.session.commit()

    def test_storylines_page(self):
        first_story = Storyline('storyline a', 'description', self.valid_tag.id)
        db.session.add(first_story)
        db.session.commit()

        response = self.app.get('/storylines')
        assert b'storyline a' in response.data
        assert b'storyline b' in response.data

    def test_new_storyline_form(self):
        response = self.app.get('/storylines/new')
        assert b'New Storyline' in response.data

    def test_storyline_creation(self):
        data = { 'title':'some storyline', 'description':'a useful description',
                 'tag_id':self.valid_tag.id }
        response = self.app.post('/storylines/new', data=data)
        assert response.status_code == 302

        response = self.app.get('/storylines')
        assert b'some storyline' in response.data

if __name__ == '__main__':
    unittest.main()
