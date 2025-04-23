from ..models import INCCIndex

def verificar_indices_incc(request):
    return {
        'incc_faltando': not INCCIndex.objects.exists()
    }
