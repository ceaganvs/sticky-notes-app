from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Note
from .forms import NoteForm

# Create your views here.


def note_list(request):
    """
    Display a list of all sticky notes.

    Args:
        request: HttpRequest object

    Returns:
        Rendered template with list of all notes
    """
    notes = Note.objects.all()
    context = {
        'notes': notes,
        'total_notes': notes.count()
    }
    return render(request, 'notes/note_list.html', context)


def note_detail(request, pk):
    """
    Display the details of a specific note.

    Args:
        request: HttpRequest object
        pk: Primary key of the note to display

    Returns:
        Rendered template with note details
    """
    note = get_object_or_404(Note, pk=pk)
    context = {
        'note': note
    }
    return render(request, 'notes/note_detail.html', context)


def note_create(request):
    """
    Handle creation of a new sticky note.

    GET: Display empty form
    POST: Process form submission and create note

    Args:
        request: HttpRequest object

    Returns:
        Rendered form template or redirect to note list
    """
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            messages.success(request, f'Note "{note.title}" created successfully!')
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm()

    context = {
        'form': form,
        'action': 'Create'
    }
    return render(request, 'notes/note_form.html', context)


def note_update(request, pk):
    """
    Handle updating an existing sticky note.

    GET: Display form with current note data
    POST: Process form submission and update note

    Args:
        request: HttpRequest object
        pk: Primary key of the note to update

    Returns:
        Rendered form template or redirect to note detail
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            messages.success(request, f'Note "{note.title}" updated successfully!')
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)

    context = {
        'form': form,
        'note': note,
        'action': 'Update'
    }
    return render(request, 'notes/note_form.html', context)


def note_delete(request, pk):
    """
    Handle deletion of a sticky note.

    GET: Display confirmation page
    POST: Delete the note and redirect to list

    Args:
        request: HttpRequest object
        pk: Primary key of the note to delete

    Returns:
        Rendered confirmation template or redirect to note list
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'POST':
        note_title = note.title
        note.delete()
        messages.success(request, f'Note "{note_title}" deleted successfully!')
        return redirect('note_list')

    context = {
        'note': note
    }
    return render(request, 'notes/note_confirm_delete.html', context)
