import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
from pathlib import Path

# Add src to path if running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
import api_gemini.client as api_gemini_client
from api_gemini.client import MedicalAnalyzerClient
import pdf_maker

class DSClinicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DS Clinic Medical Analyzer")
        self.root.geometry("900x700")
        
        try:
            client_config = api_gemini_client.GeminiConfig(api_key=config.GOOGLE_API_KEY)
            self.ai_client = MedicalAnalyzerClient(config=client_config)
        except ValueError as e:
            messagebox.showwarning("API Key Missing", str(e) + "\nPlease set it before analyzing.")
            self.ai_client = None

        self._build_ui()

    def _build_ui(self):
        # --- TOP: Input Documents ---
        tk.Label(self.root, text="Input Documents (Medical records, labs, etc.):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.txt_input = scrolledtext.ScrolledText(self.root, height=10, wrap=tk.WORD)
        self.txt_input.pack(fill="both", expand=True, padx=10, pady=5)

        # --- MIDDLE: Predefined Question & Action ---
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(mid_frame, text="Predefined Question:").pack(side="left")
        self.entry_question = tk.Entry(mid_frame, width=60)
        self.entry_question.insert(0, "Analyze these documents, summarize health status, and highlight abnormalities.")
        self.entry_question.pack(side="left", padx=5)
        
        self.btn_analyze = ttk.Button(mid_frame, text="Analyze Documents", command=self.run_initial_analysis)
        self.btn_analyze.pack(side="left", padx=5)

        # --- BOTTOM: Gemini Response & Editor ---
        tk.Label(self.root, text="Analysis Report (Review and Edit):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.txt_output = scrolledtext.ScrolledText(self.root, height=15, wrap=tk.WORD)
        self.txt_output.pack(fill="both", expand=True, padx=10, pady=5)

        # --- FOOTER: Follow-up & Export ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(bottom_frame, text="Ask Google AI (Follow-up):").pack(side="left")
        self.entry_followup = tk.Entry(bottom_frame, width=40)
        self.entry_followup.pack(side="left", padx=5)
        
        self.btn_followup = ttk.Button(bottom_frame, text="Send", command=self.run_followup)
        self.btn_followup.pack(side="left", padx=5)

        self.btn_export = ttk.Button(bottom_frame, text="Export Final Report to PDF", command=self.export_pdf)
        self.btn_export.pack(side="right")

    def run_thread(self, target, button):
        if not self.ai_client:
            messagebox.showerror("Error", "Gemini API client not initialized.")
            return
        button.config(state="disabled")
        threading.Thread(target=target, args=(button,), daemon=True).start()

    def run_initial_analysis(self):
        docs = self.txt_input.get("1.0", tk.END).strip()
        question = self.entry_question.get().strip()
        
        if not docs: return messagebox.showwarning("Warning", "Input documents are empty.")

        def task(btn):
            try:
                result = self.ai_client.analyze_initial(docs, question)
                # Update UI in main thread
                self.root.after(0, lambda: self._update_output(result, clear=True))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("API Error", str(e)))
            finally:
                self.root.after(0, lambda: btn.config(state="normal"))
                
        self.run_thread(task, self.btn_analyze)

    def run_followup(self):
        question = self.entry_followup.get().strip()
        if not question: return

        def task(btn):
            try:
                result = self.ai_client.ask_followup(question)
                append_text = f"\n\n--- Follow-up: {question} ---\n{result}"
                self.root.after(0, lambda: self._update_output(append_text, clear=False))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("API Error", str(e)))
            finally:
                self.root.after(0, lambda: btn.config(state="normal"))
                self.root.after(0, lambda: self.entry_followup.delete(0, tk.END))

        self.run_thread(task, self.btn_followup)

    def _update_output(self, text, clear=False):
        if clear:
            self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, text)

    def export_pdf(self):
        final_text = self.txt_output.get("1.0", tk.END).strip()
        if not final_text:
            return messagebox.showwarning("Warning", "No report content to export.")
            
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            try:
                pdf_maker.export_to_pdf(final_text, filepath)
                messagebox.showinfo("Success", f"Report saved successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

def main():
    root = tk.Tk()
    app = DSClinicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()