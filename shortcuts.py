from telethon.errors import ChatForwardsRestrictedError
from telethon import events
from ABH import ABH
class shortcuts:
    def __init__(self, event):
        self.event = event
        self.id = event.id
        self.chat = event.chat
        self.sender = event.sender
        self.uid = event.sender_id
        self.text = event.text or ""
        self.message = event.message
        self.chat_id = event.chat_id
        self.is_group = event.is_group
        self.input_chat = event.input_chat
        self.is_private = event.is_private
        self.raw_text = getattr(event.message, 'raw_text', "")
        self.media = event.message.media if event.message else None
        self.name = event.sender.first_name if event.sender else '.'
        self.buttons = event.message.buttons if event.message else None
        self.fwd_from = event.message.fwd_from if event.message else None
        self.entities = event.message.entities if event.message else None
        self.is_reply = bool(event.message.reply_to) if event.message else False
        self.mentions = event.message.get_entities_text() if event.message else None
        self.file = event.message.file if event.message and event.message.media else None
        self.reply_msg_id = event.message.reply_to_msg_id if event.message and event.message.reply_to else None
        self.title = event.chat.title if not event.is_private and event.chat and hasattr(event.chat, 'title') else event.sender.first_name or str(event.sender_id)
        self.link = f"https://t.me/c/{str(event.chat_id)[4:]}/{event.id}" if getattr(event, 'is_group', False) and str(event.chat_id).startswith("-100") else None
async def hint(text):
    await ABH.send_message(int(HVAR), text)
async def try_forward(event, gidvar):
    if event.message and not event.message.out and event.message.id:
        try:
            await ABH.forward_messages(
                entity=int(gidvar),
                messages=event.message.id,
                from_peer=event.chat_id
            )
            return True
        except ChatForwardsRestrictedError:
            return False
        except Exception as e:
            return False
    else:
        return False
