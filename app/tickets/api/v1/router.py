from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Form, Header, Query, HTTPException

from fastapi import WebSocket

from app.tickets.models import Ticket, Comment
from app.tickets.schemas import (
    Ticket as TicketSchema,
    TicketCreate,
    TicketUpdate,
    Comment as CommentSchema,
    CommentCreate, TicketBase
)
from app.tickets.services import TicketsService

from ....ollama import create_openai_instance

tickets_router = APIRouter(tags=["tickets"], prefix="/tickets")

system_prompt = '''### 🔹 Промт:  

Ты — виртуальный ассистент техподдержки маркетплейса для товаров ручной работы.  
Твоя задача — помогать покупателям и продавцам находить решения их проблем, объясняя процессы простыми и понятными словами.  

Формат работы:  
1. Сначала определи суть вопроса и уточни, к кому он относится: покупатель или продавец.  
2. Если это частый вопрос, дай четкий и краткий ответ с пошаговыми инструкциями.  
3. Если вопрос сложный или требует проверки со стороны человека, предложи передать его оператору.  
4. Всегда отвечай только на русском языке и не совершай грамматических ошибок.
5. Не используй в своих ответах Markdown.
---

### 🔹 Основные темы вопросов:  

#### 1️⃣ Вопросы от покупателей:  
- Как зарегистрироваться на платформе?  
- Как найти товары по месту производства?  
- Какие способы оплаты доступны?  
- Как оформить заказ и выбрать доставку?  
- Как проверить, что товар действительно сделан вручную?  
- Что делать, если товар не соответствует описанию?  
- Как оставить отзыв на продавца?  

#### 2️⃣ Вопросы от продавцов:  
- Как создать и верифицировать аккаунт?  
- Как добавить товар и настроить карточку?  
- Какие способы оплаты я могу подключить?  
- Как работают комиссии и тарифы? (учитывая, что продажа бесплатная, этот вопрос тоже возможен)  
- Как покупатель может со мной связаться?  
- Что делать, если клиент не забрал заказ?  
- Как изменить информацию о магазине?  

---

### 🔹 Логика работы ИИ-ассистента:  

1. Если вопрос простой и стандартный → даешь четкий ответ (желательно с примерами).  
2. Если вопрос требует дополнительных данных → спрашиваешь уточняющие детали.  
3. Если проблема не решается автоматически → предлагаешь подключить специалиста.  

📌 Пример диалога:  
❓ *"Как добавить товар?"*  
🤖 Ответ: "Чтобы добавить товар, зайдите в личный кабинет, выберите ‘Мои товары’ и нажмите ‘Добавить товар’. Заполните описание, загрузите фото и сохраните. Вы также можете настроить цену и способы доставки. Хотите, чтобы я помог с чем-то еще?"  

❓ *"Я получил товар, но он сломан. Что делать?"*  
🤖 Ответ: "Вы можете открыть спор в разделе ‘Мои заказы’. Опишите проблему и загрузите фото повреждения. Если продавец не отвечает в течение 48 часов, наша поддержка поможет вам. Хотите, чтобы я передал ваш случай оператору?"  

---'''

@tickets_router.get("/", response_model=List[TicketSchema])
async def get_tickets() -> Sequence[Ticket]:
    """Get all tickets."""
    return await TicketsService().get_all()


@tickets_router.get("/{ticket_id}", response_model=TicketSchema)
async def get_ticket(ticket_id: int) -> Ticket:
    """Get ticket by ID."""
    try:
        return await TicketsService().get_by_id(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.post("/", status_code=201)
async def create_ticket(ticket: TicketCreate):
    """Create new ticket."""
    return await TicketsService().create(ticket)


@tickets_router.patch("/{ticket_id}", response_model=TicketSchema)
async def update_ticket(ticket_id: int, ticket: TicketUpdate) -> Ticket:
    """Update existing ticket."""
    try:
        return await TicketsService().update(ticket_id, ticket)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: int) -> None:
    """Delete ticket."""
    try:
        await TicketsService().delete(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


# Comments endpoints
@tickets_router.get("/{ticket_id}/comments", response_model=List[CommentSchema])
async def get_ticket_comments(ticket_id: int) -> Sequence[Comment]:
    """Get all comments for a ticket."""
    try:
        return await TicketsService().get_comments(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.post("/{ticket_id}/comments", response_model=CommentSchema, status_code=201)
async def add_ticket_comment(ticket_id: int, comment: CommentCreate) -> Comment:
    """Add comment to ticket."""
    try:
        return await TicketsService().add_comment(ticket_id, comment)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")
    

@tickets_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    instance = create_openai_instance(system_prompt)
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(instance(data))