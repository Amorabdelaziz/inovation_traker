from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Comment, Idea


class IdeaForm(forms.ModelForm):
    new_category_name = forms.CharField(
        required=False,
        max_length=50,
        help_text='Add a new category if none of the existing options fit.',
    )
    new_category_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text='Optional description for the new category.',
    )

    class Meta:
        model = Idea
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            field.widget.attrs.setdefault('class', css_class)
        self.fields['category'].required = False

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category_name = (cleaned_data.get('new_category_name') or '').strip()

        if new_category_name:
            existing = Category.objects.filter(name__iexact=new_category_name).first()
            if existing:
                cleaned_data['category'] = existing
                cleaned_data['new_category_name'] = ''
            else:
                cleaned_data['new_category_name'] = new_category_name

        if not cleaned_data.get('category') and not cleaned_data.get('new_category_name'):
            raise forms.ValidationError('Select a category or provide a new one.')
        return cleaned_data

    def save(self, commit=True):
        idea = super().save(commit=False)
        new_category_name = self.cleaned_data.get('new_category_name')
        new_category_description = (self.cleaned_data.get('new_category_description') or '').strip()

        if new_category_name:
            name = new_category_name.strip()
            if name:
                category, created = Category.objects.get_or_create(
                    name=name,
                    defaults={'description': new_category_description},
                )
                if not created and new_category_description and not category.description:
                    category.description = new_category_description
                    category.save(update_fields=['description'])
                idea.category = category

        if commit:
            idea.save()
        return idea


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.setdefault('class', 'form-control')


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class IdeaStatusForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.setdefault('class', 'form-select')

