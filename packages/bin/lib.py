
# Comma separator for ,000 long numeric values
def value_separator(value):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US')
    return locale.format("%d", value, grouping=True)


def number_choice(start=1, end=100, step=1):
    objs = range(start,end)[::step]
    choice = []
    for obj in objs:
        choice.append((str(obj), str(obj)),)
    
    return tuple(choice)


def given_year(start=1970, end=2048):
    from datetime import datetime

    if end == 'now':
        end = int(datetime.now().year) + 1
    
    default = datetime.now().year
    choices = number_choice(start, end)
    
    return choices, default


def given_month():
    from datetime import datetime
    from packages.bin.dictionary import Month
    
    current_month = datetime.now().month
    default = Month.month_name[current_month-1]
    choices = []
    
    for month in Month.month_name:
        choices.append((month, month),)
    
    return tuple(choices), default


def path_and_rename(instance, filename):
    import hashlib,datetime
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(instance.reference + str(datetime.datetime.now())).hexdigest() + ext
    return '/'.join(['dmc/geoqinetiq/hr/photos', filename])


def cert_path_and_rename(instance, filename):
    import hashlib,datetime
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(instance.profile.reference + str(datetime.datetime.now())).hexdigest() + ext
    return '/'.join(['dmc/geoqinetiq/hr/certificate', filename])


def asset_path_and_rename(instance, filename):
    import hashlib
    import datetime
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(filename + str(datetime.datetime.now())).hexdigest() + ext
    return '/'.join(['dmc/geoqinetiq/asset', filename])


def get_thumb(path, version='128x128'):
    ext = '.' + path.split('.')[-1]
    filename = "".join(path.split('.')[:-1])
    return filename + '.' + version + ext


def get_query_string(request):
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']

    return queries_without_page


def remove_prev_photo(url):

    import os
    from django.conf import settings

    #delete any previous image
    try:
        url = str(url)
        #get actual file name
        ext = '.' + url.split('.')[-1]
        filename = "".join(url.split('.')[:-1])
        fn = []
        fn.append(settings.MEDIA_ROOT + '/' + filename + ext)
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.64x64' + ext)
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.128x128' + ext)
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.256x256' + ext)
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.512x512' + ext)
        fn.append(settings.MEDIA_ROOT + '/' + filename + '.1024x1024' + ext)

        for f in fn:
            try:
                os.path.exists(f) and os.remove(f)
            except OSError:
                pass

    except (KeyError, ValueError, AttributeError):
        pass


def autocomplete_state(queryset=None, instance_var=None, url=None, element=None, token=1):

    print instance_var

    if instance_var is None or instance_var == []:
        json_object = ""

    elif token > 1:
        try:
            try:
                tmp = instance_var
            except (ValueError, AttributeError):
                tmp = ""

            if type(tmp) == str or type(tmp) == unicode:
                m_objects = tmp.split(',')
            else:
                m_objects = []
                for m_object in tmp:
                    m_objects.append(m_object.id)

            arr = []
            for m_object in m_objects:
                r_object = queryset.get(id=m_object)
                arr.append('''{'id':'%s', 'name':"%s"}''' % (str(m_object), r_object))

            json_object = ''', prePopulate: [%s]''' % (','.join(arr)) if arr else ""

        except (ValueError, UnboundLocalError):
            json_object = ""

    else:
        try:
            json_object = ''', prePopulate: [{'id':'%s', 'name':'%s'}]''' % (str(instance_var.id), instance_var)

        except (ValueError, UnboundLocalError):
            json_object = ""

    #script for form
    script = '''
    <script>
    $(document).ready(function(){
        $('#%s').tokenInput('%s', {theme:'wit', tokenLimit:%s, hintText:'Start typing name' %s});
    });
    </script>''' % (element, url, token, json_object)

    return script