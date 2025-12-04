from django.test import TestCase, Client
from django.urls import reverse
from .models import Note
from .forms import NoteForm


class NoteModelTest(TestCase):
    """Test cases for the Note model."""

    def setUp(self):
        """Set up test data."""
        self.note = Note.objects.create(
            title="Test Note",
            content="This is test content."
        )

    def test_note_creation(self):
        """Test that a note is created with correct attributes."""
        self.assertEqual(self.note.title, "Test Note")
        self.assertEqual(self.note.content, "This is test content.")
        self.assertIsNotNone(self.note.created_at)
        self.assertIsNotNone(self.note.updated_at)

    def test_note_str_method(self):
        """Test the string representation of a note."""
        self.assertEqual(str(self.note), "Test Note")

    def test_note_ordering(self):
        """Test notes are ordered by creation date (newest first)."""
        note1 = Note.objects.create(
            title="First Note",
            content="First content"
        )
        note2 = Note.objects.create(
            title="Second Note",
            content="Second content"
        )
        notes = Note.objects.all()
        self.assertEqual(notes[0], note2)
        self.assertEqual(notes[1], note1)

    def test_note_get_absolute_url(self):
        """Test the get_absolute_url method."""
        expected_url = reverse('note_detail', args=[str(self.note.id)])
        self.assertEqual(self.note.get_absolute_url(), expected_url)


