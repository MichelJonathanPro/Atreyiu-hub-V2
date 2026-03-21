from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'tags', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'article'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags (séparés par des virgules)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Contenu de l\'article...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
