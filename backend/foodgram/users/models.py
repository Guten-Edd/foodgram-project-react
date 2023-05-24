from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class MyUser(AbstractUser):
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    USERS_ROLE = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_ADMIN, 'Админ'),
    )
    role = models.CharField(
        choices=USERS_ROLE,
        max_length=10,
        verbose_name='Роль пользователя',
        default=ROLE_USER,
    )
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]',
                           message='Недопустимые символы в имени пользователя')
        ]
    )
    password = models.CharField('Пароль', max_length=150,)
    email = models.EmailField(
        'e-mail',
        max_length=254,
        unique=True,
        )
    first_name = models.TextField('Имя', max_length=150,)
    last_name = models.TextField('Фамилия', max_length=150,)

    class Meta:
        ordering = ['-date_joined',]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик на автора рецепта'
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_object'
        )]

    def __str__(self) -> str:
        return (f'Пользователь {self.user.username}'
                f' подписан на {self.author.username}')