class NoteFormTest(TestCase):
    """Test cases for the NoteForm."""

    def test_form_valid_data(self):
        """Test form with valid data."""
        form = NoteForm(data={
            'title': 'Valid Title',
            'content': 'Valid Content'
        })
        self.assertTrue(form.is_valid())

    def test_form_empty_title(self):
        """Test form rejects empty title."""
        form = NoteForm(data={
            'title': '',
            'content': 'Some content'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_empty_content(self):
        """Test form rejects empty content."""
        form = NoteForm(data={
            'title': 'Some title',
            'content': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_whitespace_only_title(self):
        """Test form rejects whitespace-only title."""
        form = NoteForm(data={
            'title': '   ',
            'content': 'Valid content'
        })
        self.assertFalse(form.is_valid())

    def test_form_whitespace_only_content(self):
        """Test form rejects whitespace-only content."""
        form = NoteForm(data={
            'title': 'Valid title',
            'content': '   '
        })
        self.assertFalse(form.is_valid())

    def test_form_title_max_length(self):
        """Test form rejects title exceeding max length."""
        long_title = 'x' * 201
        form = NoteForm(data={
            'title': long_title,
            'content': 'Valid content'
        })
        self.assertFalse(form.is_valid())


class ViewNotesUseCaseTest(TestCase):
    """Test cases for viewing notes (Use Case: View Notes)."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()

    def test_view_empty_notes_list(self):
        """Test viewing notes list when no notes exist."""
        url = reverse('note_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_list.html')
        self.assertEqual(response.context['total_notes'], 0)
        self.assertContains(response, 'No notes yet!')

    def test_view_notes_list_with_multiple_notes(self):
        """Test viewing list with multiple notes."""
        Note.objects.create(title="Note 1", content="Content 1")
        Note.objects.create(title="Note 2", content="Content 2")
        Note.objects.create(title="Note 3", content="Content 3")

        url = reverse('note_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_notes'], 3)
        self.assertContains(response, "Note 1")
        self.assertContains(response, "Note 2")
        self.assertContains(response, "Note 3")

    def test_view_note_details(self):
        """Test viewing details of a specific note."""
        note = Note.objects.create(
            title="Detail Test",
            content="Detailed content here"
        )
        url = reverse('note_detail', args=[note.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_detail.html')
        self.assertContains(response, "Detail Test")
        self.assertContains(response, "Detailed content here")

    def test_view_nonexistent_note_returns_404(self):
        """Test viewing non-existent note returns 404."""
        url = reverse('note_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CreateNoteUseCaseTest(TestCase):
    """Test cases for creating notes (Use Case: Create Note)."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('note_create')

    def test_create_note_form_display(self):
        """Test create note form is displayed correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_create_note_with_valid_data(self):
        """Test creating a note with valid data."""
        initial_count = Note.objects.count()
        data = {
            'title': 'New Test Note',
            'content': 'This is new content'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Note.objects.count(), initial_count + 1)

        note = Note.objects.latest('created_at')
        self.assertEqual(note.title, 'New Test Note')
        self.assertEqual(note.content, 'This is new content')
        self.assertRedirects(
            response,
            reverse('note_detail', args=[note.pk])
        )

    def test_create_note_with_invalid_data(self):
        """Test creating note with invalid data shows errors."""
        data = {
            'title': '',
            'content': 'Content without title'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'title',
            'This field is required.'
        )

    def test_create_note_with_long_title(self):
        """Test creating note with title exceeding max length."""
        data = {
            'title': 'x' * 201,
            'content': 'Valid content'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Note.objects.count(), 0)
        self.assertFormError(
            response.context['form'],
            'title',
            'Ensure this value has at most 200 characters (it has 201).'
        )


class EditNoteUseCaseTest(TestCase):
    """Test cases for editing notes (Use Case: Edit Note)."""

    def setUp(self):
        """Set up test client and note."""
        self.client = Client()
        self.note = Note.objects.create(
            title="Original Title",
            content="Original Content"
        )
        self.url = reverse('note_update', args=[self.note.pk])

    def test_edit_note_form_display(self):
        """Test edit note form displays with current data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')
        self.assertContains(response, "Original Title")
        self.assertContains(response, "Original Content")

    def test_edit_note_with_valid_data(self):
        """Test editing note with valid data."""
        data = {
            'title': 'Updated Title',
            'content': 'Updated Content'
        }
        response = self.client.post(self.url, data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Title')
        self.assertEqual(self.note.content, 'Updated Content')
        self.assertRedirects(
            response,
            reverse('note_detail', args=[self.note.pk])
        )

    def test_edit_note_with_invalid_data(self):
        """Test editing note with invalid data preserves original."""
        data = {
            'title': '',
            'content': 'Updated content'
        }
        response = self.client.post(self.url, data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Original Title')
        self.assertEqual(response.status_code, 200)

    def test_edit_nonexistent_note_returns_404(self):
        """Test editing non-existent note returns 404."""
        url = reverse('note_update', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DeleteNoteUseCaseTest(TestCase):
    """Test cases for deleting notes (Use Case: Delete Note)."""

    def setUp(self):
        """Set up test client and note."""
        self.client = Client()
        self.note = Note.objects.create(
            title="Note to Delete",
            content="This will be deleted"
        )
        self.url = reverse('note_delete', args=[self.note.pk])

    def test_delete_confirmation_page(self):
        """Test delete confirmation page is displayed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_confirm_delete.html')
        self.assertContains(response, "Note to Delete")

    def test_delete_note_successfully(self):
        """Test deleting a note removes it from database."""
        initial_count = Note.objects.count()
        response = self.client.post(self.url)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertRedirects(response, reverse('note_list'))

    def test_delete_nonexistent_note_returns_404(self):
        """Test deleting non-existent note returns 404."""
        url = reverse('note_delete', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class URLRoutingTest(TestCase):
    """Test cases for URL routing."""

    def test_note_list_url(self):
        """Test note list URL resolves correctly."""
        url = reverse('note_list')
        self.assertEqual(url, '/notes/')

    def test_note_detail_url(self):
        """Test note detail URL resolves correctly."""
        url = reverse('note_detail', args=[1])
        self.assertEqual(url, '/notes/1/')

    def test_note_create_url(self):
        """Test note create URL resolves correctly."""
        url = reverse('note_create')
        self.assertEqual(url, '/notes/create/')

    def test_note_update_url(self):
        """Test note update URL resolves correctly."""
        url = reverse('note_update', args=[1])
        self.assertEqual(url, '/notes/1/edit/')

    def test_note_delete_url(self):
        """Test note delete URL resolves correctly."""
        url = reverse('note_delete', args=[1])
        self.assertEqual(url, '/notes/1/delete/')

