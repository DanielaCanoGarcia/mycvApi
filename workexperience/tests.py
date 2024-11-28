from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from workexperience.schema import schema
from workexperience.models import WorkExperience

# Create your tests here.

EXPERIENCE_BY_ID_QUERY = '''
query experienceById($idExperience: Int!) {
  experienceById(idExperience: $idExperience) {
    id
    city
    yearStart
    yearEnd
    work
    position
    achievments
  }
}
'''

EXPERIENCES_QUERY = '''
query experiences($search: String) {
  experiences(search: $search) {
    id
    city
    yearStart
    yearEnd
    work
    position
    achievments
  }
}
'''

CREATE_WORK_EXPERIENCE_MUTATION = '''
mutation CreateWorkExperience($idExperience: Int!, $city: String!, $yearStart: Int!, $yearEnd: Int!, $work: String!, $position: String!, $achievments: JSONString!) {
  createWorkExperience(
    idExperience: $idExperience,
    city: $city,
    yearStart: $yearStart,
    yearEnd: $yearEnd,
    work: $work,
    position: $position,
    achievments: $achievments
  ) {
    idExperience
    city
    yearStart
    yearEnd
    work
    position
    achievments
  }
}
'''

DELETE_WORK_EXPERIENCE_MUTATION = '''
mutation DeleteWorkExperience($idExperience: Int!) {
  deleteWorkExperience(idExperience: $idExperience) {
    idExperience
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

class WorkExperienceTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.experience1 = mixer.blend(WorkExperience)
        self.experience2 = mixer.blend(WorkExperience)
   
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

    def test_experienceById_query(self):
        response = self.query(
            EXPERIENCE_BY_ID_QUERY,
            variables={'idExperience': self.experience1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['experienceById']['id'], self.experience1.id)

    def test_experiences_query(self):
        response = self.query(
            EXPERIENCES_QUERY,
            variables={'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['experiences']), 2)

    def test_createWorkExperience_mutation(self):
        response = self.query(
            CREATE_WORK_EXPERIENCE_MUTATION,
            variables={
                'idExperience': 0,
                'city': 'New York',
                'yearStart': 2020,
                'yearEnd': 2022,
                'work': 'Software Development',
                'position': 'Developer',
                'achievments': '{"achievment1": "Built a successful app", "achievment2": "Led a team of developers"}'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createWorkExperience': {
                'idExperience': content['data']['createWorkExperience']['idExperience'],
                'city': 'New York',
                'yearStart': 2020,
                'yearEnd': 2022,
                'work': 'Software Development',
                'position': 'Developer',
                'achievments': '{"achievment1": "Built a successful app", "achievment2": "Led a team of developers"}'
            }
        }, content['data'])

    def test_deleteWorkExperience_mutation(self):
        # Test deleting an existing work experience record
        response = self.query(
            DELETE_WORK_EXPERIENCE_MUTATION,
            variables={'idExperience': self.experience1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteWorkExperience': {'idExperience': self.experience1.id}}, content['data'])

        # Verify that the work experience record is deleted
        with self.assertRaises(WorkExperience.DoesNotExist):
            WorkExperience.objects.get(id=self.experience1.id)

    def test_deleteWorkExperience_invalid_id(self):
        # Test deleting a work experience record with an invalid ID
        response = self.query(
            DELETE_WORK_EXPERIENCE_MUTATION,
            variables={'idExperience': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Work Experience!')

class UnauthenticatedUserWorkExperienceTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.experience1 = mixer.blend(WorkExperience)
        self.experience2 = mixer.blend(WorkExperience)

    def test_experienceById_query_unauthenticated(self):
        response = self.query(
            EXPERIENCE_BY_ID_QUERY,
            variables={'idExperience': self.experience1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_experiences_query_unauthenticated(self):
        response = self.query(
            EXPERIENCES_QUERY,
            variables={'search': '*'}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_createWorkExperience_mutation_unauthenticated(self):
        response = self.query(
            CREATE_WORK_EXPERIENCE_MUTATION,
            variables={
                'idExperience': 0,
                'city': 'New York',
                'yearStart': 2020,
                'yearEnd': 2022,
                'work': 'Software Development',
                'position': 'Developer',
                'achievments': '{"achievment1": "Built a successful app", "achievment2": "Led a team of developers"}'
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteWorkExperience_mutation_unauthenticated(self):
        # Test deleting a work experience record without authentication
        response = self.query(
            DELETE_WORK_EXPERIENCE_MUTATION,
            variables={'idExperience': self.experience1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

if __name__ == '__main__':
    TestCase.main()
