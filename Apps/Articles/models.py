from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('Digital', 'Numérique'),
        ('Design', 'Design'),
        ('Business', 'Affaires'),
        ('Startup', 'Startup'),
    ]

    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name="Auteur")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Digital', verbose_name="Catégorie")
    tags = models.CharField(max_length=255, blank=True, help_text="Séparez les tags par des virgules", verbose_name="Tags")
    content = models.TextField(verbose_name="Contenu")
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    is_published = models.BooleanField(default=True, verbose_name="Est publié")
    obsidian_path = models.CharField(max_length=500, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Add a unique suffix to slug if title already exists
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title
