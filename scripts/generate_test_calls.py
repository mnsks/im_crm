from django.utils import timezone
from datetime import timedelta
import random
from core.models import User, CentreAppels
from missions.models import Mission
from saisie.models import SaisieResultat
from clients.models import Client

def generate_test_calls():
    # Get a centre d'appel
    centres = CentreAppels.objects.all()
    if centres:
        centre = centres.first()
    else:
        print("Aucun centre d'appel trouvé")
        return

    # Get agents from this centre
    agents = User.objects.filter(role='agent', parent_centre=centre)
    if not agents:
        print("Aucun agent trouvé pour ce centre")
        return

    # Get missions for this centre
    missions = Mission.objects.filter(centre=centre)
    if not missions:
        print("Aucune mission trouvée pour ce centre")
        return

    # Get some clients
    clients = Client.objects.all()
    if not clients:
        print("Aucun client trouvé")
        return

    # Current time
    now = timezone.now()
    start_of_day = now.replace(hour=8, minute=0, second=0, microsecond=0)

    # Generate calls for each hour from 8h to current hour
    current_hour = now.hour
    if current_hour < 8:
        current_hour = 20  # If it's before 8h, generate data for whole previous day

    print(f"Génération des appels de test de 8h à {current_hour}h...")

    # Delete existing calls for today
    SaisieResultat.objects.filter(date_appel__date=now.date()).delete()

    for hour in range(8, current_hour + 1):
        # Generate 5-15 calls per hour
        num_calls = random.randint(5, 15)
        
        for _ in range(num_calls):
            # Random minute in the hour
            minute = random.randint(0, 59)
            call_time = start_of_day.replace(hour=hour, minute=minute)
            
            # Random duration between 1 and 15 minutes
            duration = timedelta(minutes=random.randint(1, 15))
            
            # Random type and status
            type_appel = random.choice(['entrant', 'sortant'])
            status = random.choice(['success', 'failure', 'callback', 'unavailable'])
            
            # Create the call record
            SaisieResultat.objects.create(
                mission=random.choice(missions),
                agent=random.choice(agents),
                client=random.choice(clients),
                type_appel=type_appel,
                status=status,
                commentaire=f"Appel test {type_appel} - {status}",
                duree_appel=duration,
                date_appel=call_time
            )

    print("Génération terminée !")
    
    # Print some stats
    total_calls = SaisieResultat.objects.filter(date_appel__date=now.date()).count()
    incoming_calls = SaisieResultat.objects.filter(date_appel__date=now.date(), type_appel='entrant').count()
    outgoing_calls = SaisieResultat.objects.filter(date_appel__date=now.date(), type_appel='sortant').count()
    missed_calls = SaisieResultat.objects.filter(date_appel__date=now.date(), status='failure').count()
    
    print(f"\nStatistiques pour aujourd'hui :")
    print(f"Total des appels : {total_calls}")
    print(f"Appels entrants : {incoming_calls}")
    print(f"Appels sortants : {outgoing_calls}")
    print(f"Appels manqués : {missed_calls}")
