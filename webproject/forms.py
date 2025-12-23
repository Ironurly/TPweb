from django import forms
from webproject.models import Question, Tag
import re


class AskQuestionForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your question title...',
            'id': 'title'
        })
    )
    text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your question details...',
            'id': 'text',
            'rows': 15
        })
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by spaces...',
            'id': 'tags'
        })
    )

    def clean_tags(self):
        tags_string = self.cleaned_data.get('tags', '')
        if not tags_string:
            return []
        
        tag_names = [tag.strip() for tag in tags_string.split(' ') if tag.strip()]
        
        if len(tag_names) > 5:
            raise forms.ValidationError("Maximum 5 tags allowed")
        
        for tag_name in tag_names:
            if not re.match(r'^[\w-]+$', tag_name):
                raise forms.ValidationError(
                    f"Tag '{tag_name}' contains invalid characters. "
                    "Only letters, numbers, underscore (_), and dash (-) are allowed."
                )
        
        return tag_names

class AnswerForm(forms.Form):
    text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your answer here...',
            'id': 'answer-text',
            'rows': 10
        })
    )

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError("Answer text cannot be empty")
        return text
