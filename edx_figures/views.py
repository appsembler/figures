from django.shortcuts import render

# Create your views here.

def edx_figures_spa(request):

    context = {
        'edx_figures_api_url': 'http://api.foo.com',
        'edx_figures_api_url_ssl': 'https://api.foo.com',
    }
    return render(request, 'edx_figures/index.html', context)

