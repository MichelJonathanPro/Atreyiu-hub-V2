from django.shortcuts import render
from .models import RoadmapItem

def roadmap_view(request):
    items = RoadmapItem.objects.all().order_by('-created_at')
    return render(request, 'RoadMap/RoadMap.html', {'items': items})
