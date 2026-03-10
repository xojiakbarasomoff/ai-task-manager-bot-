from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models.task import Task


def get_tasks_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    buttons = []
    for task in tasks:
        status_icon = {
            "TODO": "🔵",
            "IN_PROGRESS": "🟡",
            "DONE": "🟢",
        }.get(task.status, "🔵")

        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {task.title}",
                callback_data=f"task:{task.id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="➕ Yangi vazifa",
            callback_data="task:create"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔵 TODO",
                    callback_data=f"task_status:{task_id}:TODO"
                ),
                InlineKeyboardButton(
                    text="🟡 IN PROGRESS",
                    callback_data=f"task_status:{task_id}:IN_PROGRESS"
                ),
                InlineKeyboardButton(
                    text="🟢 DONE",
                    callback_data=f"task_status:{task_id}:DONE"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"task_delete:{task_id}"
                ),
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="task:list"
                ),
            ],
        ]
    )


def get_priority_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔴 HIGH",
                    callback_data="priority:HIGH"
                ),
                InlineKeyboardButton(
                    text="🟡 MEDIUM",
                    callback_data="priority:MEDIUM"
                ),
                InlineKeyboardButton(
                    text="🟢 LOW",
                    callback_data="priority:LOW"
                ),
            ]
        ]
    )