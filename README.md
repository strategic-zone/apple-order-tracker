# Apple Order Tracker Bot

![Bot Demo](assets/bot_demo.png)

Telegram bot to track Apple store order status. Get notifications when your order status changes.

## Features
- Real-time order status monitoring
- Automatic notifications on status changes
- Progress visualization with emojis
- Restricted access (single user)

## Usage
1. Create bot with [@BotFather](https://t.me/botfather)
2. Get your Telegram ID from [@userinfobot](https://t.me/userinfobot)
3. Set environment variables:
```env
ALLOWED_USER_ID=your_telegram_id
TOKEN=your_bot_token
ORDER_STATUS_URL=your_apple_order_url
```

## Docker Deployment
```bash
git clone https://github.com/yourusername/apple-order-tracker
cd apple-order-tracker
docker compose up -d
```

## Commands
- `/start` - Start tracking
- Button `Check Order Status` - Manual status check

## Status Types
- 📝 Placed
- ⚙️ Processing
- 🚚 Shipping To Store
- 📦 Ready For Pickup
- ✅ Picked Up

Status check interval: 15 minutes

## Requirements
- Docker & Docker Compose
- Python 3.11+
- Telegram Bot Token
- Apple Order Status URL