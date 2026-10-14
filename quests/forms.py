from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Character, QuestTask, Tag

class HeroRegistrationForm(UserCreationForm):
    hero_name = forms.CharField(label="Имя вашего героя", max_length=50)
    character_class = forms.ChoiceField(label="Выберите класс", choices=Character.CLASS_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('hero_name', 'character_class')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Character.objects.create(
                user=user,
                hero_name=self.cleaned_data['hero_name'],
                character_class=self.cleaned_data['character_class']
            )
        return user


class QuestTaskForm(forms.ModelForm):
    new_tag = forms.CharField(
        label="Новый тег (необязательно)", 
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Например: #МагияКода'})
    )

    class Meta:
        model = QuestTask
        fields = [
            'title', 'description', 'difficulty', 'day_of_week', 
            'due_date', 'start_time', 'duration_minutes', 'repeat', 
            'tags', 'party'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
