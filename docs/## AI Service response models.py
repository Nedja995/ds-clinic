## AI Service response models
#
class MedicinskaAnalizaModel:
    Ime_Pacijenta = "Full name of patient."
    Preporucena_Terapija_i_Savet = "Comprehensive summary including: root cause analysis, diagnosis summary, recommended therapy, lifestyle advice, and next steps."
    Kriticni_nalazi: niz[KriticanNalazModel] = "List of all critical or notable medical findings with expert opinions and raw parameter values."
    
class KriticanNalazModel:
    Expertsko_Mišljenje = "Expert opinion, diagnosis, explanation of the problem, and its cause. Highlight severity if applicable."
    Parametar_i_Vrjednost = "The specific medical parameter and its measured value (e.g., 'Glucose 7.8 mmol/L' or 'D=0.004')."

