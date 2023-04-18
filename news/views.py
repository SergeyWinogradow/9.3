# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from datetime import datetime

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView)
from .models import News, Category
from .filters import NewsFilter
from django.shortcuts import redirect, render, get_object_or_404
from .forms import NewsForm

from django.contrib.auth.models import User

from .models import BaseRegisterForm


from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import PermissionRequiredMixin



class AddNews(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_news', )
    # // customize form view


# Теперь нам нужно добавить ещё одно view для апгрейда аккаунта.
# Иными словами, для добавления в группу authors.
# поэтому напишем функцию-представление.
#
# не забывая импортировать модель групп, и декоратор проверки аутентификации.



@login_required
def news_edit(request, news_id):
    news = get_object_or_404(News, id=news_id)

    try:
        category_id = news.category.id
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        category = None


    return render(request, 'news_edit.html', {'news': news, 'category': category})


@login_required
def subscribe_category(request, category_id):

        category = Category.objects.get(id=category_id)
        category.subscribers.add(request.user)
        return redirect('news_edit', news_id=category.news.first().id)

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')



class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'

# class ProtectedView(TemplateView):
#     template_name = 'prodected_page.html'
#
#     @method_decorator(login_required, name='dispatch')
#     class ProtectedView(TemplateView):
#         template_name = 'prodected_page.html'

# class ProtectedView(LoginRequiredMixin, TemplateView):
#     template_name = 'news_edit.html'



class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view, login_url='/login/')

class ArticleEditView(LoginRequiredMixin, UpdateView):
    model = News
    template_name = 'news_edit.html'
    fields = [
              'name',
              'description',
              'category',
              'published_date',
              'author'
              ]
    success_url = reverse_lazy('news_list')

class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = News
    # Поле, которое будет использоваться для сортировки объектов
    ordering = 'name'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'newss.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'newss'
    paginate_by = 10  # вот так мы можем указать количество записей на странице

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.

        self.filterset = NewsFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


    # # Метод get_context_data позволяет нам изменить набор данных,
    # # который будет передан в шаблон.
    # def get_context_data(self, **kwargs):
    #     # С помощью super() мы обращаемся к родительским классам
    #     # и вызываем у них метод get_context_data с теми же аргументами,
    #     # что и были переданы нам.
    #     # В ответе мы должны получить словарь.
    #     #context = super().get_context_data(**kwargs)
    #     # К словарю добавим текущую дату в ключ 'time_now'.
    #     context['time_now'] = datetime.utcnow()
    #     # Добавим ещё одну пустую переменную,
    #     # чтобы на её примере рассмотреть работу ещё одного фильтра.
    #     context['next_sale'] = "Важная новость!"
    #     return context

class NewsDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельно новости
    model = News
    # Используем другой шаблон — news.html
    template_name = 'news.html'
    # Название объекта, в котором будет выбранный пользователем
    context_object_name = 'news'

# Добавляем новое представление для создания новостей.
class NewsCreate(CreateView):
    # Указываем нашу разработанную форму
    form_class = NewsForm
    # модель news
    model = News
    # и новый шаблон, в котором используется форма.
    template_name = 'news_edit.html'



    # def form_valid(self, form):
    #     news = form.save(commit=False)
    #     news.author = 2
    #     return super().form_valid(form)

# def create_news(request):
#     form = NewsForm()
#
#     if request.method == 'POST':
#         form = NewsForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/news/')
#
#     return render(request, 'news_edit.html', {'form': form })

# Добавляем представление для изменения новостей.
class NewsUpdate(UpdateView):
    form_class = NewsForm
    model = News
    template_name = 'news_edit.html'

# Представление удаляющее новость.
class NewsDelete(DeleteView):
    model = News
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')