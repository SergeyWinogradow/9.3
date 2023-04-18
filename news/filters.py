from django_filters import FilterSet, DateFilter, ModelChoiceFilter, ModelMultipleChoiceFilter
from .models import News, Category
from django import forms

# Создаем свой набор фильтров для модели News.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class NewsFilter(FilterSet):
   category = ModelMultipleChoiceFilter(
      field_name='category',
      queryset=Category.objects.all(),
      #label='Category',
      #empty_label='Выберите вариант'
   )


   published_date =DateFilter(
       field_name='publish_date',
       lookup_expr='gt',
       widget=forms.DateInput(attrs={'type': 'date'}),
       label='Дата'
   )

   class Meta:
       # В Meta классе мы должны указать Django модель,
       # в которой будем фильтровать записи.
       model = News
       # В fields мы описываем по каким полям модели
       # будет производиться фильтрация.
       fields = {
           # поиск по названию
           'name': ['icontains'],
           # количество новостей должно быть больше
           #'publish_date': ['gt'],
           'category': ['exact'],
           'author': ['exact'],

       }