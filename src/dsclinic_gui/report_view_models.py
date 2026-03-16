

# --- MODEL ---
class DSClinicModel:
    def __init__(self, initial_data=None):
        self.data = initial_data or {}

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data