import graphene
from graphene_django import DjangoObjectType
from .models import Header
from users.schema import UserType
from django.db.models import Q

class HeaderType(DjangoObjectType):
    class Meta:
        model = Header

class Query(graphene.ObjectType):
    headers = graphene.List(HeaderType, search=graphene.String())
    header_by_id = graphene.Field(HeaderType, id=graphene.Int())

    def resolve_header_by_id(self, info, id, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return Header.objects.filter(Q(posted_by=user) & Q(id=id)).first()

    def resolve_headers(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        if search == "*":
            return Header.objects.filter(posted_by=user)[:10]
        return Header.objects.filter(Q(posted_by=user) & Q(name__icontains=search))

class CreateOrUpdateHeader(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    urlImage = graphene.String()
    email = graphene.String()
    telephone = graphene.String()
    ubication = graphene.String()
    redSocial = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        id = graphene.Int(required=False)
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        urlImage = graphene.String(required=False)
        email = graphene.String(required=True)
        telephone = graphene.String(required=False)
        ubication = graphene.String(required=False)
        redSocial = graphene.String(required=False)

    def mutate(self, info, name, email, description="", urlImage="", telephone="", ubication="", redSocial="", id=None):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')

        if Header.objects.exists() and not id:
            raise Exception("Only one Header instance is allowed.")

        if id:
            header_instance = Header.objects.filter(id=id).first()
            if header_instance:
                header_instance.name = name
                header_instance.description = description
                header_instance.urlImage = urlImage
                header_instance.email = email
                header_instance.telephone = telephone
                header_instance.ubication = ubication
                header_instance.redSocial = redSocial
            else:
                raise Exception('Header not found!')
        else:
            header_instance = Header(
                name=name,
                description=description,
                urlImage=urlImage,
                email=email,
                telephone=telephone,
                ubication=ubication,
                redSocial=redSocial,
                posted_by=user
            )

        header_instance.save()

        return CreateOrUpdateHeader(
            id=header_instance.id,
            name=header_instance.name,
            description=header_instance.description,
            urlImage=header_instance.urlImage,
            email=header_instance.email,
            telephone=header_instance.telephone,
            ubication=header_instance.ubication,
            redSocial=header_instance.redSocial,
            posted_by=header_instance.posted_by
        )

class DeleteHeader(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        header_instance = Header.objects.filter(id=id).first()

        if not header_instance:
            raise Exception('Invalid Header!')

        header_instance.delete()

        return DeleteHeader(
            id=id
        )

class Mutation(graphene.ObjectType):
    create_or_update_header = CreateOrUpdateHeader.Field()
    delete_header = DeleteHeader.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
