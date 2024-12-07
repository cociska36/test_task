from django.db import models
from aiogram import Bot
from django.conf import settings

class User(models.Model):
    user_id = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        db_table = 'users'  # Таблица, которая будет использоваться в базе данных

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    async def send_to_users(self, bot: Bot):
        """Отправка рассылки всем пользователям через бота."""
        users = User.objects.all()
        for user in users:
            try:
                # Отправляем сообщение в чат пользователю
                await bot.send_message(user.user_id, self.content)
                print(f"Сообщение отправлено пользователю {user.user_id}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user.user_id}: {e}")
