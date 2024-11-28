import graphene
from graphene_django import DjangoObjectType
from .models import Header
from django.contrib.auth import get_user_model

class HeaderType(DjangoObjectType):
    class Meta:
        model = Header

class CreateOrUpdateHeader(graphene.Mutation):
    header = graphene.Field(HeaderType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        url_image = graphene.String(required=False)
        email = graphene.String(required=True)
        telephone = graphene.String(required=False)
        ubication = graphene.String(required=False)
        red_social = graphene.String(required=False)

    def mutate(self, info, name, email, description=None, url_image=None, telephone=None, ubication=None, red_social=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not authenticated!")

        header, created = Header.objects.update_or_create(
            posted_by=user,
            defaults={
                'name': name,
                'email': email,
                'description': description,
                'urlImage': url_image,
                'telephone': telephone,
                'ubication': ubication,
                'redSocial': red_social
            }
        )
        return CreateOrUpdateHeader(header=header)

class DeleteHeader(graphene.Mutation):
    success = graphene.Boolean()

    def mutate(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not authenticated!")

        try:
            header = Header.objects.get(posted_by=user)
            header.delete()
            return DeleteHeader(success=True)
        except Header.DoesNotExist:
            return DeleteHeader(success=False)

class Query(graphene.ObjectType):
    headers = graphene.List(HeaderType)

    def resolve_headers(self, info, **kwargs):
        return Header.objects.all()

class Mutation(graphene.ObjectType):
    create_or_update_header = CreateOrUpdateHeader.Field()
    delete_header = DeleteHeader.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

