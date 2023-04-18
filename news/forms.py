from django import forms
from django.core.exceptions import ValidationError
from .models import News

class NewsForm(forms.ModelForm):
   #description = forms.CharField(min_length=200)

   class Meta:
       model = News
       #fields = '__all__' - все поля автоматом
       fields = [

           'name',
           'description',
           'category',
           'published_date',
           'author',
       ]

   def clean(self):
       cleaned_data = super().clean()
       name = cleaned_data.get("name")
       description = cleaned_data.get("description")

       if name == description:
           raise ValidationError(
               "Описание не должно быть идентично названию."
           )

       return cleaned_data