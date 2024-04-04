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
                if precioTotal <= precioMax and r.capacity == residentes and fechaInicio < fechaFin: 
                    goodRoom = True
                    bookings = Booking.objects.filter(room_id = r.id)
                    for b in bookings:
                        bookingStart = b.start
                        bookingEnd = b.end
                        if not((fechaInicio < bookingStart and fechaFin < bookingStart) or (fechaInicio > bookingEnd and fechaFin > bookingEnd)):
                            goodRoom = False
                            filteredHotels = []
                            break
                    if goodRoom:
                        filteredHotels.append(r)

        return filteredHotels

#API REST

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
        serializer.is_valid()

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
        OpenApiParameter(name='hora',location=OpenApiParameter.QUERY, description='Hora a la que empieza la actividad', required=True, type=str),
        OpenApiParameter(name='precioMax',location=OpenApiParameter.QUERY, description='Precio máximo de la actividad', required=True, type=str),
    ],)
    def get(self, request, format=None, *args, **kwargs):
        ciudad = request.GET.get('ciudad', '').split()
        for i in range(len(ciudad)):
            ciudad[i] = unidecode.unidecode(ciudad[i])
        tipo = request.GET.get('tipo', '')
        fechaInicio = request.GET.get('fecha', '')
        fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d').date()
        hora = request.GET.get('hora', '')
        hora = datetime.strptime(hora, '%H:%M:%S').time()
        precioMax = float(request.GET.get('precioMax', ''))
        activities = Activity.objects.filter(city__iin=ciudad).filter(type=tipo).filter(date=fechaInicio).filter(startTime__gte=hora).filter(price__lte=precioMax).order_by("price")[:3]
        serializer = ActivitySerializers(activities, many=True)
        
        return Response(serializer.data)

class ActivityType_APIView(APIView):

    @extend_schema(responses= ActivitySerializers(many=True))
    def get(self, request, format=None, *args, **kwargs):
        activities = Activity.objects.values_list('type', flat=True).distinct()
        
        return Response(activities)

#WEBHOOK DIALOGFLOW

@functions_framework.http
@csrf_exempt
def handleWebhook(request):
    req = json.loads(request.body)
    intent = req['queryResult']['intent']['displayName']

    responseText = ""

    if intent == "Intent Busqueda Hoteles":
        responseText = webhookSearchHotels(req)
    elif intent == "Intent Busqueda Vuelos":
        responseText = webhookSearchFlights(req)
    elif intent == "Intent Busqueda Actividades":
        responseText = webhookSearchActivityTypes(req)
    elif intent == "Intent Busqueda Actividades - Followup":
        responseText = webhookSearchActivities(req)

    return JsonResponse(responseText, safe=False)

def webhookSearchHotels(req):
    ciudad = req['queryResult']['parameters']['ciudad']
    ciudad = unidecode.unidecode(ciudad)
    residentes = int(req['queryResult']['parameters']['residentes'])
    fechaInicio = req['queryResult']['parameters']['fechaInicio'][0:10]
    fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d').date()
    fechaFin = req['queryResult']['parameters']['fechaFin'][0:10]
    fechaFin= datetime.strptime(fechaFin, '%Y-%m-%d').date()
    precioMax = float(req['queryResult']['parameters']['precioMax'])
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

