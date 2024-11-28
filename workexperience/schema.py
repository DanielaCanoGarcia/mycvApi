import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType
from django.db.models import Q

class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

class Query(graphene.ObjectType):
    experiences = graphene.List(WorkExperienceType, search=graphene.String())
    experienceById = graphene.Field(WorkExperienceType, idExperience=graphene.Int())

    def resolve_experienceById(self, info, idExperience, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        filter = (
            Q(posted_by=user) & Q(id=idExperience)
        )
        return WorkExperience.objects.filter(filter).first()

    def resolve_experiences(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)
        if search == "*":
            filter = Q(posted_by=user)
            return WorkExperience.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(work__icontains=search)
            )
            return WorkExperience.objects.filter(filter)

class CreateWorkExperience(graphene.Mutation):
    idExperience = graphene.Int()
    city = graphene.String()
    yearStart = graphene.Int()
    yearEnd = graphene.Int()
    work = graphene.String()
    position = graphene.String()
    achievments = graphene.JSONString()
    postedBy = graphene.Field(UserType)

    class Arguments:
        idExperience = graphene.Int()
        city = graphene.String()
        yearStart = graphene.Int()
        yearEnd = graphene.Int()
        work = graphene.String()
        position = graphene.String()
        achievments = graphene.JSONString()

    def mutate(self, info, idExperience, city, yearStart, yearEnd, work, position, achievments):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentExperience = WorkExperience.objects.filter(id=idExperience).first()
        print(currentExperience)
        experience = WorkExperience(
            city=city,
            year_start=yearStart,
            year_end=yearEnd,
            work=work,
            position=position,
            achievments=achievments,
            posted_by=user
        )

        if currentExperience:
            experience.id = currentExperience.id

        experience.save()

        return CreateWorkExperience(
            idExperience=experience.id,
            city=experience.city,
            yearStart=experience.year_start,
            yearEnd=experience.year_end,
            work=experience.work,
            position=experience.position,
            achievments=experience.achievments,
            postedBy=experience.posted_by
        )

class DeleteWorkExperience(graphene.Mutation):
    idExperience = graphene.Int()

    class Arguments:
        idExperience = graphene.Int()

    def mutate(self, info, idExperience):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentExperience = WorkExperience.objects.filter(id=idExperience).first()
        print(currentExperience)

        if not currentExperience:
            raise Exception('Invalid Work Experience!')

        currentExperience.delete()

        return DeleteWorkExperience(
            idExperience=idExperience
        )

class Mutation(graphene.ObjectType):
    createWorkExperience = CreateWorkExperience.Field()
    deleteWorkExperience = DeleteWorkExperience.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
