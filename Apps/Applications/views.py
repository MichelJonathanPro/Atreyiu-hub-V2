from django.shortcuts import render

def index(request):
    """
    Main page for applications.
    """
    # dummy data for front-end demonstration
    applications = [
        {
            'id': 1,
            'title': 'StockMaster Pro',
            'description': 'Gestion de stock intelligente avec IA prédictive pour anticiper les ruptures.',
            'category': 'Business',
            'platform': 'Web / Mobile',
            'version': 'v2.4.0',
            'status': 'Live',
            'status_class': 'bg-success',
            'techs': ['Django', 'React', 'Redis'],
            'image': 'assets/images/blog/blog-img-9.jpg'
        },
        {
            'id': 2,
            'title': 'EduStream',
            'description': 'Plateforme d\'apprentissage interactive supportant le streaming 4K et les quiz en temps réel.',
            'category': 'Education',
            'platform': 'Web',
            'version': 'v1.1.0',
            'status': 'Beta',
            'status_class': 'bg-warning',
            'techs': ['Next.js', 'WebRTC', 'PostgreSQL'],
            'image': 'assets/images/blog/blog-img-1.jpg'
        },
        {
            'id': 3,
            'title': 'CollabSync',
            'description': 'Espace de travail collaboratif chiffré de bout en bout pour équipes distantes.',
            'category': 'Productivité',
            'platform': 'Desktop / Web',
            'version': 'v0.9.5',
            'status': 'Early Access',
            'status_class': 'bg-info',
            'techs': ['Electron', 'Node.js', 'Socket.io'],
            'image': 'assets/images/blog/blog-img-2.jpg'
        }
    ]
    
    context = {
        'applications': applications,
        'page_title': 'Hub d\'Applications',
        'page_tagline': 'Des solutions logicielles puissantes, innovantes et prêtes à l\'emploi.',
    }
    return render(request, 'Applications/Applications_index.html', context)

def detail(request):
    """
    Detail page for a specific application.
    """
    context = {
        'title': 'StockMaster Pro',
        'version': 'v2.4.0',
        'status': 'Live',
        'status_class': 'bg-success',
        'description': 'StockMaster Pro est une solution de gestion de stock de nouvelle génération...',
        'techs': ['Django', 'React', 'Redis', 'PostgreSQL', 'Docker'],
        'image': 'assets/images/blog/blog-img-9.jpg'
    }
    return render(request, 'Applications/Applications_detail.html', context)
