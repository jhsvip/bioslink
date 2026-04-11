import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import webbrowser
import os
from datetime import datetime

class BIOSManager:
    def __init__(self, root):
        self.root = root
        self.root.title("主板BIOS链接管理器")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f2f5")
        
        # 全局主题 + 字体
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('Microsoft YaHei', 9))
        style.configure("Treeview", font=('Microsoft YaHei', 10), rowheight=28)
        style.configure("Treeview.Heading", font=('Microsoft YaHei', 11, 'bold'))
        style.configure("TLabelframe", padding=5)
        
        # 数据文件
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bios_links.json")
        self.bios_data = self.load_data()
        
        # 主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill="both", expand=True)
        
        # 顶部：添加 + 查询
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="x", pady=(0, 12))
        
        self.add_frame = ttk.LabelFrame(self.top_frame, text="添加新BIOS链接", padding="10")
        self.add_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.create_add_form()
        
        self.query_frame = ttk.LabelFrame(self.top_frame, text="BIOS链接查询", padding="10")
        self.query_frame.pack(side="right", fill="x", expand=True)
        self.create_query_controls()
        
        # 底部：查询结果（填满整个底部）
        self.result_main_frame = ttk.LabelFrame(self.main_frame, text="查询结果", padding="10")
        self.result_main_frame.pack(fill="both", expand=True, pady=(5,0))
        self.create_result_table()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化
        self.update_bios_list()
        self.update_query_results()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        else:
            return []

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.bios_data, f, indent=2, ensure_ascii=False)
            self.status_var.set("数据已保存")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存失败：{str(e)}")

    def create_add_form(self):
        # 品牌 芯片组
        row1 = ttk.Frame(self.add_frame)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="品牌:", width=8).pack(side="left", padx=(0,5))
        self.brand_var = tk.StringVar()
        cbo = ttk.Combobox(row1, textvariable=self.brand_var, width=15)
        cbo['values'] = ("ASUS", "GIGABYTE", "MSI", "ASRock", "Biostar", "other")
        cbo.pack(side="left", padx=(0,15))
        cbo.current(0)

        ttk.Label(row1, text="芯片组:", width=8).pack(side="left", padx=(0,5))
        self.chipset_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.chipset_var, width=15).pack(side="left", padx=(0,15))

        # 系列 型号
        row2 = ttk.Frame(self.add_frame)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="系列:", width=8).pack(side="left", padx=(0,5))
        self.series_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.series_var, width=15).pack(side="left", padx=(0,15))

        ttk.Label(row2, text="型号:", width=8).pack(side="left", padx=(0,5))
        self.model_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.model_var, width=15).pack(side="left", padx=(0,15))

        # 链接
        row3 = ttk.Frame(self.add_frame)
        row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="下载链接:", width=8).pack(side="left", padx=(0,5))
        self.link_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.link_var).pack(side="left", fill="x", expand=True)

        # 备注
        row4 = ttk.Frame(self.add_frame)
        row4.pack(fill="x", pady=4)
        ttk.Label(row4, text="备注:", width=8).pack(side="left", padx=(0,5))
        self.notes_text = scrolledtext.ScrolledText(row4, height=2)
        self.notes_text.pack(side="left", fill="x", expand=True)

        # 按钮
        row5 = ttk.Frame(self.add_frame)
        row5.pack(fill="x", pady=6)
        ttk.Button(row5, text="添加", command=self.add_bios_link, width=10).pack(side="left", padx=5)
        ttk.Button(row5, text="重置", command=self.reset_form, width=10).pack(side="left", padx=5)
        ttk.Label(row5, text="链接必须以 http/https 开头", foreground="#666").pack(side="right")

    def create_query_controls(self):
        row1 = ttk.Frame(self.query_frame)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="品牌:", width=8).pack(side="left", padx=(0,5))
        self.query_brand_var = tk.StringVar()
        cbo = ttk.Combobox(row1, textvariable=self.query_brand_var, width=12)
        cbo['values'] = ("全部", "ASUS", "GIGABYTE", "MSI", "ASRock", "Biostar", "other")
        cbo.pack(side="left", padx=(0,15))
        cbo.current(0)

        ttk.Label(row1, text="芯片组:", width=8).pack(side="left", padx=(0,5))
        self.query_chipset_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.query_chipset_var, width=12).pack(side="left", padx=(0,15))

        row2 = ttk.Frame(self.query_frame)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="系列:", width=8).pack(side="left", padx=(0,5))
        self.query_series_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.query_series_var, width=12).pack(side="left", padx=(0,15))

        ttk.Label(row2, text="型号:", width=8).pack(side="left", padx=(0,5))
        self.query_model_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.query_model_var, width=12).pack(side="left", padx=(0,15))

        row3 = ttk.Frame(self.query_frame)
        row3.pack(fill="x", pady=8)
        ttk.Button(row3, text="查询", command=self.search_bios_links, width=10).pack(side="left", padx=5)
        ttk.Button(row3, text="导出链接", command=self.export_links, width=12).pack(side="left", padx=5)

    def create_result_table(self):
        # 按钮
        btn_frame = ttk.Frame(self.result_main_frame)
        btn_frame.pack(fill="x", pady=(0,8))
        ttk.Button(btn_frame, text="编辑选中", command=self.edit_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_selected).pack(side="left", padx=5)

        # 表格
        cols = ["型号", "品牌", "芯片组", "系列", "链接", "备注"]
        self.tree = ttk.Treeview(self.result_main_frame, columns=cols, show="headings")

        # 列宽与样式（型号最大最左，品牌芯片组缩进）
        self.tree.heading("型号", text="型号")
        self.tree.column("型号", width=240, minwidth=200)
        self.tree.heading("品牌", text="品牌")
        self.tree.column("品牌", width=110, minwidth=90)
        self.tree.heading("芯片组", text="芯片组")
        self.tree.column("芯片组", width=130, minwidth=100)
        self.tree.heading("系列", text="系列")
        self.tree.column("系列", width=130, minwidth=100)
        self.tree.heading("链接", text="下载链接")
        self.tree.column("链接", width=320, minwidth=250)
        self.tree.heading("备注", text="备注")
        self.tree.column("备注", width=150, minwidth=100)

        # 滚动条
        sy = ttk.Scrollbar(self.result_main_frame, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(self.result_main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

        self.tree.bind("<Double-1>", self.open_link)
        self.tree.tag_configure("model", font=('Microsoft YaHei',10,'bold'))

    # ==================== 核心展示（缩进+型号放大）====================
    def update_bios_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for item in self.bios_data:
            row = self.tree.insert("", "end", values=(
                item["model"],
                "  " + item["brand"],   # 缩进
                "  " + item["chipset"], # 缩进
                item["series"],
                item["link"],
                item.get("notes","")
            ), tags=("model",))

    def update_query_results(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        b = self.query_brand_var.get().lower()
        c = self.query_chipset_var.get().lower()
        s = self.query_series_var.get().lower()
        m = self.query_model_var.get().lower()

        for item in self.bios_data:
            if b != "全部" and item["brand"].lower() != b: continue
            if c and c not in item["chipset"].lower(): continue
            if s and s not in item["series"].lower(): continue
            if m and m not in item["model"].lower(): continue

            self.tree.insert("", "end", values=(
                item["model"],
                "  " + item["brand"],
                "  " + item["chipset"],
                item["series"],
                item["link"],
                item.get("notes","")
            ), tags=("model",))

        cnt = len(self.tree.get_children())
        self.status_var.set(f"查询完成，共 {cnt} 条")

    # ==================== 功能 ====================
    def add_bios_link(self):
        brand = self.brand_var.get()
        chipset = self.chipset_var.get()
        series = self.series_var.get()
        model = self.model_var.get()
        link = self.link_var.get()
        note = self.notes_text.get("1.0","end-1c")

        if not model or not brand:
            messagebox.showerror("错误","品牌、型号不能为空")
            return
        if not link.startswith("http"):
            messagebox.showerror("错误","链接必须以 http/https 开头")
            return

        self.bios_data.append({
            "brand":brand,"chipset":chipset,"series":series,"model":model,"link":link,"notes":note
        })
        self.save_data()
        self.reset_form()
        self.update_bios_list()
        self.status_var.set(f"已添加：{model}")

    def reset_form(self):
        self.brand_var.set("ASUS")
        self.chipset_var.set("")
        self.series_var.set("")
        self.model_var.set("")
        self.link_var.set("")
        self.notes_text.delete("1.0",tk.END)

    def search_bios_links(self):
        self.update_query_results()

    def open_link(self, e):
        sel = self.tree.selection()
        if not sel: return
        link = self.tree.item(sel[0])["values"][4]
        webbrowser.open(link)
        self.status_var.set(f"已打开：{link}")

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示","请先选择一项")
            return
        idx = self.tree.index(sel[0])
        data = self.bios_data[idx]

        win = tk.Toplevel(self.root)
        win.title("编辑")
        win.geometry("560x420")
        win.configure(bg="#f0f2f5")
        frm = ttk.Frame(win, padding=20)
        frm.pack(fill="both", expand=True)

        # 表单
        ttk.Label(frm, text="品牌：").grid(row=0,column=0,sticky="w",pady=6)
        br = tk.StringVar(value=data["brand"])
        ttk.Combobox(frm,textvariable=br,values=("ASUS","GIGABYTE","MSI","ASRock","Biostar","other")).grid(row=0,column=1,pady=6)

        ttk.Label(frm, text="芯片组：").grid(row=1,column=0,sticky="w",pady=6)
        cs = tk.StringVar(value=data["chipset"])
        ttk.Entry(frm,textvariable=cs).grid(row=1,column=1,pady=6)

        ttk.Label(frm, text="系列：").grid(row=2,column=0,sticky="w",pady=6)
        se = tk.StringVar(value=data["series"])
        ttk.Entry(frm,textvariable=se).grid(row=2,column=1,pady=6)

        ttk.Label(frm, text="型号：").grid(row=3,column=0,sticky="w",pady=6)
        mo = tk.StringVar(value=data["model"])
        ttk.Entry(frm,textvariable=mo).grid(row=3,column=1,pady=6)

        ttk.Label(frm, text="链接：").grid(row=4,column=0,sticky="w",pady=6)
        li = tk.StringVar(value=data["link"])
        ttk.Entry(frm,textvariable=li,width=40).grid(row=4,column=1,pady=6)

        ttk.Label(frm, text="备注：").grid(row=5,column=0,sticky="nw",pady=6)
        nt = scrolledtext.ScrolledText(frm,width=40,height=4)
        nt.grid(row=5,column=1,pady=6)
        nt.insert("1.0", data.get("notes",""))

        def save():
            if not li.get().startswith("http"):
                messagebox.showerror("错误","链接格式错误")
                return
            self.bios_data[idx] = {
                "brand":br.get(),"chipset":cs.get(),"series":se.get(),
                "model":mo.get(),"link":li.get(),"notes":nt.get("1.0","end-1c")
            }
            self.save_data()
            self.update_bios_list()
            win.destroy()

        ttk.Button(frm, text="保存", command=save).grid(row=6,column=1,pady=10,sticky="e")
        win.mainloop()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示","请选择要删除的项")
            return
        if messagebox.askyesno("确认","确定删除？"):
            idx = self.tree.index(sel[0])
            del self.bios_data[idx]
            self.save_data()
            self.update_bios_list()
            self.status_var.set("已删除")

    def export_links(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("文本","*.txt"),("JSON","*.json")])
        if not path: return
        try:
            if path.endswith(".json"):
                with open(path,"w",encoding="utf-8") as f:
                    json.dump(self.bios_data,f,indent=2,ensure_ascii=False)
            else:
                with open(path,"w",encoding="utf-8") as f:
                    f.write(f"BIOS链接导出 {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
                    for i,item in enumerate(self.bios_data,1):
                        f.write(f"{i}. {item['model']}\n品牌：{item['brand']}\n芯片组：{item['chipset']}\n链接：{item['link']}\n\n")
            messagebox.showinfo("成功", f"已导出到：\n{path}")
        except:
            messagebox.showerror("失败","导出出错")

if __name__ == "__main__":
    root = tk.Tk()
    app = BIOSManager(root)
    root.mainloop()