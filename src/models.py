from pydantic import BaseModel


class ReportItem(BaseModel):
    misljenje: str
    parametar: str