def webhookSearchFlights(req):
    origen = req['queryResult']['parameters']['origen']
    origen = unidecode.unidecode(origen)
    destino = req['queryResult']['parameters']['destino']
    destino = unidecode.unidecode(destino)
    viajeros = int(req['queryResult']['parameters']['viajeros'])
    fechaSalida = req['queryResult']['parameters']['fechaSalida'][0:10]
    fechaSalida = datetime.strptime(fechaSalida, '%Y-%m-%d').date()
    fechaRegreso = req['queryResult']['parameters']['fechaRegreso'][0:10]
    fechaRegreso= datetime.strptime(fechaRegreso, '%Y-%m-%d').date()
    precioMax = float(req['queryResult']['parameters']['precioMax'])
    responseText = ""

    flights = Flight.objects.filter(destination=destino).filter(departure=origen).filter(departureDate=fechaSalida).filter(returnDate=fechaRegreso).filter(price__lte=precioMax).filter(remainingSeats__gte=viajeros).order_by("price")[:3]

    if(len(flights) == 0):
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Lo siento, pero no he podido encontrar vuelos que cumplan todas tus necesidades. ¿Puedo ayudarte con otra cosa?"]}}]}
    else:
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Esto es lo que he encontrado: "]}}]}
        for d in flights:
            responseText["fulfillmentMessages"].append({"text": {"text": ["Vuelo con " + d.airline +  " destino " + d.destination + ", desde " + d.departure + ", por " + str(d.price) + "€ cada ticket. " + str(d.remainingSeats) + " asientos disponibles."]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Fecha de salida: " + str(d.departureDate)]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Horario del vuelo de ida: " + str(d.departureDepartureTime)[0:5] + " - " + str(d.departureArrivalTime)[0:5]]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Fecha de regreso: " + str(d.returnDate)]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Horario del vuelo de regreso: " + str(d.returnDepartureTime)[0:5] + " - " + str(d.returnArrivalTime)[0:5]]}})
            responseText["fulfillmentMessages"].append({"text": {"text": [""]}})

        responseText["fulfillmentMessages"].append({"text": {"text": ["Espero que te sea útil. ¿Puedo ayudarte con algo más?"]}})

    return responseText

def webhookSearchActivityTypes(req):
    responseText = ""

    activities = Activity.objects.values_list('type', flat=True).distinct()

    responseText = {"fulfillmentMessages": [{"text": {"text": ["De acuerdo, te ayudaré a encontrar actividades turísticas. Dime cuál de los siguientes tipos de actividad te interesa:"]}}]}
    for d in activities:
        responseText["fulfillmentMessages"].append({"text": {"text": [d]}})
        responseText["fulfillmentMessages"].append({"text": {"text": [""]}})

    return responseText

def webhookSearchActivities(req):
    tipo = req['queryResult']['parameters']['tipo']
    tipo = unidecode.unidecode(tipo)
    ciudad = req['queryResult']['parameters']['ciudad']
    ciudad = unidecode.unidecode(ciudad)
    fecha = req['queryResult']['parameters']['fecha'][0:10]
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    hora = req['queryResult']['parameters']['hora'][11:19]
    hora = datetime.strptime(hora, '%H:%M:%S').time()
    precioMax = float(req['queryResult']['parameters']['precioMax'])
    responseText = ""

    activities = Activity.objects.filter(city=ciudad).filter(type=tipo).filter(date=fecha).filter(startTime__gte=hora).filter(price__lte=precioMax).order_by("price")[:3]

    if(len(activities) == 0):
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Lo siento, pero no he podido encontrar actividades que cumplan todas tus necesidades. ¿Puedo ayudarte con otra cosa?"]}}]}
    else:
        responseText = {"fulfillmentMessages": [{"text": {"text": ["Esto es lo que he encontrado: "]}}]}
        for d in activities:
            responseText["fulfillmentMessages"].append({"text": {"text": [d.title]}})
            responseText["fulfillmentMessages"].append({"text": {"text": [d.description]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Empieza a las " + str(d.startTime)[0:5] + " del " + str(d.date) + ", y dura " + str(d.duration) + " horas"]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Ubicación: " + d.address + ", " + d.city]}})
            if(d.price == 0):
                responseText["fulfillmentMessages"].append({"text": {"text": ["Precio por persona: gratuito"]}})
            else:
                responseText["fulfillmentMessages"].append({"text": {"text": ["Precio por persona: " + str(d.price)]}})
            responseText["fulfillmentMessages"].append({"text": {"text": ["Teléfono de contacto: " + d.phone]}})
            responseText["fulfillmentMessages"].append({"text": {"text": [""]}})

        responseText["fulfillmentMessages"].append({"text": {"text": ["Espero que te sea útil. ¿Puedo ayudarte con algo más?"]}})

    return responseText