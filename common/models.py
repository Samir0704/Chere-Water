from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from django.utils.translation import gettext_lazy as _


class Media(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', _('Image')
        VIDEO = 'video', _('Video')
        AUDIO = 'audio', _('Audio')
        OTHER = 'other', _('Other')

    file = models.FileField(_('file'), upload_to='all_media_files/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'mp4', 'mp3'])])
    type = models.CharField(_('type'), max_length=20, choices=MediaType.choices, default=MediaType.IMAGE)

    def __str__(self):
        return f"{self.file.name}-{self.type}"

    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Medias')

    def clean(self):
        if self.type == Media.MediaType.IMAGE:
            if not self.file.name.split(".")[-1] in ['jpg', 'jpeg', 'png']:
                raise ValidationError(_('Only jpg, jpeg, png are allowed'))
        elif self.type == Media.MediaType.VIDEO:
            if not self.file.name.split(".")[-1] in ['mp4']:
                raise ValidationError(_('Only mp4 are allowed'))



