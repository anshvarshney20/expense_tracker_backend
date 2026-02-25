
from fastapi import APIRouter
from app.schemas.marketing import ContactCreate, NewsletterSubscribe
from app.schemas.responses import SuccessResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/contact", response_model=SuccessResponse[None])
async def contact_form(contact_in: ContactCreate):
    # In a real app, you'd save to DB or send email
    logger.info(f"Contact form received: {contact_in.email} - {contact_in.interest}")
    print(f"DEBUG: Contact from {contact_in.name} ({contact_in.email}) regarding {contact_in.interest}")
    return SuccessResponse(message="Transmission received and archived.")

@router.post("/newsletter", response_model=SuccessResponse[None])
async def newsletter_subscribe(sub_in: NewsletterSubscribe):
    logger.info(f"Newsletter subscription: {sub_in.email}")
    print(f"DEBUG: Newsletter subscription for {sub_in.email}")
    return SuccessResponse(message="Sovereign pulse initialized.")
