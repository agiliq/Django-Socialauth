from django import  template

register = template.Library()

@register.simple_tag
def get_calculated_username(user):
    if hasattr(user, 'openidprofile_set') and user.openidprofile_set.filter().count():
        if user.openidprofile_set.filter(is_username_valid = True).count():
            return user.openidprofile_set.filter(is_username_valid = True)[0].user.username
        else:
            from django.core.urlresolvers import  reverse
            editprof_url = reverse('socialauth_editprofile')
            return u'Anonymous User. <a href="%s">Add name</a>'%editprof_url
    else:
        return user.username
