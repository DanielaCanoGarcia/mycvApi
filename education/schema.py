import graphene
from graphene_django import DjangoObjectType
from .models import Education
from users.schema import UserType
from django.db.models import Q

class EducationType(DjangoObjectType):
    class Meta:
        model = Education

class Query(graphene.ObjectType):
    degrees = graphene.List(EducationType, search=graphene.String())
    degreeById = graphene.Field(EducationType, idEducation=graphene.Int())

    def resolve_degreeById(self, info, idEducation, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id=idEducation)
        )
        return Education.objects.filter().first()

    def resolve_degrees(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Education.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(degree__icontains=search)
            )
            return Education.objects.filter(filter)
class CreateEducation(graphene.Mutation):
    idEducation = graphene.Int()
    degree     = graphene.String()
    university = graphene.String()
    start_date = graphene.Date()
    end_date   = graphene.Date()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idEducation= graphene.Int()  
        degree     = graphene.String()
        university = graphene.String()
        start_date = graphene.Date()
        end_date   = graphene.Date()

    #3
    def mutate(self, info, idEducation, degree, university, start_date, end_date):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentEducation = Education.objects.filter(id=idEducation).first()
        print (currentEducation)
        education = Education(
            degree     = degree,
            university = university,
            start_date = start_date,
            end_date   = end_date,
            posted_by  = user
            )

        if currentEducation:
            education.id = currentEducation.id

        education.save()

        return CreateEducation(
            idEducation  = education.id,
            degree     = education.degree,
            university = education.university,
            start_date = education.start_date,
            end_date   = education.end_date,
            posted_by  = education.posted_by
        )
    
class DeleteEducation(graphene.Mutation):
        idEducation = graphene.Int()

        class Arguments:
            idEducation= graphene.Int()

        def mutate(self, info, idEducation):
            user = info.context.user or None

            if user.is_anonymous:
                raise Exception('Not logged in!')
            print(user)

            currentEducation = Education.objects.filter(id=idEducation).first()
            print (currentEducation)

            if not currentEducation:
                raise Exception('Invalid Education!')

            currentEducation.delete()

            return CreateEducation(
                idEducation=idEducation
                )
#4
class Mutation(graphene.ObjectType):
    create_education = CreateEducation.Field()
    delete_education = DeleteEducation.Field()