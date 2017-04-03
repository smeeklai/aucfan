from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Master, Pos, SeasonalTrend
from .serializers import MasterSerializer, PosSerializer, SeasonalTrendSerializer,SampleSerializer # ,PosdataHistorySerializer,SampleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from django_pandas.io import read_frame
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
import pandas as pd
from django.shortcuts import get_list_or_404

from django.http import Http404
# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'masters':reverse('master-list', request=request, format=None),
        'pos':reverse('pos-list', request=request, format=None),
        'seasonaltrend':reverse('seasonaltrend-list', request=request,format=None),
        'predict':reverse('predict-list', request=request,format=None),
    })


def index(request):
    return HttpResponse(datetime.now())



class MasterList(generics.ListCreateAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

class MasterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer


class PosList(generics.ListCreateAPIView):
    queryset = Pos.objects.all()
    serializer_class = PosSerializer

class PosDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pos.objects.all()
    serializer_class = PosSerializer



class SeasonalTrendList(generics.ListCreateAPIView):
    queryset = SeasonalTrend.objects.all()
    serializer_class = SeasonalTrendSerializer

class SeasonalTrendDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SeasonalTrend.objects.all()
    serializer_class = SeasonalTrendSerializer

class PosFilterViewSet(generics.ListAPIView):
    serializer_class = PosSerializer
    def get_queryset(self):
        query_jan = self.kwargs['jan']
        return Pos.object.filter(pos__jan = query_jan)



#
# class MasterViewSet(ModelViewSet):
#     queryset = Master.objects.all()
#     serializer_class = MasterSerializer
#     filter_fields = ('jan')

# class PosViewSet(ModelViewSet):
#     queryset = Pos.objects.all()
#     serializer_class = PosSerializer
#     filter_fields = ('jan')
#
# class SeasonalTrendViewSet(ModelViewSet):
#     queryset = SeasonalTrend.objects.all()
#     serializer_class = SeasonalTrendSerializer





class PredictList(APIView):

    def get(self,request,format=None):
        #master = Master.objects.all()

        #serializer=MasterSerializer(master, many=True)
        raise Http404

class Predict(APIView):
    def get_object(self,pk):
        pos = Pos.objects.filter(jan=pk, )
        if not pos:
             raise Http404
        return pos
    def post(self,request,pk,format=None):
        pos_object = self.get_object(pk)
        pos = pd.DataFrame.from_records(pos_object.values())

        pos.date = pos.datetime.apply(lambda x: pd.to_datetime(x))
        pos.index = pos.date
        #pos.date = pos.date.apply(lambda x: x.strftime('%Y-%m-%d'))
        pos.price = pos.price.apply(lambda x:float(x))
        import statsmodels.api as sm
        arima = sm.tsa.ARIMA(pos.price, order=[7, 1, 1]).fit()
        arima_result = arima.forecast(180)
        result = {"predict":[int(arima_result[0][-1])], "lower": [int(arima_result[2][-1][0])],
                  "upper": [int(arima_result[2][-1][1])]}

        #serializer=PosSerializer(pos)
        serializer=PosSerializer(pos, many=True)
        #return Response(serializer.data)
        return Response(result)

# class Sample(APIView):
#     def get(self, request, format=None):
#         raise Http404
#         return Response("a")


    #def post(self,request,format=None):
        # serializer= SnippetSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #return Response()

# class predictPrice(APIView):
#     def post(self,request):
#         #serializer = PosdataHistorySerializer(data=request.data)
#         serializer = SampleSerializer(data=request.data)
#
#         if serializer.is_valid():
#             return Response(request.data,status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#
#
# class preprocess(APIView):
#     def post(self,request):
#         df = read_frame(request.data, fieldnames=[])
#         return Response(request.data,status=status.HTTP_200_OK)
