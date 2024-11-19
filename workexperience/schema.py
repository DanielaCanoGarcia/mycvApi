import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType
from django.db.models import Q

class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

class Query(graphene.ObjectType):
    work_experiences = graphene.List(WorkExperienceType, search=graphene.String())
    work_experience_by_id = graphene.Field(WorkExperienceType, id=graphene.Int())

    def resolve_work_experience_by_id(self, info, id, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return WorkExperience.objects.filter(Q(posted_by=user) & Q(id=id)).first()

    def resolve_work_experiences(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        if search == "*":
            return WorkExperience.objects.filter(posted_by=user)[:10]
        return WorkExperience.objects.filter(Q(posted_by=user) & Q(city__icontains=search))

class CreateOrUpdateWorkExperience(graphene.Mutation):
    id = graphene.Int()
    city = graphene.String()
    year_start = graphene.Int()
    year_end = graphene.Int()
    work = graphene.String()
    position = graphene.String()
    achievements = graphene.JSONString()
    posted_by = graphene.Field(UserType)

    class Arguments:
        id = graphene.Int(required=False)
        city = graphene.String(required=True)
        year_start = graphene.Int(required=True)
        year_end = graphene.Int(required=True)
        work = graphene.String(required=True)
        position = graphene.String(required=True)
        achievements = graphene.JSONString(required=False)

    def mutate(self, info, city, year_start, year_end, work, position, achievements={}, id=None):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')

        if id:
            work_experience_instance = WorkExperience.objects.filter(id=id).first()
            if work_experience_instance:
                work_experience_instance.city = city
                work_experience_instance.year_start = year_start
                work_experience_instance.year_end = year_end
                work_experience_instance.work = work
                work_experience_instance.position = position
                work_experience_instance.achievements = achievements
            else:
                raise Exception('WorkExperience not found!')
        else:
            work_experience_instance = WorkExperience(
                city=city,
                year_start=year_start,
                year_end=year_end,
                work=work,
                position=position,
                achievements=achievements,
                posted_by=user
            )

        work_experience_instance.save()

        return CreateOrUpdateWorkExperience(
            id=work_experience_instance.id,
            city=work_experience_instance.city,
            year_start=work_experience_instance.year_start,
            year_end=work_experience_instance.year_end,
            work=work_experience_instance.work,
            position=work_experience_instance.position,
            achievements=work_experience_instance.achievements,
            posted_by=work_experience_instance.posted_by
        )

class DeleteWorkExperience(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        current_work_experience = WorkExperience.objects.filter(id=id).first()

        if not current_work_experience:
            raise Exception('Invalid Work Experience!')

        current_work_experience.delete()

        return DeleteWorkExperience(
            id=id
        )

class Mutation(graphene.ObjectType):
    create_or_update_work_experience = CreateOrUpdateWorkExperience.Field()
    delete_work_experience = DeleteWorkExperience.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
