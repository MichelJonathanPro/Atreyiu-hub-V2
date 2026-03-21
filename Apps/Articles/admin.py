from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'is_published')
    list_filter = ('category', 'is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'tags', 'obsidian_path')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'slug', 'category', 'tags', 'author')
        }),
        ('Contenu', {
            'fields': ('content', 'image')
        }),
        ('Statut et Synchro', {
            'fields': ('is_published', 'obsidian_path', 'created_at', 'updated_at')
        }),
    )
