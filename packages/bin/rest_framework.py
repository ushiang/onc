import json
from django.http import HttpResponse
from django.views.generic import View


class RestView(View):

    queryset = None

    fields = None

    data = list()

    limit = 100

    model = None

    qk = None

    mode = "full"

    safe_display = False

    def get(self, request, method=None, pk=None, qk=None, search=None):

        self.qk = qk
        self.safe_display = request.GET.get("safe")

        if pk is not None:
            return self.retrieve(pk=pk)

        elif qk is not None:
            return self.retrieve_group()

        else:
            return self.list()

    def retrieve(self, raw=False, pk=None):
        self.queryset = self.queryset.filter(pk=pk)
        return self.render_data(raw)

    def retrieve_group(self, raw=False, pk=None):
        """
        This method should be declared in the child class, just a place holder
        :param raw:
        :param pk:
        :return:
        """
        pass

    def list(self, raw=False, mode="full"):
        return self.render_data(raw)

    def render_column(self, row, column):
        """ Renders a column on a row
        """
        if hasattr(row, 'get_%s_display' % column):
            # It's a choice field
            text = getattr(row, 'get_%s_display' % column)()
        else:
            try:
                text = getattr(row, column)
            except AttributeError:
                obj = row
                for part in column.split('.'):
                    if obj is None:
                        break
                    obj = getattr(obj, part)

                text = obj

        if hasattr(row, 'get_absolute_url'):
            return '<a href="%s">%s</a>' % (row.get_absolute_url(), text)
        else:
            return text

    def build_table(self):

        data = list()
        for q in self.queryset[:self.limit]:
            row = dict()
            if self.mode == "minimalistic":
                fields = self.fields_min
            else:
                fields = self.fields
            for k, v in fields.iteritems():
                row[k] = self.render_column(q, k)

            data.append(row)

        self.data = data

    def render_data(self, raw=False):

        self.build_table()

        if raw:
            return self.data

        else:
            self.data = {
                'result': self.data,
                'count': self.queryset.count(),
                'limit': self.limit,
            }
            return HttpResponse(json.dumps(self.data))

    @staticmethod
    def render_rest_from_queryset(queryset):

        data = list()

        for x in queryset:
            data.append({
                "id": x.pk,
                "name": str(x)
            })

        return data