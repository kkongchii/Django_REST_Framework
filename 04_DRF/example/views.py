import re
from rest_framework import permissions, generics, status, mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from .models import Book
from .serializers import BookSerializer

@api_view(['GET'])
def HelloAPI(request):
    return Response("hello world!")

@api_view(['GET', 'POST']) #GET, POST 요청을 처리하게 만들어주는 데코레이터
def booksAPI(request): #/book/
    if request.method == 'GET': #GET요청
        books = Book.objects.all() #Book모델로부터 전체 데이터 가져오기
        serializer = BookSerializer(books, many = True) #시리얼러아지에 전체 데이터 한번에 집어넣기(직렬화, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) #return Response
    elif request.method == 'POST': #POST요청
        serializer = BookSerializer(data=request.data) #POST요청으로 들어온 데이터를 시리얼라이저에 집어넣기
        if serializer.is_valid(): #유효한데이터라면
            serializer.save() #시리얼라이저의 역직렬화를 통해 save(), 모델시리얼라이저의 기본 create()가 동작
            return Response(serializer.data, status=status.HTTP_201_CREATED) #201메시지(POST가 정상적으로 등록됨)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)#400메시지(잘못된요청)

@api_view(['GET'])
def bookAPI(request, bid): #/book/bid
    book = get_object_or_404(Book, bid=bid) #bid=bid인 데이터를 Book에서 가져오고 없으면 404에러
    serializer = BookSerializer(book) #시리얼라이저에 데이터 집어넣기, 직렬화
    return Response(serializer.data, status=status.HTTP_200_OK) #리턴

class HelloAPI(APIView):
    def get(self, request):
        return Response("hello world")
    

class BooksAPI(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BookAPI(APIView):
    def get(self, request, bid):
        book = get_object_or_404(Book, bid=bid)
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

#mixins를 이용해 중복되는 코드를 간결하게 작성해보자
class BooksAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView ):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get(self, request, *args, **kwargs): #전체목록보기
        return self.list(request, *args, **kwargs) #mixins.ListModelMixin과 연결
    def post(self, request, *args, **kwargs): #한권 등록하기
        return self.create(request, *args, **kwargs) #mixins.CreateModelMixin과 연결
    
class BookAPIMixins(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'bid' #장고기본모델의 pk가 아닌 bid를 pk로 사용
    
    def get(self, request, *args, **kwargs): #한권정보보기
        return self.retrieve(request, *args, **kwargs) #mixins.RetrieveModelMixin과 연결
    def put(self, request, *args, **kwargs): #한권수정하기
        return self.update(request, *args, **kwargs) #mixins.UpdateModelMixin과 연결
    def delete(self, request, *args, **kwargs): #한권삭제하기
        return self.destroy(request, *args, **kwargs) #mixins.DestroyModelMixin과 연결
    
#Generics으로 코드를 더 줄여보자, return 필요없음 상속받는 클래스정보로부터 어차피 이미 알고있기 때문
#실행은 똑같이 urls.py 추가하고 직접 들어가보기 지금은 생략
class BooksAPIGenerics(generics.ListCreateAPIView): #전체목록+생성
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
class BookAPIGenerics(generics.RetrieveUpdateDestroyAPIView): #1개+1개수정+1개삭제
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'bid'
    
#Viewset&Router로 URL 작성부분까지 더 줄여보자
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
#4줄까지 줄어들어버렸다... ModelViewSet은 CRUD+전체목록 다섯가지 기능이 미리 작성되어있음