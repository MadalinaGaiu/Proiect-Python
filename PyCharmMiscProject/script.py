import tkinter as tk
from tkinter import ttk
import math
import os
import time

class AppManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Spectral Ultra-Complex")
        self.geometry("1100x1000")
        self.configure(bg="#1a1a1a")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartMenu, ModeSelection, SignalAnalyzer, GalleryPage, ComparisonPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartMenu")

    def show_frame(self, page_name, mode=None, load_file=None):
        frame = self.frames[page_name]
        if page_name == "SignalAnalyzer":
            if load_file:
                frame.current_filename = load_file
                frame.set_mode(mode if mode else "Fizică")
                frame.load_project_data(load_file)
            elif mode:
                frame.current_filename = None
                frame.set_mode(mode)
        elif page_name == "ComparisonPage" and mode:
            frame.perform_group_analysis(mode)

        if page_name == "GalleryPage":
            frame.refresh_gallery()
        frame.tkraise()

class StartMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        tk.Label(self, text="ANALIZA SEMNALELOR SINUSOIDALE", font=("Consolas", 32, "bold"), fg="#00d1b2",
                 bg="#1a1a1a").pack(pady=100)
        tk.Button(self, text="INIȚIALIZARE", font=("Consolas", 16, "bold"), bg="#333", fg="white", width=20,
                  command=lambda: controller.show_frame("ModeSelection")).pack(pady=10)
        tk.Button(self, text="📂 GALERIE PROIECTE", font=("Consolas", 16, "bold"), bg="#2c3e50", fg="white", width=20,
                  command=lambda: controller.show_frame("GalleryPage")).pack()

