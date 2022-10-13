from django.contrib import admin
from .models import Post, Group, Comment
from django.conf import settings


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = settings.EMPTY_VALUE_FILLER


admin.site.register(Group)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created', 'text')
    list_filter = ('created',)
    search_fields = ('author', 'text')


admin.site.register(Comment, CommentAdmin)
