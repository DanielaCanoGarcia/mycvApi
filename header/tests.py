from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from header.schema import schema
from header.models import Header

# Create your tests here.

HEADERS_QUERY = '''
 {
   headers {
     id
     name
     email
     description
     urlImage
     telephone
     ubication
     redSocial
   }
 }
'''

CREATE_OR_UPDATE_HEADER_MUTATION = '''
mutation CreateOrUpdateHeader($name: String!, $email: String!, $description: String, $urlImage: String, $telephone: String, $ubication: String, $redSocial: String) {
  createOrUpdateHeader(
    name: $name,
    email: $email,
    description: $description,
    urlImage: $urlImage,
    telephone: $telephone,
    ubication: $ubication,
    redSocial: $redSocial
  ) {
    header {
      id
      name
      email
      description
      urlImage
      telephone
      ubication
      redSocial
    }
  }
}
'''

DELETE_HEADER_MUTATION = '''
mutation DeleteHeader {
  deleteHeader {
    success
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

class HeaderTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.header1 = mixer.blend(Header)
        self.header2 = mixer.blend(Header)
   
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

    def test_headers_query(self):
        response = self.query(
            HEADERS_QUERY,
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        print("query headers results")
        print(response)
        assert len(content['data']['headers']) == 2

    def test_create_or_update_header_mutation(self):
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'description': 'Test Description',
                'urlImage': 'https://example.com/image.jpg',
                'telephone': '123-456-7890',
                'ubication': 'Test Location',
                'redSocial': 'https://twitter.com/johndoe'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createOrUpdateHeader': {
                'header': {
                    'id': content['data']['createOrUpdateHeader']['header']['id'],
                    'name': 'John Doe',
                    'email': 'john.doe@example.com',
                    'description': 'Test Description',
                    'urlImage': 'https://example.com/image.jpg',
                    'telephone': '123-456-7890',
                    'ubication': 'Test Location',
                    'redSocial': 'https://twitter.com/johndoe'
                }
            }
        }, content['data'])

    def test_delete_header_mutation(self):
        # Test deleting an existing header
        response = self.query(
            DELETE_HEADER_MUTATION,
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteHeader': {'success': True}}, content['data'])

        # Verify that the header record is deleted
        with self.assertRaises(Header.DoesNotExist):
            Header.objects.get(id=self.header1.id)

class UnauthenticatedUserHeaderTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.header1 = mixer.blend(Header)
        self.header2 = mixer.blend(Header)

    def test_headers_query_unauthenticated(self):
        response = self.query(
            HEADERS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not authenticated!')

    def test_create_or_update_header_mutation_unauthenticated(self):
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'description': 'Test Description',
                'urlImage': 'https://example.com/image.jpg',
                'telephone': '123-456-7890',
                'ubication': 'Test Location',
                'redSocial': 'https://twitter.com/johndoe'
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not authenticated!')

    def test_delete_header_mutation_unauthenticated(self):
        response = self.query(
            DELETE_HEADER_MUTATION,
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not authenticated!')

if __name__ == '__main__':
    TestCase.main()
