from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        label = {
            'text': ('Текст поста'),
            'group': ('Группа поста')
        }
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа, к которой будет относиться пост')
        }
