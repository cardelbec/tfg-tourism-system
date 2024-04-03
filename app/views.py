from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FlightSerializers, ActivitySerializers, RoomSerializers
from .models import Hotel, Room, Booking, Flight, Activity
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import datetime
from django.db.models import Field
from django.db.models.lookups import In
import unidecode
import functions_framework
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse, JsonResponse

@Field.register_lookup
class IIn(In):
    lookup_name = 'iin'

    def process_lhs(self, *args, **kwargs):
        sql, params = super().process_lhs(*args, **kwargs)

        # Convert LHS to lowercase
        sql = f'LOWER({sql})'

        return sql, params

    def process_rhs(self, qn, connection):
        rhs, params = super().process_rhs(qn, connection)

        # Convert RHS to lowercase
        params = tuple(p.lower() for p in params)

        return rhs, params

def searchRooms(hotels, residentes, fechaInicio, fechaFin, precioMax):
        filteredHotels = []
        for h in hotels:
            rooms = Room.objects.filter(hotel_id = h.id)
            for r in rooms:
                precioTotal = r.price*(fechaFin - fechaInicio).days
                if precioTotal <= precioMax and r.capacity == residentes: 
                    goodRoom = True
                    bookings = Booking.objects.filter(room_id = r.id)
                    for b in bookings:
                        bookingStart = b.start
                        bookingEnd = b.end
                        if not((fechaInicio < bookingStart and fechaFin < bookingStart) or (fechaInicio > bookingEnd and fechaFin > bookingEnd)):
                            goodRoom = False
                            break
                    if goodRoom:
                        filteredHotels.append(r)

        return filteredHotels

class Hotel_APIView(APIView):

    @extend_schema(responses= RoomSerializers(many=True),
                   parameters=[
        OpenApiParameter(name='ciudad',location=OpenApiParameter.QUERY, description='Ciudad del hotel', required=True, type=str),
        OpenApiParameter(name='residentes',location=OpenApiParameter.QUERY, description='Numero de residentes', required=True, type=str),
        OpenApiParameter(name='fechaInicio',location=OpenApiParameter.QUERY, description='Fecha de inicio de la estancia', required=True, type=str),
        OpenApiParameter(name='fechaFin',location=OpenApiParameter.QUERY, description='Fecha final de la estancia', required=True, type=str),
        OpenApiParameter(name='precioMax',location=OpenApiParameter.QUERY, description='Precio máximo total de la estancia', required=True, type=str),
    ],)
    def get(self, request, format=None, *args, **kwargs):
        ciudad = request.GET.get('ciudad', '').split()
        for i in range(len(ciudad)):
            ciudad[i] = unidecode.unidecode(ciudad[i])
        residentes = int(request.GET.get('residentes', ''))
        fechaInicio = request.GET.get('fechaInicio', '')
        fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d').date()
        fechaFin = request.GET.get('fechaFin', '')
        fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d').date()
        precioMax = float(request.GET.get('precioMax', ''))
        hotels = Hotel.objects.filter(city__iin = ciudad).order_by("-stars")[:3]
        hotels = searchRooms(hotels, residentes, fechaInicio, fechaFin, precioMax)
        serializer = RoomSerializers(data=hotels, many=True)

        return Response(serializer.data)

class Flight_APIView(APIView):

    @extend_schema(responses= FlightSerializers(many=True),
                   parameters=[
        OpenApiParameter(name='destino',location=OpenApiParameter.QUERY, description='Destino del vuelo', required=True, type=str),
        OpenApiParameter(name='origen',location=OpenApiParameter.QUERY, description='Origen del vuelo', required=True, type=str),
        OpenApiParameter(name='viajeros',location=OpenApiParameter.QUERY, description='Numero de viajeros', required=True, type=str),
        OpenApiParameter(name='fechaSalida',location=OpenApiParameter.QUERY, description='Fecha de salida del vuelo', required=True, type=str),
        OpenApiParameter(name='fechaRegreso',location=OpenApiParameter.QUERY, description='Fecha de regreso del vuelo', required=True, type=str),
        OpenApiParameter(name='precioMax',location=OpenApiParameter.QUERY, description='Precio máximo del vuelo', required=True, type=str),
    ],)
    def get(self, request, format=None, *args, **kwargs):
        destino = request.GET.get('destino', '').split()
        for i in range(len(destino)):
            destino[i] = unidecode.unidecode(destino[i])
        origen = request.GET.get('origen', '').split()
        for i in range(len(origen)):
            origen[i] = unidecode.unidecode(origen[i])
        viajeros = request.GET.get('viajeros', '')
        fechaSalida = request.GET.get('fechaSalida', '')
        fechaSalida = datetime.strptime(fechaSalida, '%Y-%m-%d').date()
        fechaRegreso = request.GET.get('fechaRegreso', '')
        fechaRegreso = datetime.strptime(fechaRegreso, '%Y-%m-%d').date()
        precioMax = float(request.GET.get('precioMax', ''))
        flights = Flight.objects.filter(destination__iin=destino).filter(departure__iin=origen).filter(departureDate=fechaSalida).filter(returnDate=fechaRegreso).filter(price__lte=precioMax).filter(remainingSeats__gte=viajeros).order_by("price")[:3]
        serializer = FlightSerializers(flights, many=True)
        
        return Response(serializer.data)
    
