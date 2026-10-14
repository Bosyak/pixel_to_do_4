import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import QuestTask, Character, Tag
from .forms import HeroRegistrationForm, QuestTaskForm

def register_view(request):
    if request.method == 'POST':
        form = HeroRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = HeroRegistrationForm()
    return render(request, 'quests/register.html', {'form': form})


@login_required
def dashboard_view(request):
    # Гарантируем, что у каждого юзера есть персонаж (даже у суперюзера)
    character, _ = Character.objects.get_or_create(
        user=request.user, 
        defaults={'hero_name': request.user.username, 'character_class': 'paladin'}
    )

    # Получаем все задачи, где пользователь создатель ИЛИ участник пати
    user_quests = QuestTask.objects.filter(
        Q(creator=request.user) | Q(party=request.user)
    ).distinct().prefetch_related('tags', 'party')

    # Группируем задачи по дням недели (0 - Пн ... 6 - Вс)
    days_board = []
    for day_num, day_name in QuestTask.DAYS_OF_WEEK:
        days_board.append({
            'day_num': day_num,
            'day_name': day_name,
            'quests': user_quests.filter(day_of_week=day_num)
        })

    # Календарь на текущий месяц
    today = date.today()
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(today.year, today.month)
    calendar_data = []
    for week in month_days:
        week_data = []
        for d in week:
            day_quests = user_quests.filter(due_date=d)
            week_data.append({'date': d, 'quests': day_quests, 'is_current_month': d.month == today.month})
        calendar_data.append(week_data)

    form = QuestTaskForm()
    return render(request, 'quests/dashboard.html', {
        'character': character,
        'days_board': days_board,
        'calendar_data': calendar_data,
        'today': today,
        'form': form,
    })


@login_required
def create_or_edit_quest(request, pk=None):
    quest = get_object_or_404(QuestTask, pk=pk) if pk else None
    if request.method == 'POST':
        form = QuestTaskForm(request.POST, instance=quest)
        if form.is_valid():
            saved_quest = form.save(commit=False)
            if not pk:
                saved_quest.creator = request.user
            saved_quest.save()
            form.save_m2m()
            saved_quest.party.add(request.user)  # Создатель всегда в группе

            # Если вписан новый тег
            new_tag_name = form.cleaned_data.get('new_tag')
            if new_tag_name:
                tag, _ = Tag.objects.get_or_create(name=new_tag_name, creator=request.user)
                saved_quest.tags.add(tag)

            return redirect('dashboard')
    return redirect('dashboard')


@login_required
def delete_quest(request, pk):
    quest = get_object_or_404(QuestTask, pk=pk)
    if request.user == quest.creator or request.user in quest.party.all():
        quest.delete()
    return redirect('dashboard')


@login_required
def start_battle_api(request, pk):
    """Переводит задачу в режим активной битвы с монстром."""
    if request.method == 'POST':
        quest = get_object_or_404(QuestTask, pk=pk)
        quest.status = 'in_battle'
        quest.save()
        monster = quest.monster_data
        return JsonResponse({
            'status': 'ok',
            'quest_id': quest.id,
            'quest_title': quest.title,
            'monster_name': monster['name'],
            'monster_hp': monster['hp'],
            'monster_sprite': monster['sprite'],
            'bg': monster['bg'],
            'duration': quest.duration_minutes,
            'party_members': [u.username for u in quest.party.all()]
        })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def finish_battle_api(request, pk):
    """Наносит финальный удар по монстру и начисляет опыт всей группе!"""
    if request.method == 'POST':
        quest = get_object_or_404(QuestTask, pk=pk)
        if quest.status != 'defeated':
            quest.status = 'defeated'
            
            # Если задача ежедневная/еженедельная, можно сбрасывать или клонировать,
            # но для наглядности оставим отметку победы
            quest.save()

            # Начисляем XP и Золото всем участникам группы (кооператив!)
            leveled_up = False
            for member in quest.party.all():
                char, _ = Character.objects.get_or_create(user=member)
                has_lvl_up = char.add_rewards(quest.xp_reward, quest.gold_reward)
                if member == request.user and has_lvl_up:
                    leveled_up = True

            my_char = request.user.character
            return JsonResponse({
                'status': 'victory',
                'xp_gained': quest.xp_reward,
                'gold_gained': quest.gold_reward,
                'leveled_up': leveled_up,
                'new_level': my_char.level,
                'current_xp': my_char.xp,
                'next_xp': my_char.xp_to_next_level,
                'xp_percent': my_char.xp_percentage,
                'gold': my_char.gold
            })
    return JsonResponse({'status': 'error'}, status=400)
