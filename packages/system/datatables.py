from django.utils.translation import gettext as _
from django_datatables_view.base_datatable_view import BaseDatatableView
from packages.bin.bin import table_dropdown, format_date
from packages.bin.search import get_query

base_url = '/system/users/'
base_template = 'system/users/'


class UsersTable(BaseDatatableView):

    from .models import Users

    second_base = ''

    # The model we're going to show
    model = Users

    # define the columns that will be returned
    columns = ['email', 'users_user_class', 'profile', 'active', 'password', 'status']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['email', 'email', 'profile.firstname', 'active', 'email']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 50

    def get_initial_queryset(self):
        # return queryset used as base for further sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.

        return self.model.pp.filter(status=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'profile':
            return row.profile.get_badge()

        elif column == 'users_user_class':
            tmp = row.users_user_class.all()
            uc = ""
            for x in tmp:
                uc += "<a href='#system/privilege/uc_user-delete/%s/' class='text-danger'>%s</a><br/>" % \
                      (x.id, x.user_class)
            uc = None if uc == "" else uc

            return uc

        elif column == 'password':
            reset_link = "<a ui-WitMVC-href href='#system/users/reset-password/%s/' data-modal='true' " \
                         "class='btn btn-xs bg-orange-700 btn-labeled'>" \
                         "<b><i class='fa fa-refresh'></i></b> <strong>%s</strong>" \
                         "</a>" % (row.pk, _("Reset Password"))

            return reset_link

        elif column == 'active':
            if row.active == 0:
                btn_name = 'Activate'
                btn_link = '#system/users/status/activate/%s/' % row.id

                activate_link = "<a ui-WitMVC-href href='%s' data-action='true' data-method='get' " \
                                "class='btn btn-xs bg-success-800 btn-labeled'>" \
                                "<b><i class='fa fa-lock'></i></b> <strong>%s</strong>" \
                                "</a>" % (btn_link, btn_name)

            else:
                btn_name = 'Deactivate'
                btn_link = '#system/users/status/deactivate/%s/' % row.id

                activate_link = "<a ui-WitMVC-href href='%s' data-action='true' data-method='get' " \
                                "class='btn btn-xs bg-danger-800 btn-labeled'>" \
                                "<b><i class='fa fa-lock'></i></b> <strong>%s</strong>" \
                                "</a>" % (btn_link, btn_name)

            return activate_link

        elif column == 'status':
            actions = [
                {
                    'link': base_url+self.second_base+'update/'+str(row.pk)+'/',
                    'label': _('Update'),
                },
                {
                    'link': base_url+self.second_base+'delete/'+str(row.pk)+'/',
                    'label': _('Delete'),
                }
            ]
            return table_dropdown(actions)
        else:
            return super(self.__class__, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in POST request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            search_query = get_query(search, ['email', 'profile__firstname', 'profile__lastname'])
            qs = qs.filter(search_query)

        return qs
