from django.contrib import admin
from .models import User, Newsletter
from aiogram import Bot
from django.conf import settings
import logging
import asyncio

# Настроим логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    actions = ['send_newsletter_to_all_users']

    def send_newsletter_to_all_users(self, request, queryset):
        # Используем контекстный менеджер для aiohttp
        try:
            # Получаем объект рассылки (выбираем первую, если их несколько)
            newsletter = queryset.first()  # Выбираем первую выбранную рассылку
            if not newsletter:
                self.message_user(request, "Не выбрана рассылка.")
                return

            # Текст сообщения из Content модели рассылки
            message = newsletter.content  # Поле Content из модели Newsletter

            # Получаем всех пользователей из базы данных
            users = User.objects.all()
            logger.info(f"Начинаем рассылку для {len(users)} пользователей.")

            # Запускаем асинхронные отправки сообщений в правильном цикле событий
            asyncio.run(self.send_newsletter(users, message))

            logger.info(f"Сообщение успешно отправлено всем пользователям.")
            self.message_user(request, f"Сообщение успешно отправлено всем пользователям.")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщений: {e}")
            self.message_user(request, f"Ошибка при отправке сообщений: {e}")

    async def send_newsletter(self, users, message):
        # Используем контекстный менеджер для создания и закрытия сессии
        bot = Bot(token=settings.BOT_TOKEN)
        async with bot.session:
            # Асинхронная функция для отправки сообщения всем пользователям
            for user in users:
                await self.send_message(bot, user.user_id, message)

    async def send_message(self, bot, user_id, message):
        # Асинхронная функция для отправки одного сообщения
        await bot.send_message(user_id, message)

    send_newsletter_to_all_users.short_description = 'Отправить сообщение всем пользователям'

admin.site.register(User)
admin.site.register(Newsletter, NewsletterAdmin)
