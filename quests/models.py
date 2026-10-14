from django.db import models
from django.contrib.auth.models import User

class Character(models.Model):
    CLASS_CHOICES = [
        ('paladin', 'Паладин Избранных (Танк)'),
        ('mage', 'Маг Солнца (Урон)'),
        ('rogue', 'Разбойник Горных Кланов (Крит)'),
        ('necromancer', 'Некромант Проклятых (Контроль)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='character')
    hero_name = models.CharField("Имя героя", max_length=50)
    character_class = models.CharField("Класс", max_length=20, choices=CLASS_CHOICES, default='paladin')
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)

    @property
    def xp_to_next_level(self):
        # Прогрессия опыта: 1 ур = 100 XP, 2 ур = 250 XP и т.д.
        return int(100 * (self.level ** 1.3))

    @property
    def xp_percentage(self):
        return min(int((self.xp / self.xp_to_next_level) * 100), 100)

    def add_rewards(self, gained_xp, gained_gold):
        self.xp += gained_xp
        self.gold += gained_gold
        leveled_up = False
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            leveled_up = True
        self.save()
        return leveled_up

    def __str__(self):
        return f"{self.hero_name} [{self.get_character_class_display()} - Ур. {self.level}]"


class Tag(models.Model):
    name = models.CharField("Название тега", max_length=30)
    color = models.CharField("Цвет (HEX)", max_length=7, default="#e76e55")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class QuestTask(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Обычный моб (Легко — Слизень)'),
        (2, 'Элитный монстр (Средне — Орк-берсерк)'),
        (3, 'Рейд-Босс (Сложно — Древний Дракон)'),
    ]

    STATUS_CHOICES = [
        ('idle', 'В засаде (Ожидает)'),
        ('in_battle', 'В БОЮ! (Выполняется)'),
        ('defeated', 'Побежден (Выполнено)'),
    ]

    DAYS_OF_WEEK = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    REPEAT_CHOICES = [
        ('none', 'Разовый поход'),
        ('daily', 'Ежедневный дейлик'),
        ('weekly', 'Еженедельный рейд'),
    ]

    title = models.CharField("Название квеста (Имя монстра)", max_length=120)
    description = models.TextField("Описание битвы", blank=True)
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quests')
    party = models.ManyToManyField(User, related_name='party_quests', verbose_name="Группа (Соратники)")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    difficulty = models.IntegerField("Сложность", choices=DIFFICULTY_CHOICES, default=1)
    status = models.CharField("Статус", max_length=15, choices=STATUS_CHOICES, default='idle')

    day_of_week = models.IntegerField("День недели", choices=DAYS_OF_WEEK, default=0)
    due_date = models.DateField("Дата в календаре", null=True, blank=True)
    start_time = models.TimeField("Время начала штурма", null=True, blank=True)
    duration_minutes = models.PositiveIntegerField("Продолжительность боя (мин)", default=30)
    repeat = models.CharField("Повторяемость", max_length=10, choices=REPEAT_CHOICES, default='none')

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def xp_reward(self):
        return {1: 35, 2: 80, 3: 200}.get(self.difficulty, 35)

    @property
    def gold_reward(self):
        return {1: 10, 2: 30, 3: 100}.get(self.difficulty, 10)

    @property
    def monster_data(self):
        # Спрайты из открытых CC0 источников (PokeAPI / OpenGameArt ретро-стиль)
        monsters = {
            1: {
                'name': 'Болотный Слизень',
                'hp': 100,
                'sprite': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/88.gif',
                'bg': 'linear-gradient(180deg, #1a2a1d 0%, #2d4c2b 70%, #142213 100%)'
            },
            2: {
                'name': 'Кровавый Голем',
                'hp': 350,
                'sprite': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/623.gif',
                'bg': 'linear-gradient(180deg, #2b1d1d 0%, #4c2b2b 70%, #1e1111 100%)'
            },
            3: {
                'name': 'Теневой Дракон Гараан',
                'hp': 1000,
                'sprite': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/635.gif',
                'bg': 'linear-gradient(180deg, #1b0c2e 0%, #3d1b5c 70%, #12061c 100%)'
            }
        }
        return monsters.get(self.difficulty, monsters[1])

    def __str__(self):
        return self.title
