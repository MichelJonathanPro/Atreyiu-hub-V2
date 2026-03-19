from django.db import models

class RoadmapItem(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Prévu'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description", blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Élément de la Roadmap"
        verbose_name_plural = "Éléments de la Roadmap"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
