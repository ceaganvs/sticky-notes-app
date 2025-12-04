from django.db import models
from django.urls import reverse

# Create your models here.


class Note(models.Model):
    """
    Model representing a sticky note.

    Attributes:
        title: The title of the note (max 200 characters)
        content: The main content of the note (unlimited text)
        created_at: Timestamp when the note was created
        updated_at: Timestamp when the note was last modified
    """
    title = models.CharField(max_length=200, help_text="Enter the note title")
    content = models.TextField(help_text="Enter the note content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Most recent notes first
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        """String representation of the Note object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this note."""
        return reverse('note_detail', args=[str(self.id)])
