from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model
from graphql import GraphQLError

from links.schema import schema
from links.models import Link, Vote

# Create your tests here.

LINKS_QUERY = '''
{
  links {
    id
    url
    description
  }
}
'''

USERS_QUERY = '''
{
  users {
    id
    username
    password
  }
}
'''

VOTES_QUERY = '''
{
  votes {
    id
    user {
      username
    }
    link {
      url
    }
  }
}
'''

CREATE_LINK_MUTATION = '''
mutation createLinkMutation($url: String!, $description: String!) {
  createLink(url: $url, description: $description) {
    description
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

CREATE_VOTE_MUTATION = '''
mutation createVote($linkId: Int!) {
  createVote(linkId: $linkId) {
    user {
      username
    }
    link {
      description
    }
  }
}
'''

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.link1 = mixer.blend(Link)
        self.link2 = mixer.blend(Link)
   
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={'email': 'adsoft@live.com.mx', 'username': 'adsoft', 'password': 'adsoft'}
        )
        print('user mutation ')
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

        self.user = get_user_model().objects.get(username='adsoft')
        self.vote1 = mixer.blend(Vote, user=self.user, link=self.link1)
        self.vote2 = mixer.blend(Vote, user=self.user, link=self.link2)

    def test_links_query(self):
        response = self.query(
            LINKS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        print("query link results")
        print(response)
        assert len(content['data']['links']) == 2

    def test_users_query(self):
        response = self.query(
            USERS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        print("query users results")
        print(response)
        assert len(content['data']['users']) == 3

    def test_createLink_mutation(self):
        response = self.query(
            CREATE_LINK_MUTATION,
            variables={'url': 'https://google.com', 'description': 'google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createLink": {"description": "google"}}, content['data'])

    def test_createVote_mutation(self):
        # Test creating a vote for an existing link
        response = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': self.link1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createVote': {
                'user': {
                    'username': 'adsoft'
                },
                'link': {
                    'description': self.link1.description
                }
            }
        }, content['data'])

    def test_createVote_invalid_link(self):
        # Test creating a vote with an invalid link ID
        response = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Link!')

    def test_votes_query(self):
        response = self.query(
            VOTES_QUERY,
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['votes']), 2)
        self.assertEqual(content['data']['votes'][0]['user']['username'], 'adsoft')
        self.assertEqual(content['data']['votes'][1]['user']['username'], 'adsoft')

class UnauthenticatedUserTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.link1 = mixer.blend(Link)
        self.link2 = mixer.blend(Link)

    def test_links_query_unauthenticated(self):
        response = self.query(
            LINKS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)

    def test_createVote_mutation_unauthenticated(self):
        # Test creating a vote without authentication
        response = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': self.link1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'GraphQLError: You must be logged to vote!')
