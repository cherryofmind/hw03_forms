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