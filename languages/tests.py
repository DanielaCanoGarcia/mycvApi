from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from languages.schema import schema
from languages.models import Languages

# Create your tests here.

LANGUAGE_BY_ID_QUERY = '''
query languageById($idLanguage: Int!) {
  languageById(idLanguage: $idLanguage) {
    id
    language
  }
}
'''

LANGUAGES_QUERY = '''
query languages($search: String) {
  languages(search: $search) {
    id
    language
  }
}
'''

CREATE_LANGUAGE_MUTATION = '''
mutation CreateLanguage($idLanguage: Int!, $language: String!) {
  createLanguage(
    idLanguage: $idLanguage,
    language: $language
  ) {
    idLanguage
    language
  }
}
'''

DELETE_LANGUAGE_MUTATION = '''
mutation DeleteLanguage($idLanguage: Int!) {
  deleteLanguage(idLanguage: $idLanguage) {
    idLanguage
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

class LanguagesTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.language1 = mixer.blend(Languages)
        self.language2 = mixer.blend(Languages)
   
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

    def test_languageById_query(self):
        response = self.query(
            LANGUAGE_BY_ID_QUERY,
            variables={'idLanguage': self.language1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['languageById']['id'], self.language1.id)

    def test_languages_query(self):
        response = self.query(
            LANGUAGES_QUERY,
            variables={'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['languages']), 2)

    def test_createLanguage_mutation(self):
        response = self.query(
            CREATE_LANGUAGE_MUTATION,
            variables={
                'idLanguage': 0,
                'language': 'Spanish'
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createLanguage': {
                'idLanguage': content['data']['createLanguage']['idLanguage'],
                'language': 'Spanish'
            }
        }, content['data'])

    def test_deleteLanguage_mutation(self):
        # Test deleting an existing language record
        response = self.query(
            DELETE_LANGUAGE_MUTATION,
            variables={'idLanguage': self.language1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteLanguage': {'idLanguage': self.language1.id}}, content['data'])

        # Verify that the language record is deleted
        with self.assertRaises(Languages.DoesNotExist):
            Languages.objects.get(id=self.language1.id)

    def test_deleteLanguage_invalid_id(self):
        # Test deleting a language record with an invalid ID
        response = self.query(
            DELETE_LANGUAGE_MUTATION,
            variables={'idLanguage': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Language!')

class UnauthenticatedUserLanguagesTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.language1 = mixer.blend(Languages)
        self.language2 = mixer.blend(Languages)

    def test_languageById_query_unauthenticated(self):
        response = self.query(
            LANGUAGE_BY_ID_QUERY,
            variables={'idLanguage': self.language1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_languages_query_unauthenticated(self):
        response = self.query(
            LANGUAGES_QUERY,
            variables={'search': '*'}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_createLanguage_mutation_unauthenticated(self):
        response = self.query(
            CREATE_LANGUAGE_MUTATION,
            variables={
                'idLanguage': 0,
                'language': 'Spanish'
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteLanguage_mutation_unauthenticated(self):
        # Test deleting a language record without authentication
        response = self.query(
            DELETE_LANGUAGE_MUTATION,
            variables={'idLanguage': self.language1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

if __name__ == '__main__':
    TestCase.main()
