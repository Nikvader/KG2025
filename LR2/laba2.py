import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик изображений (Вариант 16)")
        self.root.geometry("1200x800")


        self.original_cv_image = None
        self.processed_cv_image = None
        self.last_morph_op = None 

        # Создание интерфейса

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.LabelFrame(main_frame, text="Панель управления", padding="10")
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.image_frame = ttk.Frame(main_frame, padding="10")
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Фрейм для исходного изображения (будет слева)
        original_display_frame = ttk.Frame(self.image_frame)
        original_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.original_label = ttk.Label(original_display_frame, text="Оригинал")
        self.original_label.pack(pady=5)
        self.original_canvas = tk.Canvas(original_display_frame, bg="lightgrey")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)

        # Фрейм для итогового изображения (будет справа)
        processed_display_frame = ttk.Frame(self.image_frame)
        processed_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.processed_label = ttk.Label(processed_display_frame, text="Результат")
        self.processed_label.pack(pady=5)
        self.processed_canvas = tk.Canvas(processed_display_frame, bg="lightgrey")
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления

        file_frame = ttk.Frame(controls_frame)
        file_frame.pack(fill=tk.X, pady=10)
        ttk.Button(file_frame, text="Открыть изображение", command=self.open_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Сохранить результат", command=self.save_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Сбросить изменения", command=self.reset_image).pack(fill=tk.X, pady=2)

        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)

        ##### Поэлементные операции и контрастирование
        contrast_frame = ttk.LabelFrame(controls_frame, text="Яркость и контраст", padding="10")
        contrast_frame.pack(fill=tk.X, pady=10)

        # Яркость
        brightness_label_frame = ttk.Frame(contrast_frame)
        brightness_label_frame.pack(fill=tk.X)
        ttk.Label(brightness_label_frame, text="Яркость:").pack(side=tk.LEFT)
        self.brightness_var = tk.StringVar(value="0") # Переменная для текста метки
        ttk.Label(brightness_label_frame, textvariable=self.brightness_var).pack(side=tk.RIGHT)
        
        self.brightness_scale = ttk.Scale(contrast_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.apply_filters)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill=tk.X, pady=(0, 5))

        # Контраст
        contrast_label_frame = ttk.Frame(contrast_frame)
        contrast_label_frame.pack(fill=tk.X)
        ttk.Label(contrast_label_frame, text="Контраст:").pack(side=tk.LEFT)
        self.contrast_var = tk.StringVar(value="1.00") 
        ttk.Label(contrast_label_frame, textvariable=self.contrast_var).pack(side=tk.RIGHT)

        self.contrast_scale = ttk.Scale(contrast_frame, from_=1, to=200, orient=tk.HORIZONTAL, command=self.apply_filters)
        self.contrast_scale.set(100) # 100 будет соответствовать контрасту 1.0
        self.contrast_scale.pack(fill=tk.X)

        ttk.Button(contrast_frame, text="Линейное контрастирование", command=self.apply_linear_contrast).pack(fill=tk.X, pady=10)
        
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)

        ###### Морфологическая обработка
        morph_frame = ttk.LabelFrame(controls_frame, text="Морфологическая обработка", padding="10")
        morph_frame.pack(fill=tk.X, pady=10)

        ttk.Label(morph_frame, text="Форма элемента:").pack(anchor='w')
        self.kernel_shape = tk.StringVar(value="rect")
        ttk.Radiobutton(morph_frame, text="Прямоугольник", variable=self.kernel_shape, value="rect").pack(anchor='w')
        ttk.Radiobutton(morph_frame, text="Крест", variable=self.kernel_shape, value="cross").pack(anchor='w')
        ttk.Radiobutton(morph_frame, text="Эллипс", variable=self.kernel_shape, value="ellipse").pack(anchor='w')

        kernel_label_frame = ttk.Frame(morph_frame)
        kernel_label_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(kernel_label_frame, text="Размер элемента:").pack(side=tk.LEFT)
        self.kernel_size_var = tk.StringVar(value="5x5")
        ttk.Label(kernel_label_frame, textvariable=self.kernel_size_var).pack(side=tk.RIGHT)

        self.kernel_size = tk.IntVar(value=5)
        self.kernel_scale = ttk.Scale(morph_frame, from_=1, to=21, orient=tk.HORIZONTAL, variable=self.kernel_size, command=self.update_kernel_size)
        self.kernel_scale.pack(fill=tk.X)

        ttk.Button(morph_frame, text="Эрозия (сужение)", command=lambda: self.apply_morphology("erode")).pack(fill=tk.X, pady=5)
        ttk.Button(morph_frame, text="Дилатация (расширение)", command=lambda: self.apply_morphology("dilate")).pack(fill=tk.X, pady=2)


    def open_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")])
        if not filepath:
            return
        
        self.original_cv_image = cv2.imread(filepath)
        if self.original_cv_image is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")
            return

        self.reset_image()

    def save_image(self):
        if self.processed_cv_image is None:
            messagebox.showwarning("Внимание", "Нет обработанного изображения для сохранения.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if not filepath:
            return
            
        try:
            cv2.imwrite(filepath, self.processed_cv_image)
            messagebox.showinfo("Успех", f"Изображение сохранено в {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {e}")

    def reset_image(self):
        if self.original_cv_image is None:
            return
        self.processed_cv_image = self.original_cv_image.copy()
        self.last_morph_op = None
        
        self.brightness_scale.set(0)
        self.contrast_scale.set(100)
        self.kernel_size.set(5)
        
        self.brightness_var.set("0")
        self.contrast_var.set("1.00")
        self.kernel_size_var.set("5x5")
        
        self.display_image(self.original_cv_image, self.original_canvas)
        self.display_image(self.processed_cv_image, self.processed_canvas)

    def display_image(self, cv_image, canvas):
        if cv_image is None:
            return

        img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        if canvas_w < 2 or canvas_h < 2:
            canvas_w, canvas_h = 500, 500
        
        img_pil.thumbnail((canvas_w, canvas_h))

        photo_image = ImageTk.PhotoImage(image=img_pil)
        
        canvas.delete("all")
        canvas.create_image(canvas_w / 2, canvas_h / 2, anchor=tk.CENTER, image=photo_image)
        canvas.image = photo_image

    def apply_filters(self, _=None):
        if self.original_cv_image is None:
            return
        
        temp_image = self.original_cv_image.copy()
        
        brightness = self.brightness_scale.get()
        # Преобразуем значение ползунка например [1, 200] в [0.01, 2.0]
        contrast = self.contrast_scale.get() / 100.0

        #Обновляем текстовые метки при движении ползунков
        self.brightness_var.set(f"{int(brightness)}")
        self.contrast_var.set(f"{contrast:.2f}")

        self.processed_cv_image = cv2.convertScaleAbs(temp_image, alpha=contrast, beta=brightness)
        
        if self.last_morph_op:
            self._execute_morph(self.last_morph_op)

        self.display_image(self.processed_cv_image, self.processed_canvas)

    def apply_linear_contrast(self):
        if self.processed_cv_image is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение.")
            return

        cv2.normalize(self.processed_cv_image, self.processed_cv_image, 0, 255, cv2.NORM_MINMAX)
        self.display_image(self.processed_cv_image, self.processed_canvas)

    def apply_morphology(self, op_name):
        if self.original_cv_image is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение.")
            return
        
        self.apply_filters()
        self.last_morph_op = op_name
        self._execute_morph(op_name)
        self.display_image(self.processed_cv_image, self.processed_canvas)
        
    def _execute_morph(self, op_name):
        k_size = self.kernel_size.get()
        if k_size % 2 == 0: k_size += 1

        k_shape_str = self.kernel_shape.get()
        shape_map = {"rect": cv2.MORPH_RECT, "cross": cv2.MORPH_CROSS, "ellipse": cv2.MORPH_ELLIPSE}
        k_shape = shape_map[k_shape_str]
        
        kernel = cv2.getStructuringElement(k_shape, (k_size, k_size))

        if op_name == "erode":
            self.processed_cv_image = cv2.erode(self.processed_cv_image, kernel, iterations=1)
        elif op_name == "dilate":
            self.processed_cv_image = cv2.dilate(self.processed_cv_image, kernel, iterations=1)

    def update_kernel_size(self, value):
        # Округляем значение и делаем его нечетным для корректной работы
        k_size = int(float(value))
        if k_size % 2 == 0: k_size = max(1, k_size - 1) 
        self.kernel_size.set(k_size)
        self.kernel_size_var.set(f"{k_size}x{k_size}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()