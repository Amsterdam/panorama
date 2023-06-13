from collections import OrderedDict

from rest_framework.fields import URLField
from rest_framework.relations import HyperlinkedIdentityField, RelatedField, ManyRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ListSerializer
from rest_framework.utils.serializer_helpers import ReturnList
from rest_framework import response
from rest_framework.utils.urls import replace_query_param


class IdentityLinksField(HyperlinkedIdentityField):
    def to_representation(self, value):
        request = self.context.get('request')
        return dict(href=self.get_url(value, self.view_name, request, None))


class HyperLinksField(URLField):
    def to_representation(self, value):
        return dict(href=value)


class HALListSerializer(ListSerializer):
    @property
    def data(self):
        returnlist = super().data
        fieldname = self.child.Meta.listresults_field
        return OrderedDict({fieldname: ReturnList(returnlist, serializer=self)})


class HALSerializer(HyperlinkedModelSerializer):
    serializer_url_field = IdentityLinksField

    class Meta:
        listresults_field = 'results'
        list_serializer_class = HALListSerializer

    def get_fields(self):
        fields = super().get_fields()

        link_fields = OrderedDict()
        embedded_fields = OrderedDict()
        resulting_fields = OrderedDict()

        # first entry in resulting ordered dict
        resulting_fields['_links'] = None
        # transfer field 'url' from HyperlinkedIdentityField to field 'self'
        link_fields['self'] = fields.pop('url')

        for field_name, field in fields.items():
            if self._is_link_field(field):
                link_fields[field_name] = field
            elif self._is_embedded_field(field):
                embedded_fields[field_name] = field
            else:
                resulting_fields[field_name] = field

        resulting_fields['_links'] = self._get_links_serializer(link_fields)
        if len(embedded_fields) > 0:
            resulting_fields['_embedded'] = self._get_embedded_serializer(embedded_fields)

        return resulting_fields

    def _get_links_serializer(self, link_fields):
        parent_model = self.Meta.model

        class HALNestedLinksSerializer(HALSerializer):
            class Meta:
                model = parent_model
                fields = [key for key in link_fields.keys()]

            def get_fields(self):
                return link_fields

        return HALNestedLinksSerializer(instance=self.instance, source="*")

    @staticmethod
    def _is_link_field(field):
        return isinstance(field, RelatedField) or isinstance(field, ManyRelatedField) \
               or isinstance(field, HyperLinksField) or isinstance(field, HyperlinkedIdentityField)

    def _get_embedded_serializer(self, embedded_fields):
        # NOT IMPLEMENTED YET
        return None

    @staticmethod
    def _is_embedded_field(field):
        # NOT IMPLEMENTED YET
        return False
