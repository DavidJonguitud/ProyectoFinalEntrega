from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        project_id: int,
        uploaded_by: str,
        file_name: str,
        file_type: DocumentType,
        path: str,
    ) -> Document:
        document = Document(
            project_id=project_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_type=file_type,
            path=path,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update_document(self, document: Document, update_data: dict) -> Document:
        for key, value in update_data.items():
            setattr(document, key, value)

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document_by_id(self, id: int) -> Document | None:
        return self.db.query(Document).filter(Document.id == id).first()

    def get_documents_by_project_id(self, id: int) -> list[Document]:
        return self.db.query(Document).filter(Document.project_id == id).all()

    def delete_document(self, document: Document):
        self.db.delete(document)
        self.db.commit()
