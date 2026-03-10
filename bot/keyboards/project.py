from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models.project import Project


def get_projects_keyboard(projects: list[Project]) -> InlineKeyboardMarkup:
    buttons = []
    for project in projects:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {project.name}",
                callback_data=f"project:{project.id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="➕ Yangi loyiha",
            callback_data="project:create"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_project_detail_keyboard(project_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Vazifalar",
                    callback_data=f"project_tasks:{project_id}"
                ),
                InlineKeyboardButton(
                    text="👥 A'zolar",
                    callback_data=f"project_members:{project_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"project_delete:{project_id}"
                ),
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="project:list"
                ),
            ],
        ]
    )


def get_confirm_delete_keyboard(project_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, o'chir",
                    callback_data=f"project_delete_confirm:{project_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Yo'q",
                    callback_data=f"project:{project_id}"
                ),
            ]
        ]
    )