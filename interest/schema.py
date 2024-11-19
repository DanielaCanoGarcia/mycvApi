import graphene
from graphene_django import DjangoObjectType
from .models import Interest
from users.schema import UserType
from django.db.models import Q

class InterestType(DjangoObjectType):
    class Meta:
        model = Interest

class Query(graphene.ObjectType):
    interests = graphene.List(InterestType, search=graphene.String())
    interestById = graphene.Field(InterestType, idInterest=graphene.Int())

    def resolve_interestById(self, info, idInterest, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        filter = (
            Q(posted_by=user) & Q(id=idInterest)
        )
        return Interest.objects.filter(filter).first()

    def resolve_interests(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)
        if search == "*":
            filter = Q(posted_by=user)
            return Interest.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(interest__icontains=search)
            return Interest.objects.filter(filter)

class CreateInterest(graphene.Mutation):
    idInterest = graphene.Int()
    interest = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        idInterest = graphene.Int()
        interest = graphene.String()

    def mutate(self, info, idInterest, interest):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentInterest = Interest.objects.filter(id=idInterest).first()
        print(currentInterest)
        interest_instance = Interest(
            interest=interest,
            posted_by=user
        )

        if currentInterest:
            interest_instance.id = currentInterest.id

        interest_instance.save()

        return CreateInterest(
            idInterest=interest_instance.id,
            interest=interest_instance.interest,
            posted_by=interest_instance.posted_by
        )

class DeleteInterest(graphene.Mutation):
    idInterest = graphene.Int()

    class Arguments:
        idInterest = graphene.Int()

    def mutate(self, info, idInterest):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentInterest = Interest.objects.filter(id=idInterest).first()
        print(currentInterest)

        if not currentInterest:
            raise Exception('Invalid Interest!')

        currentInterest.delete()

        return DeleteInterest(
            idInterest=idInterest
        )

class Mutation(graphene.ObjectType):
    create_interest = CreateInterest.Field()
    delete_interest = DeleteInterest.Field()
