from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Ticket, TicketComment
from .serializers import TicketSerializer, TicketCommentSerializer, TicketAgentIDSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .permissions import TicketAccessPermission
from accounts.permissions import IsAdmin, IsAgent, IsUser
from .tasks import escalate_ticket


# user can create ticket
@extend_schema(request=TicketSerializer, responses=TicketSerializer, summary="User can create ticket")
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsUser])
def create_ticket(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save(created_by=request.user)

        delay_map = {
            'HIGH': 60,
            'MEDIUM': 14400,
            'LOW': 86400,
        }

        # Schedule escalation task based on priority
        escalate_ticket.apply_async(
            args=[ticket.id],
            countdown=delay_map[ticket.priority]
        )

        return Response(TicketSerializer(ticket).data, status=201)

    return Response(serializer.errors, status=400)



# list tickets with filters and role-based access
@extend_schema(
    summary="List tickets with search & RBAC",
    parameters=[
        OpenApiParameter(
            name='title',
            description='Search tickets by title (partial match)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='status',
            description='Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED, ESCALATED)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='priority',
            description='Filter by priority (LOW, MEDIUM, HIGH)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='assigned_to',
            description='Filter by assigned agent user ID',
            required=False,
            type=int
        ),
    ],
    responses=TicketSerializer(many=True),
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tickets(request):
    role = request.user.profile.role
    queryset = Ticket.objects.all()

    # Role-based access
    if role == 'AGENT':
        queryset = queryset.filter(assigned_to=request.user)
    elif role == 'USER':
        queryset = queryset.filter(created_by=request.user)

    # filters
    title = request.GET.get('title')
    status_ = request.GET.get('status')
    priority = request.GET.get('priority')
    assigned_to = request.GET.get('assigned_to')

    if title:
        queryset = queryset.filter(title__icontains=title)
    if status_:
        queryset = queryset.filter(status=status_)
    if priority:
        queryset = queryset.filter(priority=priority)
    if assigned_to:
        queryset = queryset.filter(assigned_to__id=assigned_to)

    serializer = TicketSerializer(queryset, many=True)
    return Response(serializer.data)



# agent can update ticket status
@extend_schema(request=TicketSerializer, responses=TicketSerializer, summary="Agent can update ticket status")
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAgent])
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, assigned_to=request.user)
    ticket.status = request.data.get('status', ticket.status)
    ticket.save()
    return Response(TicketSerializer(ticket).data)


# admin can assign ticket to agent
@extend_schema(request=TicketAgentIDSerializer, responses=TicketSerializer, summary="Admin can assign ticket to agent")
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    agent_id = request.data.get('agent_id')

    try:
        agent = User.objects.get(id=agent_id, profile__role='AGENT')
    except User.DoesNotExist:
        return Response({"error": "Agent not found"}, status=404)
    # ValueError: Field 'id' expected a number but got 'string'
    except ValueError:
        return Response({"error": "Invalid agent ID"}, status=400)
    
    ticket.assigned_to = agent
    ticket.status = 'IN_PROGRESS'
    ticket.save()

    return Response(TicketSerializer(ticket).data)


# admin can delete ticket
@extend_schema(responses=OpenApiTypes.OBJECT, summary="Admin can delete ticket")
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return Response({"message": "Ticket deleted"})


# comment on ticket
@extend_schema(request=TicketCommentSerializer, responses=TicketCommentSerializer, summary="Comment on ticket")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    TicketAccessPermission().has_object_permission(request, None, ticket)

    comment = TicketComment.objects.create(
        ticket=ticket,
        user=request.user,
        comment=request.data.get('comment')
    )

    return Response(TicketCommentSerializer(comment).data, status=201)


# BONUS
# ticket report for last 7 days
@extend_schema(
    summary="Ticket report for last 7 days",
    responses=OpenApiTypes.OBJECT,
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def ticket_report(request):
    last_7_days = timezone.now() - timedelta(days=7)

    opened = Ticket.objects.filter(created_at__gte=last_7_days).count()
    resolved = Ticket.objects.filter(
        status='RESOLVED',
        updated_at__gte=last_7_days
    ).count()
    escalated = Ticket.objects.filter(
        status='ESCALATED',
        updated_at__gte=last_7_days
    ).count()

    return Response({
        "last_7_days": {
            "opened": opened,
            "resolved": resolved,
            "escalated": escalated
        }
    })