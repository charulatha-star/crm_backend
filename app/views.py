# ----- Import libraries ------

from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Campaign,LineItem, LineItemCreative
from .serializers import ClientSerializer, CampaignSerializer
import json
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Prefetch

# Home
def home(request):
    return HttpResponse("Welcome to the CRM Home Page!")


@api_view(['POST'])
def create_client(request):
    signatures = {
        key: request.FILES[key]
        for key in request.FILES
        if key.startswith('contact_signature_')
    }

    # Unwrap JSON from FormData "data" field
    raw = request.data.get('data')
    if raw:
        parsed = json.loads(raw)
        data = parsed
    else:
        data = request.data

    serializer = ClientSerializer(
        data=data,
        context={'signatures': signatures}
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Client created successfully"}, status=201)
    return Response(serializer.errors, status=400)


# ==============================
# GET SINGLE CLIENT
# ==============================
@api_view(['GET'])
def get_client(request, client_id):
    try:
        client = Client.objects.select_related(
            'billing',          #  FIXED
            'ownership',        #  FIXED
            'classification'    #  FIXED
        ).prefetch_related(
            'addresses',        # correct
            'contacts'          # correct
        ).get(client_id=client_id)

    except Client.DoesNotExist:
        return Response({"error": "Client not found"}, status=404)

    serializer = ClientSerializer(client)
    return Response(serializer.data)


# ==============================
# GET ALL CLIENTS
# ==============================

@api_view(['GET'])
def get_all_clients(request):

    clients = Client.objects.select_related(
        'billing',          # FIXED
        'ownership',        #  FIXED
        'classification'    #  FIXED
    ).prefetch_related(
        'addresses',        #  correct
        'contacts'          #  correct
    ).all()

    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)


# ------------------------------------------------------------------------------------


# ==============================
# CREATE CAMPAIGN
# ==============================

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # 🔥 IMPORTANT for files
def create_campaign(request):

    # -------------------------
    # 1. Validate client
    # -------------------------
    client_id = request.data.get('client')

    if not client_id:
        return Response({"error": "client is required"}, status=400)

    try:
        client = Client.objects.get(client_id=client_id)
    except Client.DoesNotExist:
        return Response({"error": f"Client '{client_id}' not found"}, status=404)

    # -------------------------
    # 2. Create Campaign
    # -------------------------
    data = request.data.copy()
    data.pop('client', None)

    serializer = CampaignSerializer(data=data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    campaign = serializer.save(client=client)

    # -------------------------
    # 3. Parse Line Items JSON
    # -------------------------
    try:
        line_items_data = json.loads(request.data.get('line_items', '[]'))
    except Exception:
        return Response({"error": "Invalid line_items JSON"}, status=400)

    # -------------------------
    # 4. Create Line Items
    # -------------------------
    for i, li in enumerate(line_items_data):

        line_item = LineItem.objects.create(
            campaign=campaign,
            line_item_name=li.get('lineItemName'),

            #  JSONField → keep list
            ethnicity=li.get('ethnicity', []),

            start_date=li.get('startDate'),
            end_date=li.get('endDate'),

            #  JSONField → keep list
            ad_format=li.get('adFormat', []),

            impressions=li.get('impressions') or None,
            landing_page=li.get('landingPage') or None,
        )

        # -------------------------
        # 5. Creatives (FILES)
        # -------------------------
        for key, file in request.FILES.items():
            if key.startswith(f'line_item_{i}_creative'):
                LineItemCreative.objects.create(
                    line_item=line_item,
                    file=file
                )

    # -------------------------
    # 6. Response
    # -------------------------
    return Response({
        "message": "Campaign created successfully",
        "campaign_id": campaign.campaign_id,
        "data": CampaignSerializer(campaign).data
    }, status=status.HTTP_201_CREATED)







# UMA SENT 

# @api_view(['POST'])
# def create_campaign(request):
#     client_id = request.data.get('client')
#     if not client_id:
#         return Response({"error": "client is required"}, status=400)

#     try:
#         client = Client.objects.get(client_id=client_id)
#     except Client.DoesNotExist:
#         return Response({"error": f"Client '{client_id}' not found"}, status=404)

#     data = request.data.copy()
#     data.pop('client', None)  #  remove before serializer sees it

#     serializer = CampaignSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save(client=client)  #  pass object directly
#         return Response({
#             "message": "Campaign created successfully",
#             "campaign_id": serializer.instance.campaign_id,
#             "data": serializer.data
#         }, status=201)

#     return Response(serializer.errors, status=400)





# ==============================
# GET ALL CAMPAIGNS
# ==============================

@api_view(['GET'])
def get_campaigns(request):

    campaigns = Campaign.objects.select_related('client').prefetch_related(
        Prefetch(
            'line_items',
            queryset=LineItem.objects.prefetch_related('creatives')
        )
    ).all()

    serializer = CampaignSerializer(campaigns, many=True)
    return Response(serializer.data)

# ==============================
# GET CAMPAIGNS BY CLIENT ID
# ==============================

@api_view(['GET'])
def get_campaigns_by_client(request, client_id):

    campaigns = Campaign.objects.filter(client_id=client_id).select_related('client')
    serializer = CampaignSerializer(campaigns, many=True)

    return Response(serializer.data)


# ==============================
# GET CAMPAIGNS BY CAMPAIGN ID
# ==============================


@api_view(['GET'])
def get_campaign_by_id(request, campaign_id):

    try:
        campaign = Campaign.objects.select_related('client').prefetch_related(
            Prefetch(
                'line_items',
                queryset=LineItem.objects.prefetch_related('creatives')
            )
        ).get(campaign_id=campaign_id)

    except Campaign.DoesNotExist:
        return Response({"error": "Campaign not found"}, status=404)

    serializer = CampaignSerializer(campaign)
    return Response(serializer.data)

# ---------------------


    