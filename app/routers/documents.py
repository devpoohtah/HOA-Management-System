from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from typing import Optional

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.services.document_service import list_all_documents, create_document_admin
from app.schemas.document import DocumentCreate

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def documents_list(request: Request, user=Depends(require_authenticated)):
    documents = list_all_documents()
    is_admin_view = get_user_role(user) == "admin"

    return templates.TemplateResponse(
        request=request,
        name="documents/list.html",
        context={
            "documents": documents,
            "is_admin_view": is_admin_view,
            "base_template": "admin_base.html" if is_admin_view else "homeowner_base.html",
        },
    )


@router.get("/upload")
def upload_document_form(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        request=request,
        name="documents/upload.html",
        context={"error": None},
    )


@router.post("/upload")
def upload_document_submit(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    file_url: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    data = DocumentCreate(title=title, category=category, file_url=file_url).model_dump()
    uploaded_by = getattr(user, "id", "unknown")
    create_document_admin(data, uploaded_by=uploaded_by)

    return RedirectResponse(url="/documents", status_code=303)