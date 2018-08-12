from django.forms import Form, ModelForm, CharField, Textarea
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import ForumPost, ForumThread, ForumBoard, ForumPostEdit


class NewThreadForm(Form):
    title = CharField(label=_("Thread title"), max_length=128, required=True)
    message = CharField(label=_("First message"), required=True, widget=Textarea)

    def __init__(self, *args, **kwargs):
        super(NewThreadForm, self).__init__(*args, **kwargs)
        self.fields['message'].widget.attrs['class'] = 'bbcode_field'
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Post')))

    @transaction.atomic
    def save(self, board, user):
        thread = ForumThread.objects.create(
            board=board,
            user=user,
            title=self.cleaned_data['title']
        )
        post = ForumPost.objects.create(
            thread=thread,
            user=user,
            message=self.cleaned_data['message']
        )
        return thread, post


class NewMessageForm(Form):
    message = CharField(label='', required=True, widget=Textarea)

    def __init__(self, *args, **kwargs):
        super(NewMessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].widget.attrs['class'] = 'bbcode_field'
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Post')))

    @transaction.atomic
    def save(self, thread, user):
        thread.set_modified()
        post = ForumPost.objects.create(
            thread=thread,
            user=user,
            message=self.cleaned_data['message']
        )
        return thread, post


class MoveThreadForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoveThreadForm, self).__init__(*args, **kwargs)
        self.fields['board'].queryset = ForumBoard.objects.filter(deleted=False)\
            .order_by('section__sort_index', 'sort_index')
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Post')))

    class Meta:
        model = ForumThread
        fields = ('board', )


class EditMessageForm(ModelForm):
    title = CharField(label=_("Thread title"), max_length=128, required=True)
    edit_note = CharField(label=_("Edit note"), max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EditMessageForm, self).__init__(*args, **kwargs)
        if not self.instance.is_first:
            del self.fields['title']
        else:
            self.fields['title'].initial = self.instance.thread.title

        # Only allow attaching galleries for staff
        if not self.user.is_staff:
            del self.fields['attached_gallery']

        self.fields['message'].widget.attrs['class'] = 'bbcode_field'
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Post')))

    def save(self, commit=True):
        post = super(EditMessageForm, self).save(commit)
        if self.instance.is_first:
            self.instance.thread.title = self.cleaned_data['title']
            if commit:
                self.instance.thread.save()

        edit = ForumPostEdit(
            post=post,
            message=self.cleaned_data['edit_note'],
            editor=self.user.profile.alias
        )
        if commit:
            edit.save()

        return post, edit

    class Meta:
        model = ForumPost
        fields = ('title', 'message', 'edit_note', 'attached_gallery')
