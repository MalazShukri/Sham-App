# sham_sy/notifications.py (adjust path to your app name)

import requests
from django.conf import settings
from django.utils import timezone


def send_telegram_message(text: str):
    """
    Low-level helper to send a Telegram message.
    Uses TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from settings.py
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    # If not configured, just do nothing (don't break the API)
    if not token or not chat_id:
        print("[Telegram] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in settings.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",  # allow bold, etc.
    }

    try:
        requests.post(url, data=data, timeout=5)
    except requests.RequestException as e:
        # Don't break the main request if Telegram fails
        print(f"[Telegram] Failed to send message: {e}")


def format_service_request_message(service_request) -> str:
    """
    Build a nice, readable Telegram message for a ServiceRequest instance.
    """
    services = service_request.services.all()
    # Prefer Arabic title if available
    service_titles = ", ".join(
        [s.title_ar or s.title for s in services]
    ) or "بدون خدمات"

    details = service_request.details or "لا يوجد"
    created_str = timezone.localtime(
        service_request.created_at).strftime("%Y-%m-%d %H:%M")

    text = (
        "📥 <b>طلب خدمة جديد</b>\n\n"
        f"👤 الاسم: {service_request.user.full_name}\n"
        f"📞 الهاتف: {service_request.phone_number}\n"
        f"🧾 الخدمات: {service_titles}\n"
        f"📅 اليوم المطلوب: {service_request.service_day}\n"
        f"📍 العنوان: {service_request.address}\n"
        f"📌 تفاصيل إضافية: {details}\n"
        f"⏰ تم الإنشاء في: {created_str}"
    )
    return text


def send_new_service_request_notification(service_request):
    """
    Public function to be called from the view
    whenever a ServiceRequest is created.
    """
    text = format_service_request_message(service_request)
    send_telegram_message(text)
