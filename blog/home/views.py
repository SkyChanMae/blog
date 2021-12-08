from django.shortcuts import render
from django.urls import reverse
from django.views import View
from home.models import ArticleCategory,Article
from django.http.response import HttpResponseNotFound
# Create your views here.
class IndexView(View):
    def get(self,request):

        categories = ArticleCategory.objects.all()

        cat_id = request.GET.get('cat_id', 1)

        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')

        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)

        articles = Article.objects.filter(category=category)

        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(articles, per_page=page_size)

        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')

        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }

        return render(request,'index.html',context=context)



from home.models import Comment
class DetailView(View):

    def get(self,request):

        id = request.GET.get('id')

        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:

            article.total_views += 1
            article.save()


        categories = ArticleCategory.objects.all()


        hot_articles = Article.objects.order_by('-total_views')[:9]


        page_size = request.GET.get('page_size', 10)
        page_num = request.GET.get('page_num', 1)

        comments = Comment.objects.filter(article=article).order_by('-created')

        total_count = comments.count()

        from django.core.paginator import Paginator,EmptyPage
        paginator = Paginator(comments, page_size)

        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')

        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }
        return render(request,'detail.html',context=context)


