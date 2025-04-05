import os
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
from PyPDF2 import PdfReader, PdfWriter

# الحد الأقصى لحجم كل ملف (10 ميجابايت)
MAX_SIZE = 10 * 1024 * 1024


def split_pdf(file_path, progress_var, progress_bar, status_label):
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        # إنشاء مجلد على سطح المكتب لحفظ الملفات الناتجة
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_folder = os.path.join(desktop, "PDF_Split_Output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        part = 1
        current_writer = PdfWriter()
        pages_in_part = 0

        # تهيئة شريط التقدم
        progress_var.set(0)
        progress_bar.config(maximum=total_pages)

        # البدء في تقسيم الصفحات
        for i in range(total_pages):
            status_label.config(text=f"معالجة الصفحة {i + 1} من {total_pages}...")
            current_writer.add_page(reader.pages[i])
            pages_in_part += 1

            # حفظ مؤقتاً في الذاكرة للتحقق من الحجم
            temp_stream = io.BytesIO()
            current_writer.write(temp_stream)
            temp_size = temp_stream.tell()

            # إذا تجاوز الحجم الحد الأقصى وكان هناك أكثر من صفحة واحدة، نحفظ الجزء بدون الصفحة الأخيرة
            if temp_size > MAX_SIZE and pages_in_part > 1:
                writer_for_save = PdfWriter()
                start_index = i - pages_in_part + 1
                for j in range(pages_in_part - 1):
                    writer_for_save.add_page(reader.pages[start_index + j])
                save_path = os.path.join(output_folder, f"part_{part}.pdf")
                with open(save_path, "wb") as f_out:
                    writer_for_save.write(f_out)
                part += 1
                # إعادة تهيئة الكاتب مع الصفحة الحالية فقط
                current_writer = PdfWriter()
                current_writer.add_page(reader.pages[i])
                pages_in_part = 1

            progress_var.set(i + 1)
            progress_bar.update_idletasks()

        # حفظ الجزء الأخير إن وجد
        if pages_in_part > 0:
            save_path = os.path.join(output_folder, f"part_{part}.pdf")
            with open(save_path, "wb") as f_out:
                current_writer.write(f_out)

        status_label.config(text="اكتمل التقسيم بنجاح!")
        messagebox.showinfo("تم", f"تم تقسيم الملف بنجاح.\nتم إنشاء الملفات في:\n{output_folder}")
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء تقسيم الملف:\n{str(e)}")
        status_label.config(text="حدث خطأ أثناء التقسيم.")


def select_file(progress_var, progress_bar, status_label):
    file_path = filedialog.askopenfilename(
        title="اختر ملف PDF",
        filetypes=[("ملفات PDF", "*.pdf")]
    )
    if file_path:
        # تشغيل عملية التقسيم في خيط منفصل للحفاظ على استجابة الواجهة
        threading.Thread(target=split_pdf, args=(file_path, progress_var, progress_bar, status_label),
                         daemon=True).start()


# إنشاء نافذة التطبيق وتنسيق الواجهة
root = tk.Tk()
root.title("PDF Splitter - برنامج تقسيم ملفات PDF")
root.geometry("600x450")
root.configure(bg="#F0F8FF")  # خلفية فاتحة مناسبة

# تهيئة نمط ttk لواجهة أكثر احترافية
style = ttk.Style(root)
style.theme_use('clam')
style.configure("TButton", font=("Helvetica", 12), padding=6)
style.configure("TLabel", font=("Helvetica", 12), background="#F0F8FF")
style.configure("TProgressbar", thickness=20)

# عنوان البرنامج بخط مزخرف إن أمكن
try:
    title_font = font.Font(family="Segoe Script", size=26, weight="bold")
except Exception:
    title_font = font.Font(family="Helvetica", size=26, weight="bold")

title_label = tk.Label(root, text="PDF Splitter", bg="#F0F8FF", fg="#003366", font=title_font)
title_label.pack(pady=20)

# زر اختيار ملف PDF
select_button = ttk.Button(root, text="اختر ملف PDF",
                           command=lambda: select_file(progress_var, progress_bar, status_label))
select_button.pack(pady=10)

# شريط التقدم
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=20)

# تسمية حالة العملية
status_label = tk.Label(root, text="انتظر...", bg="#F0F8FF", fg="#003366", font=("Helvetica", 12))
status_label.pack(pady=10)

# تعليمات للمستخدم
instructions = tk.Label(root,
                        text="يقوم البرنامج بتقسيم ملف PDF إلى أجزاء بحيث يكون حجم كل جزء أقل من أو يساوي 10 ميجابايت.\nيتم إنشاء مجلد على سطح المكتب لحفظ الملفات الناتجة.",
                        bg="#F0F8FF", fg="#003366", font=("Helvetica", 12), justify="center")
instructions.pack(pady=10)

root.mainloop()
