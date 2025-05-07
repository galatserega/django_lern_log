from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

# Create your views here.


def index(request):
    """The home page for Learning Log."""
    return render(request, 'learning_logs/index.html')

def check_topic_owner(request, topic):
    """Проверяет, является ли пользователь владельцем темы."""
    if topic.owner != request.user:
        raise Http404("You are not allowed to view this topic.")


@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')

    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(request, topic)  # Проверяем, что пользователь является владельцем темы
    entries = topic.entry_set.order_by('-date_added')
    context = {"topic": topic, "entries": entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)  # задерживаем сохранение
            new_topic.owner = request.user       # устанавливаем владельца
            new_topic.save()                     # теперь сохраняем
            return redirect('learning_logs:topics')
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    context = {'topic': topic, "form": form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)

    if request.method != "POST":
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            if request.user != topic.owner:
                raise Http404("You are not allowed to edit this entry.")
            entry = form.save(commit=False)
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {"entry": entry, "topic": topic, "form": form}
    return render(request, 'learning_logs/edit_entry.html', context)
