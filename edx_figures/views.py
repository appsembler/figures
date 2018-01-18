from django.shortcuts import render

# Create your views here.

def edx_figures_home(request):

    # Placeholder context vars just to illustrate returning API hosts to the
    # client. This one uses a protocol relative url
    context = {
        'edx_figures_api_url': '//api.foo.com',
    }
    return render(request, 'edx_figures/index.html', context)

