import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math, numpy as np, sympy as sp, csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------- safe eval ----------
def safe_eval(expr, extra=None):
    allowed = {
        'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        'log': math.log, 'ln': math.log, 'log10': math.log10, 'exp': math.exp,
        'pi': math.pi, 'e': math.e, 'abs': abs, 'round': round,
        'floor': math.floor, 'ceil': math.ceil, 'pow': pow, 'complex': complex,
        'i': 1j
    }
    if extra:
        allowed.update(extra)
    if "__" in expr or "import" in expr or "open(" in expr:
        raise ValueError("Unsafe expression")
    return eval(expr, {"__builtins__": {}}, allowed)

# ---------- Modern App ----------
class QuantumCalcX(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QuantumCalc X — Modern Hackulator Edition")
        self.geometry("1000x720")
        self.configure(bg="#1E1E2F")
        self.history = []
        self._style_ui()
        self._build_ui()

    # ---------- Modern Style ----------
    def _style_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background="#1E1E2F", borderwidth=0)
        style.configure("TNotebook.Tab",
                        font=("Segoe UI", 12, "bold"),
                        padding=[12, 8],
                        background="#2E2E4F",
                        foreground="#EEEEEE",
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#3B82F6")],
                  foreground=[("selected", "#FFFFFF")])

        style.configure("Rounded.TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=8,
                        relief="flat",
                        borderwidth=0,
                        background="#3B82F6",
                        foreground="white")
        style.map("Rounded.TButton",
                  background=[("active", "#2563EB")],
                  relief=[("pressed", "groove")])

        style.configure("TEntry",
                        font=("Consolas", 14),
                        fieldbackground="#292942",
                        foreground="white",
                        borderwidth=0,
                        relief="flat",
                        padding=8)
        style.configure("TLabel",
                        background="#1E1E2F",
                        foreground="#FFFFFF",
                        font=("Segoe UI", 11))
        style.configure("TFrame", background="#1E1E2F")

    # ---------- Build Tabs ----------
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs = {
            "Basic": ttk.Frame(nb),
            "Programmer": ttk.Frame(nb),
            "Matrix": ttk.Frame(nb),
            "CAS": ttk.Frame(nb),
            "Plotter": ttk.Frame(nb),
            "History": ttk.Frame(nb)
        }
        for name, tab in self.tabs.items():
            nb.add(tab, text=name)
            tab.configure(style="TFrame")

        self._build_basic()
        self._build_programmer()
        self._build_matrix()
        self._build_cas()
        self._build_plot()
        self._build_history()

    # ---------- Basic Tab ----------
    def _build_basic(self):
        tab = self.tabs["Basic"]
        top = ttk.Frame(tab); top.pack(fill='x', pady=8)
        self.expr = tk.StringVar(); self.result = tk.StringVar()

        ttk.Entry(top, textvariable=self.expr).pack(side='left', fill='x', expand=True, padx=(8, 4))
        ttk.Button(top, text="=", style="Rounded.TButton", command=self._calc).pack(side='left', padx=(4,8))

        ttk.Label(tab, textvariable=self.result, font=("Consolas", 18, "bold"), foreground="#3B82F6").pack(pady=8)

        grid = ttk.Frame(tab); grid.pack(fill='both', expand=True, padx=8, pady=8)
        keys = [
            ['7','8','9','/','sqrt'],
            ['4','5','6','*','pow'],
            ['1','2','3','-','('],
            ['0','.','+','=',')'],
            ['sin','cos','tan','log','pi'],
            ['exp','^','abs','i','C']
        ]
        for r, row in enumerate(keys):
            for c, k in enumerate(row):
                color = "#3B82F6" if k not in ('=','C') else ("#10B981" if k=='=' else "#EF4444")
                b = tk.Button(grid, text=k, font=("Segoe UI", 12, "bold"),
                              bg=color, fg="white", relief="flat",
                              activebackground="#1E40AF", bd=0,
                              highlightthickness=0,
                              command=lambda key=k: self._press(key))
                b.grid(row=r, column=c, sticky='nsew', padx=6, pady=6, ipadx=4, ipady=4)
        for i in range(5):
            grid.columnconfigure(i, weight=1)
        for i in range(len(keys)):
            grid.rowconfigure(i, weight=1)

    def _press(self, k):
        if k == "C":
            self.expr.set(""); self.result.set(""); return
        if k == "=":
            self._calc(); return
        mapping = {'sqrt':'sqrt(','pow':'pow(','^':'**','pi':'pi','i':'i'}
        self.expr.set(self.expr.get() + mapping.get(k,k))

    def _calc(self):
        try:
            val = safe_eval(self.expr.get().replace('^','**'))
            self.result.set(str(val))
            self._history("basic:"+self.expr.get(), val)
        except Exception as e:
            self.result.set("Error: "+str(e))

    # ---------- Programmer ----------
    def _build_programmer(self):
        t = self.tabs["Programmer"]
        self.prog_in = tk.StringVar()
        ttk.Entry(t, textvariable=self.prog_in).pack(fill='x', padx=8, pady=8)
        ttk.Button(t, text="Evaluate", style="Rounded.TButton", command=self._prog_eval).pack(pady=4)
        self.prog_out = tk.Text(t, height=10, bg="#111122", fg="#D1D5DB", insertbackground="white")
        self.prog_out.pack(fill='both', expand=True, padx=8, pady=8)

    def _prog_eval(self):
        e = self.prog_in.get()
        try:
            res = safe_eval(e)
            s = f"{res}\n"
            if isinstance(res, int):
                s += f"bin: {bin(res)}\nhex: {hex(res)}\n"
            self.prog_out.insert('end', s+"\n")
            self._history("prog:"+e, res)
        except Exception as ex:
            self.prog_out.insert('end', "Error: "+str(ex)+"\n")

    # ---------- Matrix ----------
    def _build_matrix(self):
        t = self.tabs["Matrix"]
        ttk.Label(t, text="Matrix A").pack(anchor='w', padx=8)
        self.matA = tk.Text(t, height=5, bg="#111122", fg="#D1D5DB")
        self.matA.pack(fill='x', padx=8, pady=4)
        ttk.Label(t, text="Matrix B").pack(anchor='w', padx=8)
        self.matB = tk.Text(t, height=5, bg="#111122", fg="#D1D5DB")
        self.matB.pack(fill='x', padx=8, pady=4)
        f = ttk.Frame(t); f.pack(pady=6)
        for txt,op in [("A+B","add"),("A×B","mul"),("inv(A)","inv"),("det(A)","det")]:
            ttk.Button(f, text=txt, style="Rounded.TButton",
                       command=lambda o=op:self._matop(o)).pack(side='left', padx=4)
        self.mat_out = tk.Text(t, height=10, bg="#111122", fg="#D1D5DB")
        self.mat_out.pack(fill='both', expand=True, padx=8, pady=8)

    def _parse(self, txt):
        if not txt.strip(): return None
        rows = [list(map(float, r.split(','))) for r in txt.strip().splitlines()]
        return np.array(rows)

    def _matop(self, op):
        try:
            A = self._parse(self.matA.get('1.0','end'))
            B = self._parse(self.matB.get('1.0','end'))
            if op=="add": res = A+B
            elif op=="mul": res = A.dot(B)
            elif op=="inv": res = np.linalg.inv(A)
            elif op=="det": res = np.linalg.det(A)
            self.mat_out.insert('end', f"{op}: {res}\n\n")
            self._history("matrix_"+op, str(res))
        except Exception as e:
            self.mat_out.insert('end', "Error: "+str(e)+"\n")

    # ---------- CAS ----------
    def _build_cas(self):
        t = self.tabs["CAS"]
        ttk.Label(t, text="Enter expression (use x)").pack(anchor='w', padx=8)
        self.cas = tk.StringVar()
        ttk.Entry(t, textvariable=self.cas).pack(fill='x', padx=8, pady=6)
        f = ttk.Frame(t); f.pack(pady=6)
        for label, cmd in [("Simplify", self._cas_simplify),
                           ("Derivative", self._cas_diff),
                           ("Integral", self._cas_int),
                           ("Solve", self._cas_solve)]:
            ttk.Button(f, text=label, style="Rounded.TButton", command=cmd).pack(side='left', padx=4)
        self.cas_out = tk.Text(t, height=10, bg="#111122", fg="#D1D5DB")
        self.cas_out.pack(fill='both', expand=True, padx=8, pady=8)

    def _cas_simplify(self):
        e = self.cas.get()
        try:
            res = sp.simplify(sp.sympify(e))
            self.cas_out.insert('end', f"Simplified: {res}\n\n")
            self._history("cas_simplify:"+e, res)
        except Exception as ex:
            self.cas_out.insert('end', "Error: "+str(ex)+"\n")

    def _cas_diff(self):
        e = self.cas.get(); x = sp.symbols('x')
        try:
            res = sp.diff(sp.sympify(e),x)
            self.cas_out.insert('end', f"d/dx: {res}\n\n")
            self._history("cas_diff:"+e,res)
        except Exception as ex:
            self.cas_out.insert('end',"Error:"+str(ex)+"\n")

    def _cas_int(self):
        e=self.cas.get();x=sp.symbols('x')
        try:
            res=sp.integrate(sp.sympify(e),x)
            self.cas_out.insert('end',f"∫: {res}+C\n\n")
            self._history("cas_int:"+e,res)
        except Exception as ex:
            self.cas_out.insert('end',"Error:"+str(ex)+"\n")

    def _cas_solve(self):
        e=self.cas.get();x=sp.symbols('x')
        try:
            res=sp.solve(sp.sympify(e),x)
            self.cas_out.insert('end',f"Solutions: {res}\n\n")
            self._history("cas_solve:"+e,res)
        except Exception as ex:
            self.cas_out.insert('end',"Error:"+str(ex)+"\n")

    # ---------- Plotter ----------
    def _build_plot(self):
        t=self.tabs["Plotter"]
        c=ttk.Frame(t);c.pack(pady=8)
        self.plot_expr=tk.StringVar(value="sin(x)")
        ttk.Entry(c,textvariable=self.plot_expr,width=30).pack(side='left',padx=4)
        ttk.Button(c,text="Plot",style="Rounded.TButton",command=self._plot).pack(side='left',padx=4)
        self.fig,self.ax=plt.subplots(figsize=(5,4))
        self.ax.set_facecolor("#111122");self.fig.patch.set_facecolor("#1E1E2F")
        self.canvas=FigureCanvasTkAgg(self.fig,master=t)
        self.canvas.get_tk_widget().pack(fill='both',expand=True,padx=8,pady=8)

    def _plot(self):
        expr=self.plot_expr.get()
        x=np.linspace(-10,10,400)
        env={'sin':np.sin,'cos':np.cos,'tan':np.tan,'exp':np.exp,'log':np.log,'sqrt':np.sqrt,'abs':np.abs,'pi':np.pi,'e':np.e}
        y=[]
        for xv in x:
            try:y.append(eval(expr,{"__builtins__":{}},dict(env,x=xv)))
            except:y.append(np.nan)
        self.ax.clear();self.ax.plot(x,y,color="#3B82F6")
        self.ax.grid(True,color="#333");self.ax.set_xlabel('x');self.ax.set_ylabel('f(x)')
        self.fig.tight_layout();self.canvas.draw()
        self._history("plot:"+expr,"done")

    # ---------- History ----------
    def _build_history(self):
        t=self.tabs["History"]
        f=ttk.Frame(t);f.pack(pady=6)
        ttk.Button(f,text="Export CSV",style="Rounded.TButton",command=self._export).pack(side='left',padx=4)
        ttk.Button(f,text="Clear",style="Rounded.TButton",command=self._clear).pack(side='left',padx=4)
        self.hist=tk.Text(t,bg="#111122",fg="#D1D5DB")
        self.hist.pack(fill='both',expand=True,padx=8,pady=8)

    def _history(self,expr,res):
        from datetime import datetime
        t=datetime.now().strftime("%H:%M:%S")
        self.hist.insert('end',f"[{t}] {expr} = {res}\n")
        self.hist.see('end')
        self.history.append((t,expr,res))

    def _export(self):
        if not self.history:
            messagebox.showinfo("Empty","No history")
            return
        fp=filedialog.asksaveasfilename(defaultextension=".csv")
        if not fp:return
        with open(fp,'w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(["time","expr","result"]);w.writerows(self.history)
        messagebox.showinfo("Saved",f"Exported to {fp}")

    def _clear(self):
        self.history.clear();self.hist.delete('1.0','end')

if __name__=="__main__":
    QuantumCalcX().mainloop()
