

def get_page(request):
    try:
        return max(int(request.GET.get('page', 1)), 1)
    except ValueError:
        return 1
