# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from machado.api import views
from django.conf.urls import include, url
from rest_framework_nested import routers
from rest_framework.documentation import include_docs_urls


router = routers.SimpleRouter(trailing_slash=False)

router.register(
    r"jbrowse/stats/global", views.JBrowseGlobalViewSet, base_name="jbrowse_global"
)
router.register(
    r"jbrowse/features/(?P<refseq>.+)",
    views.JBrowseFeatureViewSet,
    base_name="jbrowse_features",
)
router.register(r"jbrowse/names", views.JBrowseNamesViewSet, base_name="jbrowse_names")
router.register(
    r"jbrowse/refSeqs.json", views.JBrowseRefSeqsViewSet, base_name="jbrowse_refseqs"
)

urlpatterns = [
    url(r"", include_docs_urls(title="machado API")),
    url(r"", include(router.urls)),
]
