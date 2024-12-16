import graphene
from graphene_django import DjangoObjectType
from .models import Languages
from users.schema import UserType
from django.db.models import Q

class LanguagesType(DjangoObjectType):
    class Meta:
        model = Languages

class Query(graphene.ObjectType): 
    languages = graphene.List(LanguagesType, search=graphene.String())
    languageById = graphene.Field(LanguagesType, idLanguage=graphene.Int())

    def resolve_languageById(self, info, idLanguage, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        filter = (
            Q(posted_by=user) & Q(id=idLanguage)
        )
        return Languages.objects.filter(filter).first()

    def resolve_languages(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)
        if search == "*":
            filter = Q(posted_by=user)
            return Languages.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(language__icontains=search)
            return Languages.objects.filter(filter)

class CreateLanguages(graphene.Mutation):
    idLanguage = graphene.Int()
    language = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        idLanguage = graphene.Int()
        language = graphene.String()

    def mutate(self, info, idLanguage, language):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentLanguage = Languages.objects.filter(id=idLanguage).first()
        print(currentLanguage)
        language_instance = Languages(
            language=language,
            posted_by=user
        )

        if currentLanguage:
            language_instance.id = currentLanguage.id

        language_instance.save()

        return CreateLanguages(
            idLanguage=language_instance.id,
            language=language_instance.language,
            posted_by=language_instance.posted_by
        )

class DeleteLanguages(graphene.Mutation):
    idLanguage = graphene.Int()

    class Arguments:
        idLanguage = graphene.Int()

    def mutate(self, info, idLanguage):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentLanguage = Languages.objects.filter(id=idLanguage).first()
        print(currentLanguage)

        if not currentLanguage:
            raise Exception('Invalid Language!')

        currentLanguage.delete()

        return DeleteLanguages(
            idLanguage=idLanguage
        )

class Mutation(graphene.ObjectType):
    create_language = CreateLanguages.Field()
    delete_language = DeleteLanguages.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
