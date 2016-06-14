from django.forms.widgets import Widget
from django.forms.utils import flatatt
from django.utils.html import format_html
from django_datatables_view.base_datatable_view import BaseDatatableView
from packages.bin.bin import Actions, table_button
from packages.bin.search import get_query


class CustomStaticInput(Widget):
    input_type = None
    element = 'div'
    sub_element=None

    def __init__(self, attrs=None, element='div', sub_element=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

        if sub_element is None:
            self.sub_element = 'p'
        else:
            self.sub_element = sub_element

        self.element = element

    def _format_value(self, value):
        return value

    def render(self, name, value='', attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        return format_html("<%s {0}><%s>%s</%s></%s>" % (self.element, self.sub_element, value, self.sub_element,
                        self.element), flatatt(final_attrs))


class DataTable(BaseDatatableView):

    second_base = None

    template_name = None

    # The model we're going to show
    model = None

    # define the columns that will be returned
    columns = None

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = None

    # define the columns for searching
    search_columns = None

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 100

    request = None
    column_settings = None

    def __init__(self, request=None, second_base=None, template_name=None, model=None, columns=None,
                 order_columns=None, max_display_length=None, search_columns=None, column_settings=None):
        self.second_base = second_base
        self.template_name = template_name
        self.model = model
        self.columns = columns
        self.order_columns = order_columns
        self.search_columns = search_columns
        self.max_display_length = max_display_length if max_display_length is not None else self.max_display_length
        self.request = request
        self.column_settings = None

    def render_column(self, row, column):
        # We want to render user as a custom column
        try:
            return self.column_settings[column]['format']

        except KeyError:
            return super(DataTable, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in POST request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            #search logic
            sQuery = get_query(search, self.search_columns)
            qs = qs.filter(sQuery)

        return qs