import graphene
from graphene_django import DjangoObjectType
from .models import Skills
from users.schema import UserType
from django.db.models import Q

class SkillsType(DjangoObjectType):
    class Meta:
        model = Skills

class Query(graphene.ObjectType):
    skills = graphene.List(SkillsType, search=graphene.String())
    skillById = graphene.Field(SkillsType, idSkill=graphene.Int())

    def resolve_skillById(self, info, idSkill, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        filter = (
            Q(posted_by=user) & Q(id=idSkill)
        )
        return Skills.objects.filter(filter).first()

    def resolve_skills(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)
        if search == "*":
            filter = Q(posted_by=user)
            return Skills.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(skills__icontains=search)
            return Skills.objects.filter(filter)

class CreateSkill(graphene.Mutation):
    idSkill = graphene.Int()
    skills = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        idSkill = graphene.Int()
        skills = graphene.String()

    def mutate(self, info, idSkill, skills):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentSkill = Skills.objects.filter(id=idSkill).first()
        print(currentSkill)
        skill_instance = Skills(
            skills=skills,
            posted_by=user
        )

        if currentSkill:
            skill_instance.id = currentSkill.id

        skill_instance.save()

        return CreateSkill(
            idSkill=skill_instance.id,
            skills=skill_instance.skills,
            posted_by=skill_instance.posted_by
        )

class DeleteSkill(graphene.Mutation):
    idSkill = graphene.Int()

    class Arguments:
        idSkill = graphene.Int()

    def mutate(self, info, idSkill):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentSkill = Skills.objects.filter(id=idSkill).first()
        print(currentSkill)

        if not currentSkill:
            raise Exception('Invalid Skill!')

        currentSkill.delete()

        return DeleteSkill(
            idSkill=idSkill
        )

class Mutation(graphene.ObjectType):
    create_skill = CreateSkill.Field()
    delete_skill = DeleteSkill.Field()
