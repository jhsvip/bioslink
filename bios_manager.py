import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import webbrowser
import os
import sys
from datetime import datetime

class BIOSManager:
    def __init__(self, root):
        self.root = root
        self.root.title("及叔出品 - 主板BIOS链接管理器")
        self.root.geometry("1100x700")
        
        self.COLOR_PRIMARY = "#2563eb"
        self.COLOR_SUCCESS = "#10b981"
        self.COLOR_DANGER = "#ef4444"
        self.COLOR_BG = "#f8fafc"
        self.root.configure(bg=self.COLOR_BG)
        
        self.setup_styles()
        
        # ✅ 核心修复：exe 也能正确加载 bios_links.json
        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(app_path, "bios_links.json")
        
        self.bios_data = self.load_data()

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        top_frame = ttk.LabelFrame(main_frame, text="数据管理与查询", padding="10")
        top_frame.pack(fill="x", pady=(0, 10))
        
        self.create_add_form(top_frame)
        
        right_top_frame = ttk.Frame(top_frame)
        right_top_frame.pack(side="right", fill="y", padx=(20, 0))
        
        self.create_query_input(right_top_frame)
        self.create_tips_panel(right_top_frame)
        
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 10))
        
        bottom_frame = ttk.LabelFrame(main_frame, text="BIOS 链接查询结果", padding="10")
        bottom_frame.pack(fill="both", expand=True)
        self.create_result_table(bottom_frame)
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor="w", 
                                   font=("微软雅黑", 9, "bold"),
                                   background=self.COLOR_PRIMARY,
                                   foreground="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_bios_list()
        self.status_var.set(f"🚀 加载完成，共 {len(self.bios_data)} 条记录 | 及叔出品")

    def setup_styles(self):
        style = ttk.Style()
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        
        style.configure("Treeview", rowheight=28, font=("微软雅黑", 10),
                        background="white", fieldbackground="white", foreground="black",
                        borderwidth=1, relief="solid")
        style.configure("Treeview.Heading", font=("微软雅黑", 10, "bold"),
                        background=self.COLOR_PRIMARY, foreground="white")
        style.map("Treeview", background=[('selected', '#bfdbfe')])
        style.configure("TButton", font=("微软雅黑", 9), padding=5)
        style.configure("TLabelframe", background=self.COLOR_BG)
        style.configure("TLabelframe.Label", font=("微软雅黑", 10, "bold"), foreground=self.COLOR_PRIMARY)

    def create_add_form(self, parent):
        form_frame = ttk.LabelFrame(parent, text="添加新BIOS链接", padding="10")
        form_frame.pack(side="left", fill="y", padx=(0, 20))
        fields = [
            ("品牌:", "brand_var", ["ASUS", "GIGABYTE", "MSI", "ASRock", "Biostar", "other"]),
            ("芯片组:", "chipset_var", None),
            ("系列:", "series_var", None),
            ("型号:", "model_var", None),
            ("链接:", "link_var", None),
        ]
        self.entries = {}
        for i, (label_text, var_name, values) in enumerate(fields):
            ttk.Label(form_frame, text=label_text, font=("微软雅黑", 9)).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            var = tk.StringVar()
            self.entries[var_name] = var
            if values:
                widget = ttk.Combobox(form_frame, textvariable=var, width=18, font=("微软雅黑", 9))
                widget['values'] = values
                widget.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                if var_name == "brand_var": var.set("ASUS")
            else:
                width_val = 25 if var_name == "link_var" else 18
                widget = ttk.Entry(form_frame, textvariable=var, width=width_val, font=("微软雅黑", 9))
                widget.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="备注:", font=("微软雅黑", 9)).grid(row=5, column=0, sticky="ne", padx=5, pady=5)
        self.notes_text = scrolledtext.ScrolledText(form_frame, width=25, height=3, font=("微软雅黑", 9))
        self.notes_text.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="e", pady=10)
        ttk.Button(btn_frame, text="添加", command=self.add_bios_link, width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_form, width=10).pack(side="left", padx=5)

    def create_query_input(self, parent):
        query_frame = ttk.LabelFrame(parent, text="🔍 快速查询", padding="10")
        query_frame.pack(side="top", fill="x", pady=(0, 10))
        ttk.Label(query_frame, text="品牌:", font=("微软雅黑", 9)).grid(row=0, column=0, padx=5, pady=5)
        self.query_brand_var = tk.StringVar(value="全部")
        brand_combo = ttk.Combobox(query_frame, textvariable=self.query_brand_var, width=12, font=("微软雅黑", 9))
        brand_combo['values'] = ("全部", "ASUS", "GIGABYTE", "MSI", "ASRock", "Biostar", "other")
        brand_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(query_frame, text="型号:", font=("微软雅黑", 9)).grid(row=0, column=2, padx=5, pady=5)
        self.query_model_var = tk.StringVar()
        ttk.Entry(query_frame, textvariable=self.query_model_var, width=20, font=("微软雅黑", 9)).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(query_frame, text="查询", command=self.search_bios_links).grid(row=0, column=4, padx=10)
        ttk.Button(query_frame, text="刷新", command=self.update_bios_list).grid(row=0, column=5)

    def create_tips_panel(self, parent):
        tips_frame = ttk.LabelFrame(parent, text="💡 今日提示", padding="10")
        tips_frame.pack(side="top", fill="x", pady=(0, 10))
        ttk.Label(tips_frame, text=f"🕒 时间: {datetime.now().strftime('%H:%M')}",
                  font=("微软雅黑", 10, "bold"), foreground=self.COLOR_PRIMARY).pack(anchor="w", pady=2)
        ttk.Label(tips_frame, text="☀️ 状态: 系统运行正常",
                  font=("微软雅黑", 10), foreground="#64748b").pack(anchor="w", pady=2)
        ttk.Label(tips_frame, text="💻 任务: 整理BIOS库",
                  font=("微软雅黑", 10, "bold"), foreground=self.COLOR_DANGER).pack(anchor="w", pady=10)

    def create_result_table(self, parent):
        columns = ("型号", "品牌", "芯片组", "系列", "下载链接", "备注")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        col_config = [
            ("型号", 220, "w", True),
            ("品牌", 80, "center", False),
            ("芯片组", 100, "center", False),
            ("系列", 100, "w", False),
            ("下载链接", 180, "w", False),
            ("备注", 150, "w", False)
        ]
        for col_name, width, anchor, bold in col_config:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, minwidth=50, anchor=anchor)
        self.tree.tag_configure('main_model', font=('微软雅黑', 10, 'bold'))
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.open_link)
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="✎ 编辑", command=self.edit_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="导出", command=self.export_links).pack(side="right", padx=5)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.bios_data, f, indent=2, ensure_ascii=False)

    def update_bios_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, item in enumerate(self.bios_data):
            self.tree.insert("", "end", iid=f"ITEM_{idx}", values=(
                item["model"], item["brand"], item["chipset"], item["series"], item["link"], item.get("notes", "")
            ), tags=('main_model',))

    def search_bios_links(self):
        brand = self.query_brand_var.get()
        model = self.query_model_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, item in enumerate(self.bios_data):
            if brand != "全部" and item["brand"] != brand:
                continue
            if model and model not in item["model"].lower():
                continue
            self.tree.insert("", "end", iid=f"ITEM_{idx}", values=(
                item["model"], item["brand"], item["chipset"], item["series"], item["link"], item.get("notes", "")
            ), tags=('main_model',))

    def add_bios_link(self):
        brand = self.entries['brand_var'].get()
        chipset = self.entries['chipset_var'].get()
        series = self.entries['series_var'].get()
        model = self.entries['model_var'].get()
        link = self.entries['link_var'].get()
        notes = self.notes_text.get("1.0", "end-1c")
        if not model or not link:
            messagebox.showwarning("警告", "型号和链接不能为空！")
            return
        if not link.startswith("http"):
            messagebox.showerror("错误", "链接必须以 http 开头")
            return
        self.bios_data.append({
            "brand": brand, "chipset": chipset, "series": series,
            "model": model, "link": link, "notes": notes
        })
        self.save_data()
        self.update_bios_list()
        self.reset_form()

    def reset_form(self):
        self.entries['brand_var'].set("ASUS")
        for k in self.entries:
            if k != "brand_var":
                self.entries[k].set("")
        self.notes_text.delete("1.0", "end")

    def open_link(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        selected = self.tree.selection()
        if selected:
            link = self.tree.item(selected[0])["values"][4]
            if link and link.startswith("http"):
                webbrowser.open(link)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一条数据")
            return
        iid = selected[0]
        idx = int(iid.split("_")[1])
        item = self.bios_data[idx]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("编辑 BIOS 信息")
        edit_win.geometry("750x450")
        edit_win.resizable(True, True)
        edit_win.configure(bg=self.COLOR_BG)

        frame = ttk.Frame(edit_win, padding="20")
        frame.pack(fill="both", expand=True)

        vars = {}
        fields = [
            ("品牌", "brand", ["ASUS","GIGABYTE","MSI","ASRock","Biostar","other"], item["brand"]),
            ("芯片组", "chipset", None, item["chipset"]),
            ("系列", "series", None, item["series"]),
            ("型号", "model", None, item["model"]),
            ("链接", "link", None, item["link"]),
        ]

        for i, (lbl, key, opts, val) in enumerate(fields):
            ttk.Label(frame, text=lbl + ":", font=("微软雅黑", 10)).grid(
                row=i, column=0, sticky="e", padx=10, pady=8
            )
            v = tk.StringVar(value=val)
            vars[key] = v

            if opts:
                cb = ttk.Combobox(frame, textvariable=v, values=opts, state="readonly", width=40)
                cb.grid(row=i, column=1, sticky="ew", padx=10, pady=8)
            else:
                e = ttk.Entry(frame, textvariable=v, font=("微软雅黑", 10))
                e.grid(row=i, column=1, sticky="ew", padx=10, pady=8)

        ttk.Label(frame, text="备注:", font=("微软雅黑", 10)).grid(
            row=5, column=0, sticky="ne", padx=10, pady=8
        )
        txt = scrolledtext.ScrolledText(
            frame, height=5, width=60, font=("微软雅黑", 10),
            wrap="none", undo=False
        )
        txt.grid(row=5, column=1, sticky="ew", padx=10, pady=8)
        txt.insert("1.0", item.get("notes", ""))

        def save():
            m = vars["model"].get()
            l = vars["link"].get()
            if not m or not l:
                messagebox.showwarning("警告", "型号和链接不能为空")
                return
            if not l.startswith("http"):
                messagebox.showerror("错误", "链接格式错误")
                return
            self.bios_data[idx] = {
                "brand": vars["brand"].get(),
                "chipset": vars["chipset"].get(),
                "series": vars["series"].get(),
                "model": m, "link": l,
                "notes": txt.get("1.0","end-1c")
            }
            self.save_data()
            self.update_bios_list()
            edit_win.destroy()

        ttk.Button(frame, text="保存修改", command=save, width=18).grid(
            row=6, column=1, sticky="e", padx=10, pady=15
        )

        edit_win.update_idletasks()
        x = (edit_win.winfo_screenwidth() - 750) // 2
        y = (edit_win.winfo_screenheight() - 450) // 2
        edit_win.geometry(f"750x450+{x}+{y}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示","请先选择要删除的行")
            return
        iid = selected[0]
        idx = int(iid.split("_")[1])
        model = self.bios_data[idx]["model"]
        if messagebox.askyesno("确认删除", f"确定删除 {model} ?"):
            del self.bios_data[idx]
            self.save_data()
            self.update_bios_list()

    def export_links(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件","*.txt")])
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"BIOS链接导出 {datetime.now()}\n{'='*50}\n")
            for it in self.bios_data:
                f.write(f"【{it['model']}】{it['link']}\n")
        messagebox.showinfo("导出成功", f"已导出到：\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BIOSManager(root)
    root.mainloop()
