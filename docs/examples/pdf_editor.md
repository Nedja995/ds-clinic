


Creating a completely functional "PDF Editor" (like Adobe Acrobat, where you can click and type over existing text) is incredibly complex due to how PDFs are structured. However, we can build a very robust **simple PDF editor** that allows you to:

1. **Open and View** PDF pages.
2. **Navigate** through pages.
3. **Rotate** pages.
4. **Extract Text** from pages.
5. **Save** the modified PDF as a new file.

For this, we will use Python's built-in **Tkinter** for the GUI, **PyMuPDF** (`fitz`) for extremely fast PDF rendering and manipulation, and **Pillow** (`PIL`) to display the images in Tkinter.

### Prerequisites
Before running the code, you need to install the required external libraries. Open your terminal and run:
```bash
pip install pymupdf pillow
```

### Python 3.14 Code

Save the following code as `pdf_editor.py` and run it. 

```python
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class SimplePDFEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simple Python PDF Editor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # State variables
        self.doc: fitz.Document | None = None
        self.current_page_idx: int = 0
        self.current_image: ImageTk.PhotoImage | None = None

        self._build_ui()

    def _build_ui(self):
        # Toolbar Frame
        toolbar = ttk.Frame(self.root, padding=5, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Buttons
        ttk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text="Previous Page", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Next Page", command=self.next_page).pack(side=tk.LEFT, padx=2)
        
        self.page_label_var = tk.StringVar(value="Page: 0 / 0")
        ttk.Label(toolbar, textvariable=self.page_label_var).pack(side=tk.LEFT, padx=10)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Rotate 90°", command=self.rotate_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Extract Text", command=self.extract_text).pack(side=tk.LEFT, padx=2)

        # Main Content PanedWindow (Split screen)
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left Side: PDF Viewer
        self.canvas_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.canvas_frame, weight=3)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right Side: Text Extractor
        self.text_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.text_frame, weight=1)

        ttk.Label(self.text_frame, text="Extracted Text:").pack(anchor=tk.W)
        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD, width=40)
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def open_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Select a PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return

        try:
            self.doc = fitz.open(filepath)
            self.current_page_idx = 0
            self.update_view()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{e}")

    def save_pdf(self):
        if not self.doc:
            messagebox.showwarning("Warning", "No PDF opened to save.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return

        try:
            self.doc.save(filepath)
            messagebox.showinfo("Success", "PDF saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF:\n{e}")

    def update_view(self):
        if not self.doc or self.current_page_idx >= len(self.doc):
            return

        # Update page label
        total_pages = len(self.doc)
        self.page_label_var.set(f"Page: {self.current_page_idx + 1} / {total_pages}")

        # Get the current page
        page = self.doc[self.current_page_idx]

        # Convert page to an image (Pixmap)
        # Matrix(1.5, 1.5) scales the resolution up slightly for better readability
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)

        # Convert PyMuPDF Pixmap to PIL Image
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode,[pix.width, pix.height], pix.samples)

        # Convert PIL Image to Tkinter PhotoImage
        self.current_image = ImageTk.PhotoImage(img)

        # Clear canvas and draw new image
        self.canvas.delete("all")
        
        # Center the image on the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x_pos = max((canvas_width - pix.width) // 2, 0)
        y_pos = max((canvas_height - pix.height) // 2, 0)
        
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.current_image)
        
        # Update canvas scroll region
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))

    def next_page(self):
        if self.doc and self.current_page_idx < len(self.doc) - 1:
            self.current_page_idx += 1
            self.update_view()

    def prev_page(self):
        if self.doc and self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.update_view()

    def rotate_page(self):
        if self.doc:
            page = self.doc[self.current_page_idx]
            # Rotate 90 degrees clockwise
            current_rotation = page.rotation
            page.set_rotation(current_rotation + 90)
            self.update_view()

    def extract_text(self):
        if self.doc:
            page = self.doc[self.current_page_idx]
            text = page.get_text()
            
            # Clear existing text and insert new
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, text)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Update canvas size dynamically on window resize
    app = SimplePDFEditor(root)
    root.bind("<Configure>", lambda e: app.update_view() if e.widget == root else None)
    
    root.mainloop()
```

### How this works:
1. **PyMuPDF (`fitz`)**: This handles the heavy lifting of the PDF. When you open the PDF, it creates a document object. 
2. **`update_view` Method**: It pulls the current page, creates a visual "Pixmap" (an image representation of the PDF page), scales it up slightly for better resolution via a Matrix, and maps it to a Pillow `Image`.
3. **Tkinter Canvas**: We paint the Pillow `Image` directly onto the Tkinter canvas. It supports centering the document dynamically if you resize the window.
4. **Editing (Rotation & Text Extraction)**:
    * When you click **Rotate**, it edits the internal PDF rotation metadata of that specific page by adding 90 degrees, and updates the view.
    * When you click **Extract Text**, PyMuPDF grabs the raw text strings out of the current page and drops them into the standard Tkinter `Text` box on the right.
5. **Saving**: Calling `.save()` commits any changes (like the rotations) and writes out a brand new PDF. 

### Ways to expand this in the future:
* **Delete Pages**: You can easily add a button that calls `self.doc.delete_page(self.current_page_idx)`.
* **Merge PDFs**: You can create an insert button that calls `self.doc.insert_pdf(other_doc)`.