class Activity_APIView(APIView):

    @extend_schema(responses= ActivitySerializers(many=True),
                   parameters=[
        OpenApiParameter(name='ciudad',location=OpenApiParameter.QUERY, description='Ciudad de la actividad', required=True, type=str),
        OpenApiParameter(name='tipo',location=OpenApiParameter.QUERY, description='Tipo de actividad', required=True, type=str),
        OpenApiParameter(name='fechaInicio',location=OpenApiParameter.QUERY, description='Fecha de la actividad', required=True, type=str),
        OpenApiParameter(name='precioMax',location=OpenApiParameter.QUERY, description='Precio máximo de la actividad', required=True, type=str),
    ],)
    def get(self, request, format=None, *args, **kwargs):
        ciudad = request.GET.get('ciudad', '').split()
        for i in range(len(ciudad)):
            ciudad[i] = unidecode.unidecode(ciudad[i])
        tipo = request.GET.get('tipo', '')
        fecha = request.GET.get('fecha', '')
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora = request.GET.get('hora', '')
        hora = datetime.strptime(hora, '%H:%M:%S').time()
        precioMax = float(request.GET.get('precioMax', ''))
        activities = Activity.objects.filter(city__iin=ciudad).filter(type=tipo).filter(date=fecha).filter(startTime__gte=hora).filter(price__lte=precioMax).order_by("price")[:3]
        serializer = ActivitySerializers(activities, many=True)
        
        return Response(serializer.data)

class ActivityType_APIView(APIView):

    @extend_schema(responses= ActivitySerializers(many=True))
    def get(self, request, format=None, *args, **kwargs):
        activities = Activity.objects.values_list('type', flat=True).distinct()
        
        return Response(activities)

@functions_framework.http
@csrf_exempt
def handleWebhook(request):
    req = json.loads(request.body)
    intent = req['queryResult']['intent']['displayName']

    responseText = ""

    if intent == "Intent Busqueda Hoteles":
        responseText = webhookSearchHotels(req)
    elif intent == "get-agent-name":
        responseText = "My name is Flowhook"
    else:
        responseText = f"There are no fulfillment responses defined for Intent {intent}"

    #res = {"fulfillmentMessages": [{"text": {"text": [responseText]}}]}

    return JsonResponse(responseText, safe=False)

def webhookSearchHotels(req):
    ciudad = req['queryResult']['parameters']['ciudad']
    residentes = req['queryResult']['parameters']['residentes']
    fechaInicio = req['queryResult']['parameters']['fechaInicio'][0:10]
    fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d').date()
    fechaFin = req['queryResult']['parameters']['fechaFin'][0:10]
    fechaFin= datetime.strptime(fechaFin, '%Y-%m-%d').date()
    precioMax = int(req['queryResult']['parameters']['precioMax'])
    responseText = ""

    hotels = Hotel.objects.filter(city = ciudad).order_by("-stars")[:3]
    hotels = searchRooms(hotels, residentes, fechaInicio, fechaFin, precioMax)

    if(len(hotels) == 0):
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Lo siento, pero no he podido encontrar hoteles que cumplan todas tus necesidades. ¿Puedo ayudarte con otra cosa?"]}}]}
    else:
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Esto es lo que he encontrado: "]}}]}
        for d in hotels:
            responseText["fulfillmentMessages"].append({"text": {"text": ["Habitación para " + str(d.capacity) + " en " + d.hotel.name + ", " + d.hotel.address + ", por " + str(d.price) + "€ por noche."]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Teléfono de contacto: " + d.hotel.phone]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Estrellas: " + str(d.hotel.stars)]}})
            responseText["fulfillmentMessages"].append({"text": {"text": [""]}})

        responseText["fulfillmentMessages"].append({"text": {"text": ["Espero que te sea útil. ¿Puedo ayudarte con algo más?"]}})

    return responseText