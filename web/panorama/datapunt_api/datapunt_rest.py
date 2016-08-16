from collections import OrderedDict

from rest_framework import renderers, serializers
from rest_framework import pagination, response
from rest_framework import viewsets, filters, reverse

# from rest_framework.reverse import reverse

from rest_framework.utils.urls import replace_query_param
from rest_framework_extensions.mixins import DetailSerializerMixin

DEFAULT_RENDERERS = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer)
FORMATS = [dict(format=r.format, type=r.media_type) for r in DEFAULT_RENDERERS]


def get_links(view_name, kwargs=None, request=None):
    result = OrderedDict([
        ('self', dict(
            href=reverse(view_name, kwargs=kwargs, request=request)
        ))
    ])

    return result


class DataSetSerializerMixin(object):
    def to_representation(self, obj):
        result = super().to_representation(obj)
        result['dataset'] = self.dataset
        return result


class LinksField(serializers.HyperlinkedIdentityField):
    def to_representation(self, value):
        view = self.context.get('view')
        if view.lookup_field != 'pk':
            self.lookup_url_kwarg = view.lookup_field
            self.lookup_field = view.lookup_field

        request = self.context.get('request')
        result = OrderedDict([
            ('self', dict(
                href=self.get_url(value, self.view_name, request, None))
             ),
        ])

        return result


class HALSerializer(serializers.HyperlinkedModelSerializer):
    url_field_name = '_links'
    serializer_url_field = LinksField


class HALPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        self_link = self.request.build_absolute_uri()
        if self_link.endswith(".api"):
            self_link = self_link[:-4]

        if self.page.has_next():
            next_link = replace_query_param(
                self_link, self.page_query_param, self.page.next_page_number())
        else:
            next_link = None

        if self.page.has_previous():
            prev_link = replace_query_param(
                self_link, self.page_query_param,
                self.page.previous_page_number())
        else:
            prev_link = None

        return response.Response(OrderedDict([
            ('_links', OrderedDict([
                ('self', dict(href=self_link)),
                ('next', dict(href=next_link)),
                ('previous', dict(href=prev_link)),
            ])),
            ('count', self.page.paginator.count),
            ('results', data)
        ]))


class AtlasViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = DEFAULT_RENDERERS
    pagination_class = HALPagination
    filter_backends = (filters.DjangoFilterBackend,)


class RelatedSummaryField(serializers.Field):

    def to_representation(self, value):
        count = value.count()
        model_name = value.model.__name__
        mapping = model_name.lower() + "-list"
        url = reverse(mapping, request=self.context['request'])

        parent_pk = value.instance.pk
        filter_name = list(value.core_filters.keys())[0]

        return dict(
            count=count,
            href="{}?{}={}".format(url, filter_name, parent_pk),
        )


class DisplayField(serializers.Field):

    def __init__(self, *args, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return str(value)
