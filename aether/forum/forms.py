from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db import transaction
from django.forms import CharField, Form, ModelForm, Textarea
from django.utils.translation import gettext_lazy as _

from .models import ForumBoard, ForumPost, ForumPostEdit, ForumThread


class NewThreadForm(ModelForm):
    title = CharField(label=_("Thread title"), max_length=128, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.board = kwargs.pop("board")
        super(NewThreadForm, self).__init__(*args, **kwargs)

        # Only allow attaching galleries for staff
        self.fields["attached_gallery"].required = False
        if not self.user.is_staff:
            del self.fields["attached_gallery"]

        self.fields["message"].widget.attrs["class"] = "bbcode_field"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Post")))

    @transaction.atomic
    def save(self, commit=True):
        thread = ForumThread(board=self.board, user=self.user, title=self.cleaned_data["title"])
        if commit:
            thread.save()

        post = super(NewThreadForm, self).save(commit=False)
        post.thread = thread
        post.user = self.user
        if commit:
            post.save()
        return post

    class Meta:
        model = ForumPost
        fields = ("title", "message", "attached_gallery")


class NewMessageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.thread = kwargs.pop("thread")
        super(NewMessageForm, self).__init__(*args, **kwargs)

        # Only allow attaching galleries for staff
        self.fields["attached_gallery"].required = False
        if not self.user.is_staff:
            del self.fields["attached_gallery"]

        self.fields["message"].widget.attrs["class"] = "bbcode_field"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Post")))

    @transaction.atomic
    def save(self, commit=True):
        self.thread.set_modified()
        post = super(NewMessageForm, self).save(commit=False)
        post.user = self.user
        post.thread = self.thread
        if commit:
            post.save()
        return post

    class Meta:
        model = ForumPost
        fields = ("message", "attached_gallery")


class MoveThreadForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoveThreadForm, self).__init__(*args, **kwargs)
        self.fields["board"].queryset = ForumBoard.objects.filter(deleted=False).order_by(
            "section__sort_index", "sort_index"
        )
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Post")))

    class Meta:
        model = ForumThread
        fields = ("board",)


class EditMessageForm(ModelForm):
    title = CharField(label=_("Thread title"), max_length=128, required=True)
    edit_note = CharField(label=_("Edit note"), max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(EditMessageForm, self).__init__(*args, **kwargs)
        if self.instance.is_first:
            self.fields["title"].initial = self.instance.thread.title
        else:
            del self.fields["title"]

        # Only allow attaching galleries for staff
        self.fields["attached_gallery"].required = False
        if not self.user.is_staff:
            del self.fields["attached_gallery"]

        self.fields["message"].widget.attrs["class"] = "bbcode_field"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Post")))

    def save(self, commit=True):
        post = super(EditMessageForm, self).save(commit)
        if self.instance.is_first:
            self.instance.thread.title = self.cleaned_data["title"]
            if commit:
                self.instance.thread.save()

        edit = ForumPostEdit(
            post=post, message=self.cleaned_data["edit_note"], editor=self.user.profile.alias
        )
        if commit:
            edit.save()

        return post, edit

    class Meta:
        model = ForumPost
        fields = ("title", "message", "edit_note", "attached_gallery")
