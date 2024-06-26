from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import filters
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from . import models
from . import serializers
from rest_framework import permissions
from .permissions import IsContactor, IsRepresentative, IsRepresentativeAndCreator, IsRepresentativeOrReadOnly, \
    IsCreatorOrExecutor, IsAuthorOrReadOnly


from .serializers import MyTokenObtainPairSerializer


# Create your views here.
class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class ProjectList(generics.ListAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ProjectDetail(generics.RetrieveAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class OrganizationList(generics.ListAPIView):
    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class OrganizationDetail(generics.RetrieveAPIView):
    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class ViolationTypeList(generics.ListAPIView):
    queryset = models.ViolationType.objects.all()
    serializer_class = serializers.ViolationTypeSerializer


class ViolationList(generics.ListCreateAPIView):
    # queryset = models.Violation.objects.all()
    serializer_class = serializers.ViolationSerializer
    filterset_fields = ['project', 'status']
    permission_classes = [IsRepresentative]

    def get_queryset(self):
        user = self.request.user
        queryset = models.Violation.objects.filter(creator=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ViolationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Violation.objects.all()
    serializer_class = serializers.ViolationSerializer
    permission_classes = [IsRepresentativeAndCreator]


class TaskList(generics.ListCreateAPIView):
    # queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    filterset_fields = ['violation', 'status']
    permission_classes = [IsRepresentativeOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = models.Task.objects.filter(Q(creator=user) | Q(executor=user))
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = [IsCreatorOrExecutor]


class CommentList(generics.ListCreateAPIView):
    # queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['task']
        return models.Comment.objects.filter(task=task_id)

    # def perform_create(self, serializer):
        # serializer.save(task_id=self.kwargs['task'])


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticated]


class AttachmentList(generics.ListCreateAPIView):
    queryset = models.Attachment.objects.all()
    serializer_class = serializers.AttachmentSerializer
    filterset_fields = ['violation', 'task', 'comment']


class AttachmentDetail(generics.RetrieveDestroyAPIView):
    queryset = models.Attachment.objects.all()
    serializer_class = serializers.AttachmentSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        group = self.request.query_params.get('group')
        if group:
            return User.objects.filter(groups__name=group)
        return User.objects.all()


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
