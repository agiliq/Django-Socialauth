from django import forms
from django.conf import settings

from socialauth.models import AuthMeta


ALLOW_MULTIPLE_USERNAME_EDITS = getattr(settings, 'ALLOW_MULTIPLE_USERNAME_EDITS', False)

class EditProfileForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length = 100, widget= forms.PasswordInput, required=False, help_text='If you give a password, you can login via a login form as well.')
    password2 = forms.CharField(max_length = 100, widget= forms.PasswordInput, required=False, label='Repeat password')
    first_name = forms.CharField(max_length = 100, required=False)
    last_name = forms.CharField(max_length = 100, required=False)
    
    def __init__(self, user=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.user:
            self.initial = {'email': user.email,  \
                        'first_name':user.first_name, 'last_name':user.last_name}
            
    def clean(self):
        cleaned_data = self.cleaned_data
        if 'password' in cleaned_data or 'password2' in cleaned_data:
            if 'password' in cleaned_data and 'password2' in cleaned_data:
                if cleaned_data['password'] != cleaned_data['password2']:
                    raise forms.ValidationError('The passwords do not match.')
            else:
                raise forms.ValidationError('Either ener both or None of the password fields')
                    
        return cleaned_data      
        
    def save(self):
        user = self.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
            user.set_password(self.cleaned_data['password'])
        user.save()
        try:
            authmeta = user.authmeta
            authmeta.is_email_filled = True
            authmeta.is_profile_modified = True
            authmeta.save()
        except AuthMeta.DoesNotExist:
            pass
        return user
        
        