class ModeSelection(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        tk.Label(self, text="DOMENIU DE CERCETARE", font=("Consolas", 22, "bold"), fg="white", bg="#1a1a1a").pack(
            pady=40)
        grid = tk.Frame(self, bg="#1a1a1a")
        grid.pack()
        self.modes_data = {
            "Fizică": {"color": "#209cee", "desc": "Calcul RMS, factor de putere și analiza oscilațiilor."},
            "Telecom": {"color": "#2ecc71", "desc": "Analiză modulație, lățime bandă și integritate semnal."},
            "Medicină": {"color": "#ff3860", "desc": "Monitorizare pattern-uri EKG și detecție aritmii."},
            "Acustică": {"color": "#ffdd57", "desc": "Analiză dB și studiul rezonanței acustice."},
            "Astronomie": {"color": "#9b59b6", "desc": "Entropie stelarã și perturbații orbitale."},
            "Meteo": {"color": "#e67e22", "desc": "Predicție instabilitate și avertizări de furtună."}
        }
        r, c = 0, 0
        for name, info in self.modes_data.items():
            card = tk.Frame(grid, bg="#2a2a2a", padx=15, pady=15, highlightthickness=1,
                            highlightbackground=info['color'])
            card.grid(row=r, column=c, padx=10, pady=10)
            tk.Button(card, text=name, font=("Consolas", 12, "bold"), bg=info['color'], width=15,
                      command=lambda m=name: controller.show_frame("SignalAnalyzer", mode=m)).pack()
            tk.Label(card, text=info['desc'], fg="#bbb", bg="#2a2a2a", font=("Arial", 9), wraplength=160,
                     justify="center").pack(pady=10)
            c += 1
            if c > 2: c = 0; r += 1
        tk.Button(self, text="↩ ÎNAPOI", command=lambda: controller.show_frame("StartMenu"), bg="#444",
                  fg="white").pack(pady=30)

class SignalAnalyzer(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0f0f0f")
        self.controller = controller
        self.points = []
        self.current_filename = None
        self.last_x, self.last_y = None, None
        self.mode = "Fizică"
        self.tool = "pencil"
        self.colors = {"Fizică": "#209cee", "Telecom": "#2ecc71", "Medicină": "#ff3860", "Acustică": "#ffdd57",
                       "Astronomie": "#9b59b6", "Meteo": "#e67e22"}

        header = tk.Frame(self, bg="#1a1a1a", pady=10)
        header.pack(fill=tk.X)
        self.label_title = tk.Label(header, text="LABORATOR", font=("Consolas", 14, "bold"), bg="#1a1a1a", fg="white")
        self.label_title.pack(side=tk.LEFT, padx=20)
        tk.Button(header, text="MODURI", command=lambda: controller.show_frame("ModeSelection"), bg="#333", fg="white",
                  width=10).pack(side=tk.RIGHT, padx=5)
        tk.Button(header, text="GALERIE", command=lambda: controller.show_frame("GalleryPage"), bg="#2c3e50",
                  fg="white", width=10).pack(side=tk.RIGHT, padx=5)

        toolbar = tk.Frame(self, bg="#222", pady=5)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="✎ Creion", command=lambda: self.set_tool("pencil"), bg="#444", fg="white",
                  width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🧽 Radieră", command=lambda: self.set_tool("eraser"), bg="#444", fg="white",
                  width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🗑 Reset", command=self.clear_canvas, bg="#b33939", fg="white", width=10).pack(
            side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 SALVEAZĂ", command=self.save_project_data, bg="#f39c12", fg="black", width=12).pack(
            side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(self, width=800, height=400, bg="#050505", highlightthickness=1,
                                highlightbackground="#333")
        self.canvas.pack(pady=10)
        self.setup_graph()

        self.text_report = tk.Text(self, height=15, bg="#050505", fg="#33ff33", font=("Consolas", 10), padx=10, pady=10)
        self.text_report.pack(fill=tk.X, padx=50, pady=10)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.start_action)
        self.canvas.bind("<ButtonRelease-1>", self.stop_action)

    def setup_graph(self):
        self.canvas.delete("grid")
        mid_y = 200
        for x in range(0, 801, 80):
            self.canvas.create_line(x, 0, x, 400, fill="#1a1a1a", tags="grid")
            self.canvas.create_text(x, mid_y + 15, text=f"{x}ms", fill="#444", font=("Consolas", 7), tags="grid")
        for y in range(0, 401, 40):
            self.canvas.create_line(0, y, 800, y, fill="#1a1a1a", tags="grid")
            self.canvas.create_text(25, y, text=f"{mid_y - y}", fill="#444", font=("Consolas", 7), tags="grid")
        self.canvas.create_line(0, mid_y, 800, mid_y, fill="#444", width=2, tags="grid")

    def set_tool(self, tool):
        self.tool = tool

    def set_mode(self, mode):
        self.mode = mode
        self.label_title.config(text=f"LABORATOR: {mode.upper()}", fg=self.colors.get(mode, "white"))
        self.setup_graph();
        self.clear_canvas()

    def save_project_data(self):
        all_lines = self.canvas.find_withtag("line")
        if not all_lines: return
        if self.current_filename is None: self.current_filename = f"proiect_{self.mode}_{time.strftime('%H%M%S')}.dat"
        with open(self.current_filename, "w") as f:
            for line_id in all_lines:
                c = self.canvas.coords(line_id)
                f.write(f"{c[0]},{c[1]},{c[2]},{c[3]}\n")
        self.update_report(f"ANALIZĂ SALVATĂ: {self.current_filename}")

    def load_project_data(self, filename):
        if not os.path.exists(filename): return
        self.canvas.delete("line")
        with open(filename, "r") as f:
            for line in f:
                c = [float(val) for val in line.strip().split(',')]
                self.canvas.create_line(c[0], c[1], c[2], c[3], fill=self.colors[self.mode], width=2, tags="line")
        self.rebuild_and_analyze()

    def paint(self, event):
        if self.tool == "pencil" and self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.colors[self.mode], width=2,
                                    tags="line")
        elif self.tool == "eraser":
            for item in self.canvas.find_overlapping(event.x - 10, event.y - 10, event.x + 10, event.y + 10):
                if "line" in self.canvas.gettags(item): self.canvas.delete(item)
        self.last_x, self.last_y = event.x, event.y

    def start_action(self, event):
        self.last_x, self.last_y = event.x, event.y

    def stop_action(self, event):
        self.last_x, self.last_y = None, None; self.rebuild_and_analyze()

    def rebuild_and_analyze(self):
        all_lines = self.canvas.find_withtag("line")
        if not all_lines: return
        raw_points = []
        for line in all_lines:
            c = self.canvas.coords(line)
            raw_points.extend([(c[0], c[1]), (c[2], c[3])])
        self.points = sorted(list(set(raw_points)), key=lambda p: p[0])
        self.run_ai_analysis()

    def run_ai_analysis(self):
        if len(self.points) < 10: return
        y_vals = [200 - p[1] for p in self.points]
        deltas = [abs(y_vals[i] - y_vals[i - 1]) for i in range(1, len(y_vals))]
        avg_d = sum(deltas) / len(deltas)
        instab = min((max(deltas) / (avg_d + 1)) * 10, 100)
        self.update_report(f" STATUS: {'STABIL' if instab < 35 else 'CRITIC'}\nINSTABILITATE: {instab:.1f}%")

    def update_report(self, text):
        self.text_report.delete("1.0", tk.END);
        self.text_report.insert(tk.END, f">>> {text}")

    def clear_canvas(self):
        self.canvas.delete("line");
        self.points = [];
        self.current_filename = None
        self.setup_graph();
        self.update_report("Gata pentru scanare.")

class GalleryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        self.controller = controller
        tk.Label(self, text="GALERIE PROIECTE", font=("Consolas", 22, "bold"), fg="white", bg="#1a1a1a").pack(pady=40)
        self.files_list = tk.Listbox(self, bg="#000", fg="#00ff00", font=("Consolas", 12), width=50, height=15)
        self.files_list.pack(pady=10)
        btn_frame = tk.Frame(self, bg="#1a1a1a")
        btn_frame.pack()
        tk.Button(btn_frame, text="📂 DESCHIDE", command=self.open_project, bg="#27ae60", fg="white", width=12).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 COMPARĂ TIP", command=self.compare_by_type, bg="#2980b9", fg="white",
                  width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 ȘTERGE", command=self.delete_file, bg="#c0392b", fg="white", width=12).pack(
            side=tk.LEFT, padx=5)
        tk.Button(self, text="↩ ÎNAPOI", command=lambda: controller.show_frame("StartMenu"), bg="#444",
                  fg="white").pack(pady=20)

    def refresh_gallery(self):
        self.files_list.delete(0, tk.END)
        for f in sorted([f for f in os.listdir('.') if f.endswith('.dat')]): self.files_list.insert(tk.END, f)

    def open_project(self):
        try:
            f = self.files_list.get(self.files_list.curselection())
            self.controller.show_frame("SignalAnalyzer", mode=f.split("_")[1], load_file=f)
        except:
            pass

    def compare_by_type(self):
        try:
            f = self.files_list.get(self.files_list.curselection())
            self.controller.show_frame("ComparisonPage", mode=f.split("_")[1])
        except:
            pass

    def delete_file(self):
        try:
            f = self.files_list.get(self.files_list.curselection())
            os.remove(f);
            self.refresh_gallery()
        except:
            pass

class ComparisonPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0f0f0f")
        self.controller = controller
        tk.Label(self, text="📊 ANALIZĂ COMPARATIVĂ & SFATURI", font=("Consolas", 22, "bold"), fg="#00d1b2",
                 bg="#0f0f0f").pack(pady=20)

        self.stats_panel = tk.Frame(self, bg="#1a1a1a", pady=15, highlightthickness=1, highlightbackground="#333")
        self.stats_panel.pack(fill=tk.X, padx=20, pady=10)
        self.label_avg = tk.Label(self.stats_panel, text="Medie: --", fg="white", bg="#1a1a1a", font=("Consolas", 11))
        self.label_avg.pack(side=tk.LEFT, padx=20)
        self.label_trend = tk.Label(self.stats_panel, text="Trend: --", fg="#ffdd57", bg="#1a1a1a",
                                    font=("Consolas", 11, "bold"))
        self.label_trend.pack(side=tk.LEFT, padx=20)

        self.tree = ttk.Treeview(self, columns=("Data", "Instab", "Diagnostic"), show='headings', height=10)
        self.tree.heading("Data", text="DATA FIȘIER");
        self.tree.heading("Instab", text="INSTABILITATE %")
        self.tree.heading("Diagnostic", text="STATUS")
        self.tree.pack(pady=10, padx=20, fill=tk.BOTH)

        tk.Label(self, text=" ADVISORY SYSTEM", font=("Consolas", 14, "bold"), fg="#33ff33", bg="#0f0f0f").pack(pady=10)
        self.advice_box = tk.Text(self, height=8, bg="#000", fg="#33ff33", font=("Consolas", 11), padx=15, pady=15,
                                  borderwidth=1, highlightbackground="#33ff33")
        self.advice_box.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(self, text="↩ ÎNAPOI LA GALERIE", command=lambda: controller.show_frame("GalleryPage"), bg="#444",
                  fg="white", width=25).pack(pady=20)

    def perform_group_analysis(self, mode):
        for i in self.tree.get_children(): self.tree.delete(i)
        files = sorted([f for f in os.listdir('.') if f.endswith('.dat') and f"_{mode}_" in f])
        if not files: return

        all_instabilities = []
        for f in files:
            try:
                with open(f, "r") as file:
                    y_vals_raw = []
                    for line in file:
                        coords = line.strip().split(',')
                        if len(coords) == 4:
                            y_vals_raw.append(200 - float(coords[1]))
                            y_vals_raw.append(200 - float(coords[3]))

                    # Eliminăm duplicatele consecutive pentru calcul corect al deltei
                    y_vals = [y_vals_raw[i] for i in range(len(y_vals_raw)) if
                              i == 0 or y_vals_raw[i] != y_vals_raw[i - 1]]

                if len(y_vals) > 5:
                    deltas = [abs(y_vals[i] - y_vals[i - 1]) for i in range(1, len(y_vals))]
                    avg_d = sum(deltas) / len(deltas)
                    instab = min((max(deltas) / (avg_d + 1)) * 10, 100)
                    all_instabilities.append(instab)
                    diag = "Stabil" if instab < 35 else "Risc Crescut" if instab < 65 else "CRITIC"
                    self.tree.insert("", tk.END, values=(f.split("_")[2].replace(".dat", ""), f"{instab:.1f}%", diag))
            except:
                pass

        if all_instabilities:
            avg_instab = sum(all_instabilities) / len(all_instabilities)
            self.label_avg.config(text=f"Medie Grup {mode}: {avg_instab:.1f}%")
            trend_val = 0
            if len(all_instabilities) >= 2:
                trend_val = all_instabilities[-1] - all_instabilities[-2]
                self.label_trend.config(text=f"Trend: {'📈 INSTABIL' if trend_val > 5 else '📉 OK'}")
            self.generate_ai_advice(mode, avg_instab, trend_val)

    def generate_ai_advice(self, mode, avg, trend):
        self.advice_box.delete("1.0", tk.END)
        advice = f"RECOMANDARE PENTRU CATEGORIA {mode.upper()}:\n\n"
        if avg < 30 and trend <= 0:
            advice += ">>> Sistemul este într-o stare de echilibru perfect."
        elif trend > 5:
            advice += f">>> ATENȚIE: Creștere rapidă a haosului.\n"
            if mode == "Meteo":
                advice += ">>> Sfat: Verificați senzorii barometrici. Risc de furtună."
            elif mode == "Medicină":
                advice += ">>> Sfat: Recomandat consult medical. Pattern tahicardic."
            elif mode == "Fizică":
                advice += ">>> Sfat: Opriți sistemul. Vibrații periculoase."
        elif avg > 60:
            advice += ">>> Stare critică persistentă. Recalibrați scanarea."
        else:
            advice += ">>> Mici fluctuații detectate. Monitorizați în continuare."
        self.advice_box.insert(tk.END, advice)

if __name__ == "__main__":
    app = AppManager()
    app.mainloop()