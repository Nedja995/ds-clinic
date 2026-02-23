from pydantic import BaseModel


class ReportItem(BaseModel):
    misljenje: str
    parametar: str
    
class Report(BaseModel):
    patient_name: str
    report_date: str
    terapija_i_saveti: str
    nalazi: list[ReportItem]


