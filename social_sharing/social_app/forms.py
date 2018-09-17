from django import forms


class EventForm(forms.Form):
    title = forms.CharField()
    hashtag = forms.CharField()
    location = forms.CharField()
    time = forms.CharField()
    description = forms.Textarea()
    file = forms.FileField()

