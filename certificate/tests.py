from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import json
from django.contrib.auth import get_user_model

from certificate.schema import schema
from certificate.models import Certificate

# Create your tests here.

CERTIFICATE_BY_ID_QUERY = '''
query certificateById($idCertificate: Int!) {
  certificateById(idCertificate: $idCertificate) {
    id
    certificate
    description
    year
  }
}
'''

CERTIFICATES_QUERY = '''
query {
  certificates {
    id
    certificate
    description
    year
  }
}
'''

CREATE_CERTIFICATE_MUTATION = '''
mutation CreateCertificate($idCertificate: Int!, $certificate: String!, $description: String!, $year: Int!) {
  createCertificate(
    idCertificate: $idCertificate,
    certificate: $certificate,
    description: $description,
    year: $year
  ) {
    idCertificate
    certificate
    description
    year
  }
}
'''

DELETE_CERTIFICATE_MUTATION = '''
mutation DeleteCertificate($idCertificate: Int!) {
  deleteCertificate(idCertificate: $idCertificate) {
    idCertificate
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

class CertificateTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.certificate1 = mixer.blend(Certificate)
        self.certificate2 = mixer.blend(Certificate)
        self.certificate3 = mixer.blend(Certificate, id=1, certificate="Existing Certificate", description="Existing Description", year=2021)
   
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

    def test_certificateById_query(self):
        response = self.query(
            CERTIFICATE_BY_ID_QUERY,
            variables={'idCertificate': self.certificate1.id},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['certificateById']['id'], self.certificate1.id)

    def test_certificates_query(self):
        response = self.query(
            CERTIFICATES_QUERY,
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['certificates']), 2)

    def test_createCertificate_mutation(self):
        response = self.query(
            CREATE_CERTIFICATE_MUTATION,
            variables={
                'idCertificate': 0,
                'certificate': 'Test Certificate',
                'description': 'Test Description',
                'year': 2022
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createCertificate': {
                'idCertificate': content['data']['createCertificate']['idCertificate'],
                'certificate': 'Test Certificate',
                'description': 'Test Description',
                'year': 2022
            }
        }, content['data'])

    def test_createCertificate_mutation_with_existing_id(self):
        response = self.query(
            CREATE_CERTIFICATE_MUTATION,
            variables={
                'idCertificate': 1,
                'certificate': 'New Certificate',
                'description': 'New Description',
                'year': 2022
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({
            'createCertificate': {
                'idCertificate': 1,
                'certificate': 'New Certificate',
                'description': 'New Description',
                'year': 2022
            }
        }, content['data'])
        self.assertEqual(Certificate.objects.get(id=1).certificate, 'New Certificate')


    def test_deleteCertificate_mutation(self):
        # Test deleting an existing certificate
        response = self.query(
            DELETE_CERTIFICATE_MUTATION,
            variables={'idCertificate': self.certificate1.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({'deleteCertificate': {'idCertificate': self.certificate1.id}}, content['data'])

        # Verify that the certificate record is deleted
        with self.assertRaises(Certificate.DoesNotExist):
            Certificate.objects.get(id=self.certificate1.id)

    def test_deleteCertificate_invalid_id(self):
        # Test deleting a certificate record with an invalid ID
        response = self.query(
            DELETE_CERTIFICATE_MUTATION,
            variables={'idCertificate': 9999},  # Assuming this ID does not exist
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid Certificate!')

class UnauthenticatedUserCertificateTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.certificate1 = mixer.blend(Certificate)
        self.certificate2 = mixer.blend(Certificate)

    def test_certificateById_query_unauthenticated(self):
        response = self.query(
            CERTIFICATE_BY_ID_QUERY,
            variables={'idCertificate': self.certificate1.id}
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_certificates_query_unauthenticated(self):
        response = self.query(
            CERTIFICATES_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        
        # This checks if an error is returned for unauthenticated access
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_createCertificate_mutation_unauthenticated(self):
        response = self.query(
            CREATE_CERTIFICATE_MUTATION,
            variables={
                'idCertificate': 0,
                'certificate': 'Test Certificate',
                'description': 'Test Description',
                'year': 2022
            }
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

    def test_deleteCertificate_mutation_unauthenticated(self):
        # Test deleting a certificate record without authentication
        response = self.query(
            DELETE_CERTIFICATE_MUTATION,
            variables={'idCertificate': self.certificate1.id}
        )
        content = json.loads(response.content)
        print(content)
        self.assertTrue('errors' in content)
        self.assertEqual(content['errors'][0]['message'], 'Not logged in!')

