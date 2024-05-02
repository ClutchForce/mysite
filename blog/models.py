from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from taggit.models import Tag as TaggitTag
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from modelcluster.tags import ClusterTaggableManager
# from wagtail.routable_page.models import RoutablePageMixin
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
from django.http import Http404
from django.utils.functional import cached_property

from .block import Body_block
from wagtail.fields import StreamField

from wagtail.search import index

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
#import meta data MetadataPageMixin
from wagtailmetadata.models import MetadataPageMixin
from .views import contact_send_mail, contact_send_mail2
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.functional import cached_property




class FieldForm (AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')
    
class FormPage (AbstractEmailForm):
    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('form_fields', label="Field Form"),
    ]
    @cached_property
    def blogpage (self):
        return self.get_parent().specific
    
    def get_context(self, request, *args, **kwargs):
        context = super(FormPage, self).get_context(request, *args, **kwargs)
        context['blogpage'] = self.blogpage

        if request.method == 'POST':
            name = request.POST.get('form_label')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if name and email and subject and message:
                contact_send_mail2(request, subject, message, email)
                print(messages.get_messages(request))
                #return redirect(self.url)  # Redirect to the same page

        return context
    
    # def get_context(self, request, *args, **kwargs):
    #     context = super(FormPage, self).get_context(request, *args, **kwargs)
    #     context['blogpage'] = self.blogpage
    #     return context
    
    # def serve(self, request, *args, **kwargs):
    #     # Log the messages
    #     for message in messages.get_messages(request):
    #         print(f"Message: {message}")
    #     if request.method == 'POST':
    #         print(request.session.keys())
    #         form = self.get_form(request.POST, request.FILES)

    #         if form.is_valid():
    #             # Process the form
    #             name = form.cleaned_data['form_label']
    #             email = form.cleaned_data['email']
    #             subject = form.cleaned_data['subject']
    #             message = form.cleaned_data['message']

    #             if name and email and subject and message:
    #                 contact_send_mail2(request, subject, message, email)
    #                 # Add a success message
    #                 # messages.success(request, "Email sent successfully")

    #             # Redirect to the same page or a 'thank you' page
    #             print(self.url)
    #             return HttpResponseRedirect(self.url)

        # If GET or form is not valid, render the page as usual
    #    return super().serve(request, *args, **kwargs)




# Create your models here.
class Blogpage (RoutablePageMixin,  Page):
    description = models.CharField(max_length=250, blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]
    
    def get_context (self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['blogpage'] = self
        paginator = Paginator(self.posts, 4)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.object_list.none()
        context['posts'] = posts
        return context
    
    def get_posts (self):
        return PostPage.objects.descendant_of(self).live().order_by('-post_date')
    
    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(post_date__year=year)
        if month:
            self.posts = self.posts.filter(post_date__month=month)
        if day:
            self.posts = self.posts.filter(post_date__day=day)
        return self.render(request)
    
    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        postpage = self.get_posts().filter(slug=slug).first()
        if not postpage:
            raise Http404
        return postpage.serve(request)
    
    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag):
        self.filter_term = tag
        self.filter_type = "tag"
        self.posts = self.get_posts().filter(tags__slug=tag)
        return self.render(request)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category):
        self.filter_term = category
        self.filter_type = "category"
        self.posts = self.get_posts().filter(categories__blog_category__slug=category)
        return self.render(request)

    @route(r'^$') 
    def post_list(self, request):
        self.posts = self.get_posts()
        return self.render(request)
    
    @route(r'^search/$')
    def post_search(self, request):
        search_query = request.GET.get('q', None)
        self.posts = self.get_posts()
        if search_query:
            self.filter_term = search_query
            self.filter_type = "search"
            self.posts = self.posts.search(search_query)
        return self.render(request)
    
    
class PostPage(MetadataPageMixin, Page):
    description = models.CharField(max_length=250, blank=True)
    header_image = models.ForeignKey("wagtailimages.Image", blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    tags = ClusterTaggableManager(through='PostPageTag', blank=True)
    
    body = StreamField(Body_block(), blank=True, use_json_field=True)
    
    post_date = models.DateTimeField(verbose_name="post date", default=datetime.date.today)
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('header_image'),
        FieldPanel('tags'),
        InlinePanel('categories', label="category"),
        FieldPanel('body'),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('post_date'),
    ]
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('title'),
    ]
    
    def get_context (self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['blogpage'] = self.blogpage
        return context 
    
    @cached_property
    def blogpage (self):
        return self.get_parent().specific
    
    @cached_property
    def canonical_url (self):
        from .templatetags.blogapp_tags import post_page_date_slug_url
        blogpage = self.blogpage
        return post_page_date_slug_url(self, blogpage)
    
class PostPageBlogCategory(models.Model):
    Page = ParentalKey('blog.PostPage', on_delete = models.CASCADE, blank = True, related_name='categories')
    blog_category = models.ForeignKey('blog.BlogCategory', related_name='post_pages', on_delete=models.CASCADE, blank = True)
    panels = [
        FieldPanel('blog_category'),
    ]
    class Meta:
        unique_together = ('Page', 'blog_category')

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
        
class PostPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.PostPage', blank=True)
        
@register_snippet
class Tag (TaggitTag):
    class Meta:
        proxy = True