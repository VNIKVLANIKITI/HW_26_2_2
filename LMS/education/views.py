from rest_framework import viewsets, generics
from education.serializers import LessonSerializer, CourseSerializer
from education.models import lesson, course
from rest_framework.permissions import IsAuthenticated
from education.permissions import IsCurator
from education.paginators import lessonPaginator, courcePaginator
from education.tasks import update_lesson
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe


# CRUD на вьюсетах
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    queryset = lesson.objects.all()


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = course.objects.all()
    pagination_class = courcePaginator
    

# CRUD на дженериках
class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    #permission_classes = [IsAuthenticated]

    '''
    def perform_create(self, serializer):
        new_lesson = serializer.save()
        new_lesson.owner = self.request.user
        new_lesson.save()
    '''

class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = lesson.objects.all()
    pagination_class = lessonPaginator

class LessonRetriveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = lesson.objects.all()

class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = lesson.objects.all()
    permission_classes = [IsCurator]
    
    def perform_update(self, serializer):
        current_lesson = serializer.save()
        update_lesson.delay(current_lesson.id, 'lesson')
        #new_lesson.owner = self.request.user
        #new_lesson.save()


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = lesson.objects.all()


class CreateCheckoutSession(APIView):
    def post(self, request, course_id):
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Курс не найден'}, status=status.HTTP_404_NOT_FOUND)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': course.name,
                            'description': course.description,
                        },
                        'unit_amount': int(course.price * 100),  # Цена в центах
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='courses/'+str(course_id),
            cancel_url='courses/'+str(course_id),
        )
        
        return Response({'id': session.id}, status=status.HTTP_200_OK)
