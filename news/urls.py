from django.urls import path
# Импортируем созданное нами представление
from .views import (
   NewsList, NewsDetail, NewsCreate, NewsUpdate, NewsDelete, BaseRegisterView, upgrade_me, subscribe_category, news_edit  #create_news
)
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', NewsList.as_view(), name='news_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', NewsDetail.as_view(), name='news_detail' ),
   #path('create/', create_news, name='news_create'),
   path('create/', NewsCreate.as_view() , name='news_create'),
   path('<int:pk>/update/', NewsUpdate.as_view(), name='news_update'),
   path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
   path('login/',
         LoginView.as_view(template_name = 'news/login.html'),
         name='login'),
   path('logout/',
         LogoutView.as_view(template_name = 'news/logout.html'),
         name='logout'),
   path('newsup/',
         BaseRegisterView.as_view(template_name = 'news/newsup.html'),
         name='newsup'),

   path('upgrade/', upgrade_me, name = 'upgrade'),

    path('news/news/subscribe/<int:category_id>/', subscribe_category, name='subscribe_category'),
    path('news/news/edit/<int:news_id>/', news_edit, name='news_edit'),


]



