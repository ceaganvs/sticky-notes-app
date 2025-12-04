from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    """
    Form for creating and editing sticky notes.

    Uses Django's ModelForm to automatically generate form fields
    based on the Note model.
    """

    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note title',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note content',
                'rows': 6
            })
        }
        labels = {
            'title': 'Title',
            'content': 'Content'
        }
        help_texts = {
            'title': 'Maximum 200 characters',
            'content': 'Add your note content here'
        }

    def clean_title(self):
        """Validate that the title is not empty or just whitespace."""
        title = self.cleaned_data.get('title')
        if title and not title.strip():
            raise forms.ValidationError("Title cannot be empty or just whitespace.")
        return title.strip() if title else title

    def clean_content(self):
        """Validate that the content is not empty or just whitespace."""
        content = self.cleaned_data.get('content')
        if content and not content.strip():
            raise forms.ValidationError("Content cannot be empty or just whitespace.")
        return content.strip() if content else content
