from pydantic import BaseModel


class ReportItem(BaseModel):
    misljenje: str = "NEPOZNATO"
    parametar: str = "NEPOZNATO"
    
class Report(BaseModel):
    patient_name: str = "NEPOZNATO"
    report_date: str = "NEPOZNATO"
    terapija_i_saveti: str = "NEPOZNATO"
    nalazi: list[ReportItem] = []


