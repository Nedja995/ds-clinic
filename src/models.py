from pydantic import BaseModel, Field


class MedicalCriticalFindingModel(BaseModel):
    expertsko_misljenje: str = Field(description="Experts though, diagnosis, explanation of the problem, and its cause.", default="")
    parametar_and_value: str = Field(description="Parameter and its value.", default="")

class MedicalReportModel(BaseModel):
    patient_name: str = Field(description="Full name of the patient.", default="")
    report_date: str = Field(description="Datum izvještaja.", default="")
    recommended_therapy_and_advice: str = Field(description="rezime, uzrok problema sazeto, uzrok problema detaljno, strucno misljenje dijagnoza summarized i preporucena terapija i savet summarized.", default="")
    critical_findings: list[MedicalCriticalFindingModel] = Field(description="Lista kritičnih nalaza sa ekspertskim mišljenjem i referentnim parametrima/vrednostima.", default=[])



# ---- MODELI ZA KREIRANJE KRAJNJEG PDF-a ----
class ReportItem(BaseModel):
    misljenje: str = "NEPOZNATO"
    parametar: str = "NEPOZNATO"
    
class Report(BaseModel):
    patient_name: str = "NEPOZNATO"
    report_date: str = "NEPOZNATO"
    terapija_i_saveti: str = "NEPOZNATO"
    nalazi: list[ReportItem] = []

# 1. DEFINE YOUR DESIRED OUTPUT STRUCTURE
class MedicalReport(BaseModel):
    patient_summary: str = Field(description="A brief summary of the patient's health status.")
    severe_abnormalities: list[str] = Field(description="List of critical issues that need immediate attention.")
    recommended_followups: list[str] = Field(description="Suggested next steps or lifestyle changes.")


# ---- MODELI ZA GEMINI STRUCTURED OUTPUT (POKLAPAJU SE SA PROMPTOM) ----
class GeminiNalaz(BaseModel):
    misljenje_i_dijagnoza: str = Field(description="Stručno mišljenje i dijagnoza")
    parametar: str = Field(description="Naziv parametra iz nalaza")
    vrednost: str = Field(description="Vrednost parametra (npr. D=0.004 ili 1.79)")
    status: str = Field(description="Status (npr. Povišeno, Kritično, Alarmantno)")
    znacaj: str = Field(description="Značaj ovog parametra za zdravlje")
    parametar_i_vrednost: str = Field(description="Spojen naziv parametra i vrednost")
    dijagnoza: str = Field(description="Moguća dijagnoza na osnovu nalaza")
    gde_je_problem: str = Field(description="Koji organ ili sistem je problematičan")
    rezime: str = Field(description="Kratak rezime ovog nalaza")
    uzrok_problema: str = Field(description="Kratak uzrok")
    uzrok_problema_detaljno: str = Field(description="Detaljan uzrok za ovaj specifičan nalaz")
    uzrok_problema_summarized: str = Field(description="Sažet uzrok")

class AnalysisReport(BaseModel):
    ime_pacijenta: str = Field(description="Ime i prezime pacijenta iz priloženih dokumenata")
    trenutni_datum: str = Field(description="Datum sa najnovijeg priloženog nalaza")
    dijagnoza_bolesti: str = Field(description="Opšta dijagnoza iz svih nalaza")
    dijagnoza_summarized: str = Field(description="Sažeta dijagnoza za zaglavlje")
    dijagnoza: str = Field(description="Glavna dijagnoza")
    strucno_misljenje_dijagnoza_summarized: str = Field(description="Sažeto stručno mišljenje za sve nalaze")
    preporucena_terapija_i_savet_summarized: str = Field(description="Preporučeni dalji koraci i terapija")
    gde_je_problem: str = Field(description="Generalni sistemi u organizmu gde je problem (npr. Urinarni trakt, Kardiovaskularni sistem)")
    rezime: str = Field(description="Opšti rezime slučaja pacijenta")
    uzrok_problema: str = Field(description="Generalni uzrok problema")
    uzrok_problema_detaljno: str = Field(description="Detaljno opisan uzrok kompleksnog stanja pacijenta")
    uzrok_problema_summarized: str = Field(description="Sažet uzrok problema za brzi pregled")
    problem_defined: str = Field(description="Kratko i jasno definisan glavni klinički problem u jednoj rečenici")
    nalazi: list[GeminiNalaz] = Field(description="Lista svih kritičnih i bitnih pojedinačnih nalaza iz dokumenata")
