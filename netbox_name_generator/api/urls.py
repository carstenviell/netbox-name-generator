from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register('standorte', views.StandortViewSet)
router.register('ng-typen', views.NetzwerkgeraetTypViewSet)
router.register('ng-funktionen', views.NetzwerkgeraetFunktionViewSet)
router.register('server-zwecke', views.ServerZweckViewSet)
router.register('vm-bereiche', views.VmBereichViewSet)
router.register('vm-funktionen', views.VmFunktionViewSet)

urlpatterns = router.urls
