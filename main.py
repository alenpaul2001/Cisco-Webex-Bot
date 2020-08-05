from logging import Filter
from auto_driver import (recv, timetable, toolkit, close_session, send_message, callback_handler, disconnect_handler)
from pyrogram import (Client, MessageHandler, CallbackQueryHandler,DisconnectHandler, Filters)
from creds import Info

app = Client(
    "Cisco_Auto_Driver",
    bot_token = Info.BOT_TOKEN,
    api_id = Info.API_ID,
    api_hash = Info.API_HASH,
)

app.add_handler(MessageHandler(callback=timetable, filters=Filters.command(["timetable"])))
app.add_handler(MessageHandler(callback=close_session, filters=Filters.command(["close"])))
app.add_handler(MessageHandler(callback=toolkit, filters=Filters.command(["screenshot"])))
app.add_handler(MessageHandler(callback=send_message, filters=Filters.command(["send"])))
app.add_handler(MessageHandler(callback=toolkit, filters=Filters.command(["mute"])))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(DisconnectHandler(disconnect_handler))
app.add_handler(MessageHandler(recv))
app.run()
