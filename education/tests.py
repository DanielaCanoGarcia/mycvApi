from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from education.schema import schema
from education.models import Education

# Create your tests here.

DEGREE_BY_ID_QUERY = '''
query degreeById($idEducation: Int!) {
  degreeById(idEducation: $idEducation) {
    id
    degree
    university
    startDate
    endDate
  }
}
'''

DEGREES_QUERY = '''
query degrees($search: String) {
  degrees(search: $search) {
    id
    degree
    university
    startDate
    endDate
  }
}
'''

DELETE_EDUCATION_MUTATION = '''
mutation DeleteEducation($idEducation: Int!) {
  deleteEducation(idEducation: $idEducation) {
    idEducation
  }
}
'''

CREATE_EDUCATION_MUTATION = '''
mutation CreateEducation($idEducation: Int!, $degree: String!, $university: String!, $startDate: Date!, $endDate: Date!) {
  createEducation(
    idEducation: $idEducation,
    degree: $degree,
    university: $university,
    startDate: $startDate,
    endDate: $endDate
  ) {
    idEducation
    degree
    university
    startDate
    endDate
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

class EducationTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.education1 = mixer.blend(Education)
        self.education2 = mixer.blend(Education)
   
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

    def test_degreeById_query(self):
        response = self.query(
            DEGREE_BY_ID_QUERY,
            variables={'idEducation': self.education1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['degreeById']['id'], self.education1.id)

    def test_degrees_query(self):
        response = self.query(
            DEGREES_QUERY,
            variables={'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['degrees']), 2)

    def test_createEducation_mutation(self):
        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={
                'idEducation': 0,
                'degree': 'Computer Science',
                'university': 'MIT',
                'startDate': '2020-09-01',
                'endDate': '2024-06-01'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createEducation': {
                'idEducation': content['data']['createEducation']['idEducation'],
                'degree': 'Computer Science',
                'university': 'MIT',
                'startDate': '2020-09-01',
                'endDate': '2024-06-01'
            }
        }, content['data'])

    def test_deleteEducation_mutation(self):
        # Test deleting an existing education record
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={'idEducation': self.education1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteEducation': {'idEducation': self.education1.id}}, content['data'])

        # Verify that the education record is deleted
        with self.assertRaises(Education.DoesNotExist):
            Education.objects.get(id=self.education1.id)

    def test_deleteEducation_invalid_id(self):
        # Test deleting an education record with an invalid ID
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={'idEducation': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Education!')

class UnauthenticatedUserEducationTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.education1 = mixer.blend(Education)
        self.education2 = mixer.blend(Education)

    def test_degreeById_query_unauthenticated(self):
        response = self.query(
            DEGREE_BY_ID_QUERY,
            variables={'idEducation': self.education1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_degrees_query_unauthenticated(self):
        response = self.query(
            DEGREES_QUERY,
            variables={'search': '*'}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteEducation_mutation_unauthenticated(self):
        # Test deleting an education record without authentication
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={'idEducation': self.education1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

if __name__ == '__main__':
    TestCase.main()
