import anthropic
from core.config import settings


client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


async def generate_tasks(project_idea: str) -> list[str]:
    """
    Loyiha g'oyasi asosida AI yordamida vazifalar generatsiya qiladi.
    """
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Menga '{project_idea}' loyihasi uchun "
                    f"10 ta aniq va qisqa vazifalar ro'yxatini ber.\n\n"
                    f"Qoidalar:\n"
                    f"- Har bir vazifa yangi qatorda bo'lsin\n"
                    f"- Faqat vazifa nomini yoz, izoh yozma\n"
                    f"- Raqam yoki belgi qo'yma\n"
                    f"- O'zbek tilida yoz"
                ),
            }
        ],
    )

    # Javobni satrlar ro'yxatiga ajratamiz
    raw = message.content[0].text
    tasks = [
        line.strip()
        for line in raw.strip().splitlines()
        if line.strip()
    ]
    return tasks[:10]


async def summarize_project(
    project_name: str,
    tasks: list[str],
) -> str:
    """
    Loyiha va vazifalar asosida qisqa xulosa yaratadi.
    """
    tasks_text = "\n".join(f"- {t}" for t in tasks)

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"'{project_name}' loyihasi uchun quyidagi vazifalar bor:\n"
                    f"{tasks_text}\n\n"
                    f"Shu loyiha haqida 3-4 jumladan iborat qisqa xulosa yoz. "
                    f"O'zbek tilida yoz."
                ),
            }
        ],
    )

    return message.content[0].text.strip()