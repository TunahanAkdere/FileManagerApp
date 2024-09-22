import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import datetime
import send2trash
from PIL import Image, ImageTk

class DosyaYoneticisi:
    def __init__(self, ana_pencere):
        self.ana_pencere = ana_pencere
        
        # Dil ayarlarını başlangıçta tanımlayalım
        self.dil = "tr"  # Varsayılan dil Türkçe
        self.dil_sozlugu = {
            "tr": {
                "title": "Gelişmiş Dosya Yöneticisi",
                "back": "Geri",
                "forward": "İleri",
                "up": "Yukarı",
                "refresh": "Yenile",
                "search": "Ara",
                "new_folder": "Yeni Klasör",
                "new_file": "Yeni Dosya",
                "rename": "Yeniden Adlandır",
                "delete": "Kalıcı Sil",
                "recycle": "Geri Dönüşüme Gönder",
                "change_language": "English"
            },
            "en": {
                "title": "Advanced File Manager",
                "back": "Back",
                "forward": "Forward",
                "up": "Up",
                "refresh": "Refresh",
                "search": "Search",
                "new_folder": "New Folder",
                "new_file": "New File",
                "rename": "Rename",
                "delete": "Delete Permanently",
                "recycle": "Send to Recycle Bin",
                "change_language": "Türkçe"
            }
        }

        self.ana_pencere.title(self.dil_sozlugu[self.dil]["title"])
        self.ana_pencere.geometry("1200x800")
        self.ana_pencere.configure(bg="#f5f5f5")

        self.mevcut_dizin = os.getcwd()

        self.stil = ttk.Style()
        self.stil.theme_use("clam")
        self.stil.configure("TButton", padding=10, relief="flat", background="#4CAF50", foreground="white", font=("Segoe UI", 10))
        self.stil.map("TButton", background=[("active", "#45a049")])

        self.ana_frame = tk.Frame(self.ana_pencere, bg="#f5f5f5")
        self.ana_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.ust_frame = tk.Frame(self.ana_frame, bg="#f5f5f5")
        self.ust_frame.pack(fill=tk.X, pady=(0, 20))

        self.buton_frame = tk.Frame(self.ust_frame, bg="#f5f5f5")
        self.buton_frame.pack(side=tk.LEFT)

        butonlar = [
            ("back", "geri_git", "⬅️"),
            ("forward", "ileri_git", "➡️"),
            ("up", "yukari_git", "⬆️"),
            ("refresh", "yenile", "🔄"),
            ("search", "dosya_ara", "🔍")
        ]

        for buton_adi, komut, ikon in butonlar:
            buton = ttk.Button(self.buton_frame, text=f"{ikon} {self.dil_sozlugu[self.dil][buton_adi]}", command=getattr(self, komut))
            buton.pack(side=tk.LEFT, padx=(0, 10))

        self.adres_frame = tk.Frame(self.ust_frame, bg="#f5f5f5")
        self.adres_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.adres_cubugu = tk.Entry(self.adres_frame, font=("Segoe UI", 12), bg="white", fg="#333")
        self.adres_cubugu.pack(fill=tk.X, expand=True)
        self.adres_cubugu.bind("<Return>", self.adrese_git)

        self.dil_degistir_buton = ttk.Button(self.ust_frame, text=self.dil_sozlugu[self.dil]["change_language"], command=self.dil_degistir)
        self.dil_degistir_buton.pack(side=tk.RIGHT, padx=(10, 0))

        self.agac_frame = tk.Frame(self.ana_frame, bg="#f5f5f5")
        self.agac_frame.pack(fill=tk.BOTH, expand=True)

        self.agac = ttk.Treeview(self.agac_frame, style="Treeview")
        self.agac.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.agac_frame, orient="vertical", command=self.agac.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.agac.configure(yscrollcommand=self.scrollbar.set)

        self.agac["columns"] = ("boyut", "tarih")
        self.agac.heading("#0", text="Ad")
        self.agac.heading("boyut", text="Boyut")
        self.agac.heading("tarih", text="Değiştirilme Tarihi")

        self.agac.bind("<Double-1>", self.oge_ac)
        self.agac.bind("<Button-3>", self.sag_tiklama_menu)
        self.agac.bind("<Button-3>", self.bos_alan_sag_tiklama_menu, add='+')

        self.durum_cubugu = tk.Label(self.ana_pencere, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 10), bg="#e0e0e0", fg="#333")
        self.durum_cubugu.pack(side=tk.BOTTOM, fill=tk.X)

        self.ana_pencere.bind("<Configure>", self.pencere_yeniden_boyutlandir)

        self.gecmis = []
        self.gecmis_indeksi = -1

        self.metinleri_guncelle()
        self.yenile()

    def pencere_yeniden_boyutlandir(self, event):
        # Pencere boyutu değiştiğinde çağrılır
        self.agac.column("#0", width=int(event.width * 0.4))
        self.agac.column("boyut", width=int(event.width * 0.2))
        self.agac.column("tarih", width=int(event.width * 0.3))

    def yenile(self):
        for i in self.agac.get_children():
            self.agac.delete(i)

        self.adres_cubugu.delete(0, tk.END)
        self.adres_cubugu.insert(0, self.mevcut_dizin)

        try:
            for oge in os.listdir(self.mevcut_dizin):
                tam_yol = os.path.join(self.mevcut_dizin, oge)
                boyut = os.path.getsize(tam_yol)
                tarih = os.path.getmtime(tam_yol)
                tarih_str = datetime.datetime.fromtimestamp(tarih).strftime('%Y-%m-%d %H:%M:%S')
                if os.path.isdir(tam_yol):
                    self.agac.insert("", "end", text=oge, values=(self.boyut_formatla(boyut), tarih_str), open=False, tags=("klasor",))
                else:
                    self.agac.insert("", "end", text=oge, values=(self.boyut_formatla(boyut), tarih_str), tags=("dosya",))

            self.agac.tag_configure("klasor", foreground="#1565C0", font=("Segoe UI", 10, "bold"))
            self.agac.tag_configure("dosya", foreground="#2E7D32", font=("Segoe UI", 10))

            self.durum_cubugu.config(text=f"{len(os.listdir(self.mevcut_dizin))} öğe")
        except PermissionError:
            messagebox.showerror("Hata", "Bu dizine erişim izniniz yok!")

    def boyut_formatla(self, boyut):
        for birim in ['B', 'KB', 'MB', 'GB', 'TB']:
            if boyut < 1024.0:
                return f"{boyut:.2f} {birim}"
            boyut /= 1024.0

    def oge_ac(self, event):
        secili = self.agac.focus()
        if secili:
            oge = self.agac.item(secili, "text")
            tam_yol = os.path.join(self.mevcut_dizin, oge)
            if os.path.isdir(tam_yol):
                self.gecmise_ekle(self.mevcut_dizin)
                self.mevcut_dizin = tam_yol
                self.yenile()
            else:
                os.startfile(tam_yol)

    def gecmise_ekle(self, dizin):
        self.gecmis = self.gecmis[:self.gecmis_indeksi + 1]
        self.gecmis.append(dizin)
        self.gecmis_indeksi += 1

    def geri_git(self):
        if self.gecmis_indeksi > 0:
            self.gecmis_indeksi -= 1
            self.mevcut_dizin = self.gecmis[self.gecmis_indeksi]
            self.yenile()

    def ileri_git(self):
        if self.gecmis_indeksi < len(self.gecmis) - 1:
            self.gecmis_indeksi += 1
            self.mevcut_dizin = self.gecmis[self.gecmis_indeksi]
            self.yenile()

    def yukari_git(self):
        ust_dizin = os.path.dirname(self.mevcut_dizin)
        if ust_dizin != self.mevcut_dizin:
            self.gecmise_ekle(self.mevcut_dizin)
            self.mevcut_dizin = ust_dizin
            self.yenile()

    def adrese_git(self, event):
        yeni_adres = self.adres_cubugu.get()
        if os.path.exists(yeni_adres) and os.path.isdir(yeni_adres):
            self.gecmise_ekle(self.mevcut_dizin)
            self.mevcut_dizin = yeni_adres
            self.yenile()
        else:
            messagebox.showerror("Hata", "Geçersiz dizin yolu!")

    def dosya_ara(self):
        arama_penceresi = tk.Toplevel(self.ana_pencere)
        arama_penceresi.title("Dosya Ara")
        arama_penceresi.geometry("500x150")
        arama_penceresi.configure(bg="#f5f5f5")

        tk.Label(arama_penceresi, text="Dosya adı:", font=("Segoe UI", 12), bg="#f5f5f5").pack(pady=10)
        arama_girisi = tk.Entry(arama_penceresi, width=50, font=("Segoe UI", 10))
        arama_girisi.pack(pady=10)

        def ara():
            aranan = arama_girisi.get()
            bulunanlar = []
            for root, dirs, files in os.walk(self.mevcut_dizin):
                for file in files:
                    if aranan.lower() in file.lower():
                        bulunanlar.append(os.path.join(root, file))
            
            if bulunanlar:
                sonuc_penceresi = tk.Toplevel(self.ana_pencere)
                sonuc_penceresi.title("Arama Sonuçları")
                sonuc_penceresi.geometry("800x600")
                
                sonuc_listesi = tk.Listbox(sonuc_penceresi, width=100, font=("Segoe UI", 10))
                sonuc_listesi.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
                
                for dosya in bulunanlar:
                    sonuc_listesi.insert(tk.END, dosya)
                
                def dosya_ac(event):
                    secili_index = sonuc_listesi.curselection()
                    if secili_index:
                        secili_dosya = sonuc_listesi.get(secili_index[0])
                        os.startfile(secili_dosya)
                
                sonuc_listesi.bind('<Double-1>', dosya_ac)
            else:
                messagebox.showinfo("Sonuç", "Dosya bulunamadı.")
            
            arama_penceresi.destroy()

        tk.Button(arama_penceresi, text="Ara", command=ara, font=("Segoe UI", 10), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=10)

    def sag_tiklama_menu(self, event):
        secili = self.agac.identify_row(event.y)
        if secili:
            self.agac.selection_set(secili)
            menu = tk.Menu(self.ana_pencere, tearoff=0)
            menu.add_command(label=self.dil_sozlugu[self.dil]["rename"], command=self.isim_degistir)
            menu.add_command(label=self.dil_sozlugu[self.dil]["delete"], command=self.kalici_sil)
            menu.add_command(label=self.dil_sozlugu[self.dil]["recycle"], command=self.geri_donusum_kutusuna_gonder)
            menu.post(event.x_root, event.y_root)

    def bos_alan_sag_tiklama_menu(self, event):
        if not self.agac.identify_row(event.y):
            menu = tk.Menu(self.ana_pencere, tearoff=0)
            menu.add_command(label=self.dil_sozlugu[self.dil]["new_folder"], command=self.yeni_klasor_olustur)
            menu.add_command(label=self.dil_sozlugu[self.dil]["new_file"], command=self.yeni_dosya_olustur)
            menu.post(event.x_root, event.y_root)

    def yeni_klasor_olustur(self):
        yeni_klasor_adi = simpledialog.askstring("Yeni Klasör", "Yeni klasör adı:")
        if yeni_klasor_adi:
            yeni_klasor_yolu = os.path.join(self.mevcut_dizin, yeni_klasor_adi)
            try:
                os.mkdir(yeni_klasor_yolu)
                self.yenile()
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör oluşturma başarısız: {str(e)}")

    def isim_degistir(self):
        secili = self.agac.selection()
        if secili:
            eski_isim = self.agac.item(secili)['text']
            eski_yol = os.path.join(self.mevcut_dizin, eski_isim)
            yeni_isim = simpledialog.askstring("İsim Değiştir", "Yeni isim:", initialvalue=eski_isim)
            if yeni_isim and yeni_isim != eski_isim:
                yeni_yol = os.path.join(self.mevcut_dizin, yeni_isim)
                try:
                    os.rename(eski_yol, yeni_yol)
                    self.yenile()
                except Exception as e:
                    messagebox.showerror("Hata", f"İsim değiştirme başarısız: {str(e)}")

    def kalici_sil(self):
        secili = self.agac.selection()
        if secili:
            oge = self.agac.item(secili)['text']
            tam_yol = os.path.join(self.mevcut_dizin, oge)
            if messagebox.askyesno("Kalıcı Silme", f"{oge} kalıcı olarak silinecek. Emin misiniz?"):
                try:
                    if os.path.isfile(tam_yol):
                        os.remove(tam_yol)
                    elif os.path.isdir(tam_yol):
                        import shutil
                        shutil.rmtree(tam_yol)
                    self.yenile()
                except Exception as e:
                    messagebox.showerror("Hata", f"Silme işlemi başarısız: {str(e)}")

    def geri_donusum_kutusuna_gonder(self):
        secili = self.agac.selection()
        if secili:
            oge = self.agac.item(secili)['text']
            tam_yol = os.path.join(self.mevcut_dizin, oge)
            try:
                send2trash.send2trash(tam_yol)
                self.yenile()
            except Exception as e:
                messagebox.showerror("Hata", f"Geri dönüşüm kutusuna gönderme başarısız: {str(e)}")

    def yeni_dosya_olustur(self):
        yeni_dosya_adi = simpledialog.askstring("Yeni Dosya", "Yeni dosya adı:")
        if yeni_dosya_adi:
            yeni_dosya_yolu = os.path.join(self.mevcut_dizin, yeni_dosya_adi)
            try:
                with open(yeni_dosya_yolu, 'w') as f:
                    pass  # Boş bir dosya oluştur
                self.yenile()
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya oluşturma başarısız: {str(e)}")

    def metinleri_guncelle(self):
        self.ana_pencere.title(self.dil_sozlugu[self.dil]["title"])
        
        butonlar = [
            ("back", "geri_git", "⬅️"),
            ("forward", "ileri_git", "➡️"),
            ("up", "yukari_git", "⬆️"),
            ("refresh", "yenile", "🔄"),
            ("search", "dosya_ara", "🔍")
        ]

        for i, (buton_adi, komut, ikon) in enumerate(butonlar):
            self.buton_frame.winfo_children()[i].config(text=f"{ikon} {self.dil_sozlugu[self.dil][buton_adi]}")

        self.dil_degistir_buton.config(text=self.dil_sozlugu[self.dil]["change_language"])

    def dil_degistir(self):
        self.dil = "en" if self.dil == "tr" else "tr"
        self.metinleri_guncelle()
        self.yenile()

if __name__ == "__main__":
    root = tk.Tk()
    app = DosyaYoneticisi(root)
    root.mainloop()
