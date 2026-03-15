###############################################################################
#  USED-CAR MARKETPLACE DASHBOARD 
#
#
###############################################################################
import tkinter as tk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import numpy as np
import re, sys
import re, sys
from pathlib import Path
from textwrap import shorten
import utils

# ─────────────────────────  CONFIG  ──────────────────────────
CSV_PATH = utils.get_resource_filepath("sampledata_cars.csv")       
COLUMN_ALIASES = {
    "brand": "make", "manufacturer": "make", "carname": "model",
    "rating": "consumerrating", "safety": "reliabilityrating",
}
REQUIRED = {"make", "price"}                            
# ──────────────────────────────────────────────────────────────

class Dashboard:
    # ═══════════════════════════════════════════════════════════
    def __init__(self, root: tb.Window):
        self.root = root
        self.style = tb.Style("cosmo")
        self._make_spinbox_style()
        self.clr = self.style.colors
        
        self.current_analysis_plot_func = None 
        
        self._load_data()
        self._build_gui()
        self._apply_filters()

    # ─────────── spin-box style (white arrows) ────────────────
    def _make_spinbox_style(self):
        try:
            self.style.configure("White.TSpinbox",
                                 arrowcolor="white",
                                 arrowsize=12)
            self.style.map("White.TSpinbox",
                           arrowcolor=[("disabled", "white"),
                                       ("active",   "white"),
                                       ("pressed",  "white")])
        except tk.TclError:
            pass

    # ───────────────────── DATA LOAD ───────────────────────────
    def _load_data(self):
        csv = Path(CSV_PATH)
        if not csv.exists():
            tb.dialogs.Messagebox.show_error("CSV not found", str(csv))
            sys.exit()

        df = pd.read_csv(csv, encoding="utf-8-sig", skipinitialspace=True)
        df.columns = [
            COLUMN_ALIASES.get(
                re.sub(r"[^0-9a-z]", "", c.lower().replace("\ufeff", "")),
                c.lower()
            )
            for c in df.columns
        ]
        if "year" not in df.columns:
            for col in df.columns:
                nums = pd.to_numeric(df[col], errors="coerce")
                if nums.dropna().between(1900, 2035).all():
                    df.rename(columns={col: "year"}, inplace=True)
                    break
        for col in ("price", "minmpg", "maxmpg",
                    "year", "mileage", "consumerrating"):
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str)
                          .str.replace(r"[^\d.]", "", regex=True),
                    errors="coerce"
                )
        if any(c not in df.columns for c in REQUIRED):
            tb.dialogs.Messagebox.show_error(
                "Bad CSV", "Missing required columns.")
            sys.exit()
        self.df = df.dropna(subset=["make", "price"])

    # ───────────────────── GUI BUILD ───────────────────────────
    def _build_gui(self):
        header = tb.Frame(self.root, width=600, height=60, bootstyle="light")
        header.pack_propagate(False)
        header.pack(side="top", anchor="w", padx=8, pady=(4, 2))
        tb.Label(header, text="🚗  USED-CAR DASHBOARD",
                 font=("Segoe UI", 16, "bold"), anchor="w")\
          .pack(fill="both", padx=8, pady=4)

        self.nb = tb.Notebook(self.root); self.nb.pack(fill="both", expand=True)
        self._overview_tab()
        self._analysis_tab()
        self._data_tab()

    # ─────────────────  OVERVIEW TAB  ─────────────────────────
    def _overview_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Overview")
        self._filters(tab)
        self._cards(tab)
        self._overview_fig(tab)

    def _spin(self, parent, **kw):
        return tb.Spinbox(parent, style="White.TSpinbox", **kw)

    def _filters(self, parent):
        f = tb.Labelframe(parent, text="Filters", padding=6)
        f.pack(fill="x", padx=8, pady=6)
        tk.Label(f, text="Make").grid(row=0, column=0, sticky="w", padx=4)
        self.make = tk.StringVar(value="All")
        tb.Combobox(f, textvariable=self.make, state="readonly", width=14,
                    values=["All"] + sorted(self.df["make"].unique()),
                    bootstyle="light")\
          .grid(row=0, column=1)
        self.make.trace_add("write", self._apply_filters)
        if "drivetrain" in self.df.columns:
            tk.Label(f, text="Drivetrain").grid(row=0, column=2, padx=(20, 4))
            self.drive = tk.StringVar(value="All")
            tb.Combobox(f, textvariable=self.drive, state="readonly", width=14,
                        values=["All"] + sorted(self.df["drivetrain"].dropna()
                                                .unique()),
                        bootstyle="light")\
              .grid(row=0, column=3)
            self.drive.trace_add("write", self._apply_filters)
        pr_min, pr_max = self.df["price"].min(), self.df["price"].max()
        tk.Label(f, text="Price $").grid(row=0, column=4, padx=(20, 4))
        self.pmin = tk.DoubleVar(value=float(pr_min))
        self.pmax = tk.DoubleVar(value=float(pr_max))
        for col, var in [(5, self.pmin), (6, self.pmax)]:
            self._spin(f, from_=0, to=float(pr_max), textvariable=var,
                       width=10, increment=1000, bootstyle="secondary")\
              .grid(row=0, column=col)
        if "year" in self.df.columns:
            try:
                yr_min, yr_max = int(self.df["year"].min()), int(self.df["year"].max())
            except (ValueError, TypeError):
                yr_min, yr_max = 1900, 2035
            tk.Label(f, text="Year").grid(row=0, column=7, padx=(20, 4))
            self.ymin = tk.IntVar(value=yr_min)
            self.ymax = tk.IntVar(value=yr_max)
            for col, var in [(8, self.ymin), (9, self.ymax)]:
                self._spin(f, from_=1900, to=2035, textvariable=var,
                           width=6, bootstyle="secondary")\
                  .grid(row=0, column=col)
        tb.Button(f, text="Apply Year/Price Filters",
                  bootstyle="primary-outline",
                  command=self._apply_filters)\
          .grid(row=0, column=10, padx=(30, 4))

    def _cards(self, parent):
        wrap = tb.Frame(parent); wrap.pack(fill="x", padx=8)
        self.cards = {}
        for lbl in ("Total Cars", "Average Price",
                    "Average Mileage", "Avg Rating"):
            card = tb.Frame(wrap, padding=6, relief="ridge", bootstyle="light")
            card.pack(side="left", fill="x", expand=True, padx=4, pady=4)
            val = tb.Label(card, text="-", font=("Segoe UI", 16, "bold"),
                           foreground=self.clr.info)
            val.pack()
            tb.Label(card, text=lbl, foreground="white").pack()
            self.cards[lbl] = val

    def _overview_fig(self, parent):
        fr = tb.Frame(parent); fr.pack(fill="both", expand=True, padx=8, pady=6)
        self.ov_fig = plt.Figure(figsize=(18, 10), facecolor="white",
                                 constrained_layout=True)
        self.ov_canvas = FigureCanvasTkAgg(self.ov_fig, master=fr)
        self.ov_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ───────────────── ANALYSIS TAB ──────────────────────────
    def _analysis_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Analysis")
        ctl = tb.Frame(tab); ctl.pack(fill="x", padx=8, pady=6)
        def set_and_run_analysis(plot_function):
            self.current_analysis_plot_func = plot_function
            plot_function()
        for txt, fn in (("Correlation", self._corr),
                        ("Price by Make", self._price_make),
                        ("MPG", self._mpg),
                        ("Ratings", self._ratings)):
            tb.Button(ctl, text=txt, command=lambda f=fn: set_and_run_analysis(f),
                      bootstyle="info-outline").pack(side="left", padx=4)
        self.an_fig = plt.Figure(figsize=(12, 7), facecolor="white",
                                 constrained_layout=True)
        self.an_canvas = FigureCanvasTkAgg(self.an_fig, master=tab)
        w = self.an_canvas.get_tk_widget()
        w.configure(width=1200, height=700)
        w.pack(padx=8, pady=4)

    # ───────────────── DATA TAB ────────────────────────────────
    def _data_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Data")
        top = tb.Frame(tab); top.pack(fill="x", padx=8, pady=6)
        tk.Label(top, text="Search").pack(side="left")
        self.search = tk.StringVar()
        tk.Entry(top, textvariable=self.search, width=25)\
          .pack(side="left", padx=4)
        self.search.trace_add("write", self._search_tree)
        cols = list(self.df.columns)
        self.tree = tb.Treeview(tab, columns=cols, show="headings",
                                bootstyle="light")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=120, anchor="w")
        ysb = tb.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        xsb = tb.Scrollbar(tab, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y"); xsb.pack(side="bottom", fill="x")

    # ───────────────── FILTER & STATS ──────────────────────────
    def _apply_filters(self, *_):
        df = self.df.copy()
        if self.make.get() != "All":
            df = df[df["make"] == self.make.get()]
        if hasattr(self, "drive") and self.drive.get() != "All":
            df = df[df["drivetrain"] == self.drive.get()]
        try:
            pmin, pmax = float(self.pmin.get()), float(self.pmax.get())
        except ValueError:
            pmin, pmax = df["price"].min(), df["price"].max()
        df = df[(df["price"] >= pmin) & (df["price"] <= pmax)]
        if "year" in df.columns and hasattr(self, "ymin"):
            try:
                ymin, ymax = int(self.ymin.get()), int(self.ymax.get())
            except ValueError:
                ymin, ymax = df["year"].min(), df["year"].max()
            df = df[(df["year"] >= ymin) & (df["year"] <= ymax)]
        self.filtered = df
        self._update_cards()
        self._draw_overview()
        self._fill_tree()
        if self.current_analysis_plot_func:
            self.current_analysis_plot_func()

    def _update_cards(self):
        d = self.filtered
        self.cards["Total Cars"].configure(text=f"{len(d):,}")
        self.cards["Average Price"].configure(
            text=f"${d['price'].mean():,.0f}" if not d.empty else "$0")
        m = d["mileage"].mean() if "mileage" in d.columns else np.nan
        self.cards["Average Mileage"].configure(
            text=f"{m:,.0f} mi" if not np.isnan(m) else "-")
        r = d["consumerrating"].mean() if "consumerrating" in d.columns else np.nan
        self.cards["Avg Rating"].configure(
            text=f"{r:.2f}" if not np.isnan(r) else "-")

    # ───────────────── OVERVIEW PLOTS (clickable) ──────────────
    def _draw_overview(self):
        if hasattr(self, "_ov_pick_id"):
            self.ov_fig.canvas.mpl_disconnect(self._ov_pick_id)
        
        self.ov_fig.clear()
        self._ov_annot = None 

        df = self.filtered
        if df.empty:
            ax = self.ov_fig.add_subplot(111)
            ax.axis("off")
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color="black", fontsize=16)
            self.ov_canvas.draw(); return

        gs = self.ov_fig.add_gridspec(2, 2)
        
        ax_hist = self.ov_fig.add_subplot(gs[0, 0])
        ax_scatter = self.ov_fig.add_subplot(gs[0, 1])
        ax_pie = self.ov_fig.add_subplot(gs[1, 0])
        ax_bar = self.ov_fig.add_subplot(gs[1, 1])
        
        ax_hist.hist(df["price"], bins=30, color=self.clr.info)
        ax_hist.set_title("Price Distribution", color="black")
        ax_hist.set_xlabel("Price ($)", color="black"); ax_hist.set_ylabel("Cars", color="black")
        ax_hist.tick_params(colors="black")

        df_scatter_data = df.dropna(subset=["mileage", "price"])
        self._ov_scatter_map = {}
        if not df_scatter_data.empty:
            sc = ax_scatter.scatter(df_scatter_data["mileage"], df_scatter_data["price"],
                                    s=45, alpha=0.8, c=df_scatter_data["year"], cmap="viridis")
            sc.set_picker(True); sc.set_pickradius(10)
            self._ov_scatter_map[sc] = df_scatter_data.reset_index(drop=True)
            cb = self.ov_fig.colorbar(sc, ax=ax_scatter)
            cb.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            cb.ax.tick_params(colors="black"); cb.set_label("Year", color="black")

            def _on_pick(event):
                if len(event.ind) == 0:
                    return
                row = self._ov_scatter_map[event.artist].iloc[event.ind[0]]
                label = shorten(f"{row['make']} {row.get('model','')}", width=40, placeholder="…")
                if self._ov_annot:
                    self._ov_annot.remove()
                self._ov_annot = ax_scatter.annotate(
                    label, (row["mileage"], row["price"]),
                    xytext=(10, 10), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="white", alpha=0.9), color="black")
                self.ov_canvas.draw_idle()
            self._ov_pick_id = self.ov_fig.canvas.mpl_connect("pick_event", _on_pick)

        ax_scatter.set_title("Mileage vs Price", color="black")
        ax_scatter.set_xlabel("Mileage", color="black"); ax_scatter.set_ylabel("Price ($)", color="black")
        ax_scatter.tick_params(colors="black")

        if "drivetrain" in df.columns:
            cnt = df["drivetrain"].value_counts()
            if not cnt.empty:
                ax_pie.pie(cnt, labels=cnt.index, autopct="%1.0f%%", textprops={'color': 'black'})
            ax_pie.set_title("Cars by Drivetrain", color="black")

        if not df.empty:
            top = df.groupby("make")["price"].mean().nlargest(10).sort_values()
            if not top.empty:
                top.plot(kind="barh", ax=ax_bar, color=self.clr.primary)
        ax_bar.set_title("Top-10 Makes by Avg Price", color="black")
        ax_bar.set_xlabel("Average Price ($)", color="black"); ax_bar.set_ylabel("Make", color="black")
        ax_bar.tick_params(colors="black")

        self.ov_canvas.draw()

    # ───────────────── ANALYSIS PLOTS ──────────────────────────
    def _corr(self):
        self.an_fig.clear()
        ax = self.an_fig.add_subplot(111)
        
        num = self.filtered.select_dtypes(include=np.number)
        if num.shape[1] < 2:
            ax.text(0.5, 0.5, "Not Enough Numeric Data", ha="center", va="center", color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return
        
        im = ax.imshow(num.corr(), cmap="RdYlBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(num.shape[1])); ax.set_yticks(range(num.shape[1]))
        ax.set_xticklabels(num.columns, rotation=45, ha="right", color="black")
        ax.set_yticklabels(num.columns, color="black")
        cb = self.an_fig.colorbar(im, ax=ax, fraction=0.046)
        cb.ax.tick_params(colors="black"); cb.set_label("Correlation", color="black")
        ax.set_title("Feature Correlation Heat-map", color="black")
        self.an_canvas.draw()

    def _price_make(self):
        self.an_fig.clear()
        ax = self.an_fig.add_subplot(111)
        
        df = self.filtered
        if df.empty or {"make","price"}.issubset(df.columns) is False:
            ax.text(0.5, 0.5, "No Data for this Filter", ha="center", va="center", color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return

        makes = df["make"].value_counts().nlargest(15).index
        if makes.empty:
            ax.text(0.5, 0.5, "No Makes to Display", ha="center", va="center", color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return
            
        data  = [df[df["make"] == m]["price"] for m in makes]
        # ### FIX: Use 'labels' instead of 'tick_labels' ###
        ax.boxplot(data, labels=makes, vert=False, patch_artist=True,
                   boxprops=dict(facecolor=self.clr.info),
                   medianprops=dict(color=self.clr.danger))
        ax.set_title("Price Distribution by Make", color="black")
        ax.set_xlabel("Price ($)", color="black"); ax.set_ylabel("Make", color="black")
        ax.tick_params(colors="black")
        self.an_canvas.draw()

    def _ratings(self):
        self.an_fig.clear()
        ax = self.an_fig.add_subplot(111)
        
        cols = [c for c in (
            "consumerrating","comfortrating","interiordesignrating",
            "performancerating","valueformoneyrating","reliabilityrating")
            if c in self.filtered.columns]
        
        if not cols:
            ax.text(0.5, 0.5, "No Rating Data in CSV", ha="center", va="center", color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return
            
        data = self.filtered[cols].dropna()
        if data.empty:
            ax.text(0.5, 0.5, "No Rating Data for this Filter", ha="center", va="center", color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return

        ax.boxplot(data.values,
                   labels=[c.replace("rating","") for c in cols],
                   patch_artist=True,
                   boxprops=dict(facecolor=self.clr.warning),
                   medianprops=dict(color=self.clr.danger))
        ax.set_title("Ratings Distribution", color="black")
        ax.set_ylabel("Rating (out of 5)", color="black"); ax.set_xlabel("Rating Type", color="black")
        ax.tick_params(colors="black", rotation=45)
        self.an_canvas.draw()

    def _mpg(self):
        if hasattr(self, "_mpg_pick_id"):
            self.an_fig.canvas.mpl_disconnect(self._mpg_pick_id)
        self.an_fig.clear()
        ax = self.an_fig.add_subplot(111)
        self._mpg_annot = None
        
        raw = self.filtered
        if {"minmpg","maxmpg","make"}.issubset(raw.columns) is False:
            ax.text(0.5,0.5,"No MPG Data in CSV",ha="center",va="center",color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return
            
        df = raw.dropna(subset=["minmpg","maxmpg"])
        if df.empty:
            ax.text(0.5,0.5,"No MPG Data for this Filter",ha="center",va="center",color="black", fontsize=16)
            ax.axis('off')
            self.an_canvas.draw(); return

        top = df["make"].value_counts().nlargest(6).index
        palette = plt.cm.tab10.colors
        self._scatter_map = {}
        rest = df[~df["make"].isin(top)]
        if not rest.empty:
            sc = ax.scatter(rest["minmpg"], rest["maxmpg"],
                            s=25, c="lightgrey", alpha=.45, label="Other")
            sc.set_picker(True); sc.set_pickradius(10)
            self._scatter_map[sc] = rest.reset_index(drop=True)
        for i, mk in enumerate(top):
            sub = df[df["make"] == mk]
            sc = ax.scatter(sub["minmpg"], sub["maxmpg"],
                            s=35, color=palette[i % 10], label=mk, alpha=.8)
            sc.set_picker(True); sc.set_pickradius(10)
            self._scatter_map[sc] = sub.reset_index(drop=True)
        def _on_pick(event):
            if len(event.ind) == 0:
                return
            row = self._scatter_map[event.artist].iloc[event.ind[0]]
            label = shorten(f"{row['make']} {row.get('model','')}", width=40, placeholder="…")
            if self._mpg_annot: self._mpg_annot.remove()
            self._mpg_annot = ax.annotate(
                label, (row["minmpg"], row["maxmpg"]),
                xytext=(10, 10), textcoords="offset points",
                bbox=dict(boxstyle="round", fc="white", alpha=0.9), color="black")
            self.an_canvas.draw_idle()
        self._mpg_pick_id = self.an_fig.canvas.mpl_connect("pick_event", _on_pick)
        try:
            best_hwy  = df.loc[df["maxmpg"].idxmax()]
            best_city = df.loc[df["minmpg"].idxmax()]
            for r, t in [(best_hwy, "Best Hwy"), (best_city, "Best City")]:
                ax.annotate(
                    f"{t}: {shorten(r['make']+' '+str(r.get('model','')),28, placeholder='…')}",
                    xy=(r["minmpg"], r["maxmpg"]),
                    xytext=(5, 5), textcoords="offset points",
                    fontsize=7, color="black", backgroundcolor="#ffffff80")
        except (ValueError, KeyError): pass
        ax.set_title("City MPG vs Highway MPG", color="black")
        ax.set_xlabel("City MPG", color="black"); ax.set_ylabel("Highway MPG", color="black")
        ax.tick_params(colors="black")
        if len(top) > 0:
            ax.legend(facecolor="white", framealpha=.3, fontsize=8, labelcolor="black", loc="upper left")
        self.an_canvas.draw()

    # ───────────── TABLE / SEARCH / EXPORT ─────────────────────
    def _fill_tree(self):
        self.tree.delete(*self.tree.get_children())
        for _, row in self.filtered.head(500).iterrows():
            vals = [f"{v:,.2f}" if isinstance(v, float)
                    else f"{int(v):,}" if isinstance(v, (int, np.integer)) else v
                    for v in row]
            self.tree.insert("", "end", values=vals)

    def _search_tree(self, *_):
        term = self.search.get().lower()
        self.tree.delete(*self.tree.get_children())
        if not term: self._fill_tree(); return
        mask = self.filtered.astype(str).apply(
            lambda s: s.str.lower().str.contains(term, na=False)).any(axis=1)
        for _, row in self.filtered[mask].head(500).iterrows():
            vals = [f"{v:,.2f}" if isinstance(v, float)
                    else f"{int(v):,}" if isinstance(v, (int, np.integer)) else v
                    for v in row]
            self.tree.insert("", "end", values=vals)

    def _export(self):
        fn = tb.dialogs.filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if fn:
            self.filtered.to_csv(fn, index=False)
            tb.dialogs.Messagebox.show_info("Export complete", fn)

# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tb.Window(themename="cosmo")
    Dashboard(root)
    root.mainloop()