from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from interest.schema import schema
from interest.models import Interest

# Create your tests here.

INTEREST_BY_ID_QUERY = '''
query interestById($idInterest: Int!) {
  interestById(idInterest: $idInterest) {
    id
    interest
  }
}
'''

INTERESTS_QUERY = '''
query interests($search: String) {
  interests(search: $search) {
    id
    interest
  }
}
'''

CREATE_INTEREST_MUTATION = '''
mutation CreateInterest($idInterest: Int!, $interest: String!) {
  createInterest(
    idInterest: $idInterest,
    interest: $interest
  ) {
    idInterest
    interest
  }
}
'''

DELETE_INTEREST_MUTATION = '''
mutation DeleteInterest($idInterest: Int!) {
  deleteInterest(idInterest: $idInterest) {
    idInterest
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

class InterestTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.interest1 = mixer.blend(Interest)
        self.interest2 = mixer.blend(Interest)
   
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

    def test_interestById_query(self):
        response = self.query(
            INTEREST_BY_ID_QUERY,
            variables={'idInterest': self.interest1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['interestById']['id'], self.interest1.id)

    def test_interests_query(self):
        response = self.query(
            INTERESTS_QUERY,
            variables={'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['interests']), 2)

    def test_createInterest_mutation(self):
        response = self.query(
            CREATE_INTEREST_MUTATION,
            variables={
                'idInterest': 0,
                'interest': 'Programming'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createInterest': {
                'idInterest': content['data']['createInterest']['idInterest'],
                'interest': 'Programming'
            }
        }, content['data'])

    def test_deleteInterest_mutation(self):
        # Test deleting an existing interest record
        response = self.query(
            DELETE_INTEREST_MUTATION,
            variables={'idInterest': self.interest1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteInterest': {'idInterest': self.interest1.id}}, content['data'])

        # Verify that the interest record is deleted
        with self.assertRaises(Interest.DoesNotExist):
            Interest.objects.get(id=self.interest1.id)

    def test_deleteInterest_invalid_id(self):
        # Test deleting an interest record with an invalid ID
        response = self.query(
            DELETE_INTEREST_MUTATION,
            variables={'idInterest': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Interest!')

class UnauthenticatedUserInterestTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.interest1 = mixer.blend(Interest)
        self.interest2 = mixer.blend(Interest)

    def test_interestById_query_unauthenticated(self):
        response = self.query(
            INTEREST_BY_ID_QUERY,
            variables={'idInterest': self.interest1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_interests_query_unauthenticated(self):
        response = self.query(
            INTERESTS_QUERY,
            variables={'search': '*'}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_createInterest_mutation_unauthenticated(self):
        response = self.query(
            CREATE_INTEREST_MUTATION,
            variables={
                'idInterest': 0,
                'interest': 'Programming'
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteInterest_mutation_unauthenticated(self):
        # Test deleting an interest record without authentication
        response = self.query(
            DELETE_INTEREST_MUTATION,
            variables={'idInterest': self.interest1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

if __name__ == '__main__':
    TestCase.main()
