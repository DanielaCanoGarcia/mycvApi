from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from skills.schema import schema
from skills.models import Skills

# Create your tests here.

SKILL_BY_ID_QUERY = '''
query skillById($idSkill: Int!) {
  skillById(idSkill: $idSkill) {
    id
    skills
  }
}
'''

SKILLS_QUERY = '''
query skills($search: String) {
  skills(search: $search) {
    id
    skills
  }
}
'''

CREATE_SKILL_MUTATION = '''
mutation CreateSkill($idSkill: Int!, $skills: String!) {
  createSkill(
    idSkill: $idSkill,
    skills: $skills
  ) {
    idSkill
    skills
  }
}
'''

DELETE_SKILL_MUTATION = '''
mutation DeleteSkill($idSkill: Int!) {
  deleteSkill(idSkill: $idSkill) {
    idSkill
  }
}
'''

CREATE_USER_MUTATION = '''
mutation createUserMutation($email: String!, $password: String!, $username: String!) {
  createUser(email: $email, password: $password, username: $username) {
    user {
      username
      password
    }
  }
}
'''

LOGIN_USER_MUTATION = '''
mutation TokenAuthMutation($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
  }
}
'''

class SkillsTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={'email': 'adsoft@live.com.mx', 'username': 'adsoft', 'password': 'adsoft'}
        )
        print('user mutation')
        content_user = json.loads(response_user.content)
        print(content_user['data'])

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={'username': 'adsoft', 'password': 'adsoft'}
        )

        content_token = json.loads(response_token.content)
        token = content_token['data']['tokenAuth']['token']
        print(token)
        self.headers = {"AUTHORIZATION": f"JWT {token}"}

        user = get_user_model().objects.get(username='adsoft')
        self.skill1 = mixer.blend(Skills, skills='Python', posted_by=user)
        self.skill2 = mixer.blend(Skills, skills='Django', posted_by=user)

    def test_skillById_query(self):
        response = self.query(
            SKILL_BY_ID_QUERY,
            variables={'idSkill': self.skill1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['skillById']['id'], self.skill1.id)

    def test_skills_query(self):
        response = self.query(
            SKILLS_QUERY,
            variables={'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['skills']), 2)

    def test_skills_query_with_search(self):
        response = self.query(
            SKILLS_QUERY,
            variables={'search': 'Python'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['skills']), 1)
        self.assertEqual(content['data']['skills'][0]['skills'], 'Python')

    def test_createSkill_mutation(self):
        response = self.query(
            CREATE_SKILL_MUTATION,
            variables={
                'idSkill': 0,
                'skills': 'JavaScript'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createSkill': {
                'idSkill': content['data']['createSkill']['idSkill'],
                'skills': 'JavaScript'
            }
        }, content['data'])

    def test_createSkill_mutation_with_existing_id(self):
        response = self.query(
            CREATE_SKILL_MUTATION,
            variables={
                'idSkill': self.skill1.id,  # Usar el mismo id para probar la condición if currentSkill
                'skills': 'Java'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createSkill': {
                'idSkill': self.skill1.id,
                'skills': 'Java'
            }
        }, content['data'])
        
        # Verificar que el id del existing skill es el mismo que el id del nuevo skill
        self.assertEqual(Skills.objects.get(id=self.skill1.id).skills, 'Java')

    def test_deleteSkill_mutation(self):
        # Test deleting an existing skill record
        response = self.query(
            DELETE_SKILL_MUTATION,
            variables={'idSkill': self.skill1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteSkill': {'idSkill': self.skill1.id}}, content['data'])

        # Verify that the skill record is deleted
        with self.assertRaises(Skills.DoesNotExist):
            Skills.objects.get(id=self.skill1.id)

    def test_deleteSkill_invalid_id(self):
        # Test deleting a skill record with an invalid ID
        response = self.query(
            DELETE_SKILL_MUTATION,
            variables={'idSkill': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Skill!')

class UnauthenticatedUserSkillsTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.skill1 = mixer.blend(Skills)
        self.skill2 = mixer.blend(Skills)

    def test_skillById_query_unauthenticated(self):
        response = self.query(
            SKILL_BY_ID_QUERY,
            variables={'idSkill': self.skill1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_skills_query_unauthenticated(self):
        response = self.query(
            SKILLS_QUERY,
            variables={'search': '*'}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_createSkill_mutation_unauthenticated(self):
        response = self.query(
            CREATE_SKILL_MUTATION,
            variables={
                'idSkill': 0,
                'skills': 'Python'
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteSkill_mutation_unauthenticated(self):
        # Test deleting a skill record without authentication
        response = self.query(
            DELETE_SKILL_MUTATION,
            variables={'idSkill': self.skill1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')
