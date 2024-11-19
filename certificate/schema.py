import graphene
from graphene_django import DjangoObjectType
from .models import Certificate
from users.schema import UserType
from django.db.models import Q

class CertificateType(DjangoObjectType):
    class Meta:
        model = Certificate

class Query(graphene.ObjectType):
    certificates = graphene.List(CertificateType, search=graphene.String())
    certificateById = graphene.Field(CertificateType, idCertificate=graphene.Int())

    def resolve_certificateById(self, info, idCertificate, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        filter = (
            Q(posted_by=user) & Q(id=idCertificate)
        )
        return Certificate.objects.filter(filter).first()

    def resolve_certificates(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)
        if search == "*":
            filter = Q(posted_by=user)
            return Certificate.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(certificate__icontains=search)
            return Certificate.objects.filter(filter)

class CreateCertificate(graphene.Mutation):
    idCertificate = graphene.Int()
    certificate = graphene.String()
    description = graphene.String()
    year = graphene.Int()
    posted_by = graphene.Field(UserType)

    class Arguments:
        idCertificate = graphene.Int()
        certificate = graphene.String()
        description = graphene.String()
        year = graphene.Int()

    def mutate(self, info, idCertificate, certificate, description, year):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentCertificate = Certificate.objects.filter(id=idCertificate).first()
        print(currentCertificate)
        certificate_instance = Certificate(
            certificate=certificate,
            description=description,
            year=year,
            posted_by=user
        )

        if currentCertificate:
            certificate_instance.id = currentCertificate.id

        certificate_instance.save()

        return CreateCertificate(
            idCertificate=certificate_instance.id,
            certificate=certificate_instance.certificate,
            description=certificate_instance.description,
            year=certificate_instance.year,
            posted_by=certificate_instance.posted_by
        )

class DeleteCertificate(graphene.Mutation):
    idCertificate = graphene.Int()

    class Arguments:
        idCertificate = graphene.Int()

    def mutate(self, info, idCertificate):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        currentCertificate = Certificate.objects.filter(id=idCertificate).first()
        print(currentCertificate)

        if not currentCertificate:
            raise Exception('Invalid Certificate!')

        currentCertificate.delete()

        return DeleteCertificate(
            idCertificate=idCertificate
        )

class Mutation(graphene.ObjectType):
    create_certificate = CreateCertificate.Field()
    delete_certificate = DeleteCertificate.Field()
