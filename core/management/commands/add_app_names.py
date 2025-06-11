from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Ajoute app_name aux fichiers urls.py'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        apps = [
            'core',
            'kpi_dashboard',
            'formations',
            'documents',
            'clients',
            'scripts',
            'feedback',
            'saisie',
            'rapports',
            'communication'
        ]

        for app in apps:
            urls_path = os.path.join(base_dir, app, 'urls.py')
            if os.path.exists(urls_path):
                with open(urls_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'app_name' not in content:
                    # Si le fichier est vide ou n'existe pas, créer un nouveau
                    if not content.strip():
                        new_content = f'''from django.urls import path
from . import views

app_name = '{app}'

urlpatterns = [
    # Définir vos URLs ici
]
'''
                    else:
                        # Ajouter app_name après les imports
                        import_end = content.find('urlpatterns')
                        if import_end == -1:  # Si urlpatterns n'est pas trouvé
                            new_content = content + f"\n\napp_name = '{app}'\n\nurlpatterns = []\n"
                        else:
                            new_content = (
                                content[:import_end].rstrip() +
                                f"\n\napp_name = '{app}'\n\n" +
                                content[import_end:]
                            )
                    
                    with open(urls_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Ajout de app_name à {app}/urls.py'
                    ))
                else:
                    self.stdout.write(
                        f'- {app}/urls.py a déjà un app_name'
                    )
