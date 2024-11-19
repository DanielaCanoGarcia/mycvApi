import graphene
import graphql_jwt

import links.schema
import users.schema
import education.schema
import languages.schema
import interest.schema
import skills.schema
import certificate.schema
import header.schema
import workexperience.schema

class Query(workexperience.schema.Query, header.schema.Query, certificate.schema.Query, skills.schema.Query, interest.schema.Query, languages.schema.Query, education.schema.Query, users.schema.Query, links.schema.Query, graphene.ObjectType):
    pass

class Mutation(workexperience.schema.Mutation, header.schema.Mutation, certificate.schema.Mutation, skills.schema.Mutation, interest.schema.Mutation, languages.schema.Mutation, education.schema.Mutation, users.schema.Mutation, links.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)


