import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 3")
        self.root.geometry("1200x800")

        self.scale = 20
        self.center_x = 0
        self.center_y = 0
        
        self.log_data = []
        self.execution_time = 0

        control_frame = tk.Frame(root, width=300, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(control_frame, text="Алгоритм:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        self.algo_var = tk.StringVar(value="step")
        
        algos = [
            ("Пошаговый", "step"),
            ("ЦДА (DDA)", "dda"),
            ("Брезенхем (Линия)", "bres_line"),
            ("Брезенхем (Окружность)", "bres_circle"),
            ("Кастла-Питвея", "castle"),
            ("Ву (Сглаживание)", "wu")
        ]
        
        for text, val in algos:
            tk.Radiobutton(control_frame, text=text, variable=self.algo_var, value=val, bg="#f0f0f0", command=self.update_inputs).pack(anchor="w")

        tk.Label(control_frame, text="\nКоординаты:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        
        input_frame = tk.Frame(control_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(input_frame, text="X1 (Xc):", bg="#f0f0f0").grid(row=0, column=0)
        self.entry_x1 = tk.Entry(input_frame, width=8)
        self.entry_x1.grid(row=0, column=1)
        self.entry_x1.insert(0, "-20")

        tk.Label(input_frame, text="Y1 (Yc):", bg="#f0f0f0").grid(row=0, column=2)
        self.entry_y1 = tk.Entry(input_frame, width=8)
        self.entry_y1.grid(row=0, column=3)
        self.entry_y1.insert(0, "-10")

        self.lbl_x2 = tk.Label(input_frame, text="X2 (R):", bg="#f0f0f0")
        self.lbl_x2.grid(row=1, column=0)
        self.entry_x2 = tk.Entry(input_frame, width=8)
        self.entry_x2.grid(row=1, column=1)
        self.entry_x2.insert(0, "20")

        self.lbl_y2 = tk.Label(input_frame, text="Y2:", bg="#f0f0f0")
        self.lbl_y2.grid(row=1, column=2)
        self.entry_y2 = tk.Entry(input_frame, width=8)
        self.entry_y2.grid(row=1, column=3)
        self.entry_y2.insert(0, "10")

        btn_frame = tk.Frame(control_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Построить", command=self.draw_figure, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Очистить", command=self.clear_canvas, width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="\nМасштаб:", bg="#f0f0f0").pack(anchor="w")
        self.scale_slider = tk.Scale(control_frame, from_=5, to=50, orient=tk.HORIZONTAL, command=self.on_scale_change)
        self.scale_slider.set(20)
        self.scale_slider.pack(fill=tk.X)
        
        tk.Label(control_frame, text="\nВремя:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        self.time_label = tk.Label(control_frame, text="0 ns", bg="#fff", relief=tk.SUNKEN, anchor="w")
        self.time_label.pack(fill=tk.X)

        tk.Label(control_frame, text="\nВычисления:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_text = tk.Text(control_frame, height=20, width=35, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(root, bg="white")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.update_inputs()

    def update_inputs(self):
        mode = self.algo_var.get()
        if mode == "bres_circle":
            self.lbl_x2.config(text="R:")
            self.lbl_y2.grid_remove()
            self.entry_y2.grid_remove()
        else:
            self.lbl_x2.config(text="X2:")
            self.lbl_y2.grid()
            self.entry_y2.grid()

    def on_resize(self, event):
        self.center_x = event.width // 2
        self.center_y = event.height // 2
        self.draw_grid()

    def on_scale_change(self, val):
        self.scale = int(val)
        self.draw_grid()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.log_text.delete(1.0, tk.END)
        self.time_label.config(text="0 ns")
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("grid_line")
        self.canvas.delete("grid_text")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1 or h <= 1: return

        cx, cy = self.center_x, self.center_y
        step = self.scale

        for i, x in enumerate(range(cx, w, step)):
            color = "#aaa" if i == 0 else "#ddd"
            width = 2 if i == 0 else 1
            self.canvas.create_line(x, 0, x, h, fill=color, width=width, tags="grid_line")
            if i != 0: self.canvas.create_text(x + 2, cy + 2, text=str(i), anchor="nw", font=("Arial", 8), tags="grid_text")

        for i, x in enumerate(range(cx, 0, -step)):
            if i == 0: continue
            self.canvas.create_line(x, 0, x, h, fill="#ddd", tags="grid_line")
            self.canvas.create_text(x + 2, cy + 2, text=str(-i), anchor="nw", font=("Arial", 8), tags="grid_text")

        for i, y in enumerate(range(cy, h, step)):
            color = "#aaa" if i == 0 else "#ddd"
            width = 2 if i == 0 else 1
            self.canvas.create_line(0, y, w, y, fill=color, width=width, tags="grid_line")
            if i != 0: self.canvas.create_text(cx + 2, y + 2, text=str(-i), anchor="nw", font=("Arial", 8), tags="grid_text")

        for i, y in enumerate(range(cy, 0, -step)):
            if i == 0: continue
            self.canvas.create_line(0, y, w, y, fill="#ddd", tags="grid_line")
            self.canvas.create_text(cx + 2, y + 2, text=str(i), anchor="nw", font=("Arial", 8), tags="grid_text")
            
        self.canvas.create_text(w-20, cy-15, text="X", font=("Arial", 12, "bold"), fill="black", tags="grid_text")
        self.canvas.create_text(cx+10, 10, text="Y", font=("Arial", 12, "bold"), fill="black", tags="grid_text")

    def plot_pixel(self, x, y, color="#FF5722", alpha=1.0):
        if alpha < 0.05:
            return 
        
        cx, cy = self.center_x, self.center_y
        s = self.scale
        
        screen_x = cx + x * s
        screen_y = cy - y * s
        
        fill_color = color
        if alpha < 1.0:
            if alpha < 0: alpha = 0.0
            if alpha > 1: alpha = 1.0
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                r_new = int(r * alpha + 255 * (1.0 - alpha))
                g_new = int(g * alpha + 255 * (1.0 - alpha))
                b_new = int(b * alpha + 255 * (1.0 - alpha))
                
                fill_color = f"#{r_new:02x}{g_new:02x}{b_new:02x}"
            except:
                pass 

        self.canvas.create_rectangle(
            screen_x - s/2 + 1, screen_y - s/2 + 1,
            screen_x + s/2 - 1, screen_y + s/2 - 1,
            fill=fill_color, outline=""
        )

    def get_step_by_step(self, x1, y1, x2, y2):
        points = []
        log = ["--- Пошаговый ---"]
        
        if x1 == x2 and y1 == y2:
            points.append((x1, y1, 1.0))
            return points, log

        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        log.append(f"dx={dx}, dy={dy}, steps={steps}")
        
        if abs(dx) >= abs(dy):
            m = dy / dx if dx != 0 else 0
            b = y1 - m * x1
            log.append(f"Основная X. m={m:.2f}, b={b:.2f}")
            step_dir = 1 if x2 > x1 else -1
            for x in range(x1, x2 + step_dir, step_dir):
                y = m * x + b
                y_round = round(y)
                points.append((x, y_round, 1.0))
                log.append(f"x={x}, y={y:.2f} -> {y_round}")
        else:
            m = dx / dy if dy != 0 else 0
            b = x1 - m * y1
            log.append(f"Основная Y. 1/m={m:.2f}, b={b:.2f}")
            step_dir = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step_dir, step_dir):
                x = m * y + b
                x_round = round(x)
                points.append((x_round, y, 1.0))
                log.append(f"y={y}, x={x:.2f} -> {x_round}")
        return points, log

    def get_dda(self, x1, y1, x2, y2):
        points = []
        log = ["--- ЦДА ---"]
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        log.append(f"dx={dx}, dy={dy}, steps={steps}")
        
        if steps == 0:
            points.append((x1, y1, 1.0))
            return points, log

        x_inc = dx / steps
        y_inc = dy / steps
        log.append(f"inc_x={x_inc:.2f}, inc_y={y_inc:.2f}")
        
        x = x1
        y = y1
        for i in range(steps + 1):
            x_plot = round(x)
            y_plot = round(y)
            points.append((x_plot, y_plot, 1.0))
            log.append(f"i={i}: x={x:.2f}, y={y:.2f}")
            x += x_inc
            y += y_inc
        return points, log

    def get_bresenham_line(self, x1, y1, x2, y2):
        points = []
        log = ["--- Брезенхем (Линия) ---"]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        log.append(f"dx={dx}, dy={dy}, sx={sx}, sy={sy}, err={err}")
        
        while True:
            points.append((x1, y1, 1.0))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            log_line = f"Pt({x1},{y1}) e2={e2}: "
            if e2 > -dy:
                err -= dy
                x1 += sx
                log_line += "Step X "
            if e2 < dx:
                err += dx
                y1 += sy
                log_line += "Step Y"
            log_line += f" -> err={err}"
            log.append(log_line)
        return points, log

    def get_bresenham_circle(self, xc, yc, r):
        points = []
        log = ["--- Брезенхем (Круг) ---"]
        log.append(f"C=({xc},{yc}), R={r}")
        x = 0
        y = r
        d = 3 - 2 * r
        log.append(f"Start: x=0, y={r}, d={d}")
        
        def add_octants(cx, cy, x, y, pts):
            sym_pts = [
                (cx+x, cy+y, 1.0), (cx-x, cy+y, 1.0), (cx+x, cy-y, 1.0), (cx-x, cy-y, 1.0),
                (cx+y, cy+x, 1.0), (cx-y, cy+x, 1.0), (cx+y, cy-x, 1.0), (cx-y, cy-x, 1.0)
            ]
            pts.extend(sym_pts)
            return sym_pts

        while y >= x:
            add_octants(xc, yc, x, y, points)
            log.append(f"x={x}, y={y}, d={d}")
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
        return points, log


    def get_castle_pitteway(self, x1, y1, x2, y2):
        points = []
        log = ["--- Кастла-Питвея ---"]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x2 > x1 else -1
        sy = 1 if y2 > y1 else -1
        
        steep = dy > dx
        if steep:
            dx, dy = dy, dx
            log.append("Крутая линия: логическая ось X теперь вдоль Y")

        if dy == 0:
            log.append("Прямая линия")
            cx, cy = x1, y1
            for _ in range(dx + 1):
                points.append((cx, cy, 1.0))
                if steep: cy += sy
                else:     cx += sx
            return points, log

        gcd_val = math.gcd(dx, dy)
        major_axis_steps = dx // gcd_val
        minor_axis_steps = dy // gcd_val
        
        log.append(f"dx={dx}, dy={dy}, НОД={gcd_val}. Паттерн для: {major_axis_steps}x{minor_axis_steps}")


        count_s = major_axis_steps - minor_axis_steps 
        count_d = minor_axis_steps                

        m1 = [0] 
        m2 = [1]
        
        log.append(f"Старт алгоритма: s-шагов={count_s}, d-шагов={count_d}")

        while count_s != count_d:
            if count_s > count_d:
                count_s = count_s - count_d
                m2 = m1 + m2[::-1]
            else:
                count_d = count_d - count_s
                m1 = m2 + m1[::-1]
        
        final_pattern = m2 + m1[::-1]
        
        log.append(f"Сгенерированный паттерн (0=Прямо, 1=Диаг): {final_pattern}")
        
        cx, cy = x1, y1
        points.append((cx, cy, 1.0)) 
        
        for _ in range(gcd_val):
            for step_type in final_pattern:
                if steep:
                    cy += sy
                else:
                    cx += sx
                
                if step_type == 1:
                    if steep:
                        cx += sx
                    else:
                        cy += sy
                
                points.append((cx, cy, 1.0))
        
        return points, log

    def get_wu_line(self, x1, y1, x2, y2):
        points = []
        log = ["--- Алгоритм Ву ---"]
        
        def ipart(x): return math.floor(x)
        def round_func(x): return math.floor(x + 0.5)
        def fpart(x): return x - math.floor(x)
        def rfpart(x): return 1 - fpart(x)  
        dx = x2 - x1
        dy = y2 - y1
        
        steep = abs(dy) > abs(dx)
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            dx, dy = dy, dx
            
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            
        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1.0
        
        xend = round_func(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)
        
        if steep:
            points.append((ypxl1, xpxl1, rfpart(yend) * xgap))
            points.append((ypxl1 + 1, xpxl1, fpart(yend) * xgap))
        else:
            points.append((xpxl1, ypxl1, rfpart(yend) * xgap))
            points.append((xpxl1, ypxl1 + 1, fpart(yend) * xgap))
            
        intery = yend + gradient
        
        xpxl2 = round_func(x2)
        
        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                points.append((ipart(intery), x, rfpart(intery)))
                points.append((ipart(intery) + 1, x, fpart(intery)))
            else:
                points.append((x, ipart(intery), rfpart(intery)))
                points.append((x, ipart(intery) + 1, fpart(intery)))
            intery += gradient
            
        xend = round_func(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)
        
        if steep:
            points.append((ypxl2, xpxl2, rfpart(yend) * xgap))
            points.append((ypxl2 + 1, xpxl2, fpart(yend) * xgap))
        else:
            points.append((xpxl2, ypxl2, rfpart(yend) * xgap))
            points.append((xpxl2, ypxl2 + 1, fpart(yend) * xgap))
            
        return points, log
    
    def draw_figure(self):
        self.draw_grid()
        self.log_text.delete(1.0, tk.END)
        
        try:
            x1 = int(self.entry_x1.get())
            y1 = int(self.entry_y1.get())
            
            algo = self.algo_var.get()
            
            points = []
            log = []
            
            start_time = time.perf_counter_ns()
            
            if algo == "bres_circle":
                r = int(self.entry_x2.get())
                if r < 0: raise ValueError("R < 0")
                points, log = self.get_bresenham_circle(x1, y1, r)
            else:
                x2 = int(self.entry_x2.get())
                y2 = int(self.entry_y2.get())
                
                if algo == "step":
                    points, log = self.get_step_by_step(x1, y1, x2, y2)
                elif algo == "dda":
                    points, log = self.get_dda(x1, y1, x2, y2)
                elif algo == "bres_line":
                    points, log = self.get_bresenham_line(x1, y1, x2, y2)
                elif algo == "castle":
                    points, log = self.get_castle_pitteway(x1, y1, x2, y2)
                elif algo == "wu":
                    points, log = self.get_wu_line(x1, y1, x2, y2)
            
            end_time = time.perf_counter_ns()
            duration = end_time - start_time
            
            if duration > 1000000:
                time_str = f"{duration / 1000000:.2f} ms"
            elif duration > 1000:
                time_str = f"{duration / 1000:.2f} µs"
            else:
                time_str = f"{duration} ns"
            
            self.time_label.config(text=time_str)
            self.log_text.insert(tk.END, "\n".join(log))
            
            for p in points:
                if len(p) == 3:
                    px, py, alpha = p
                else:
                    px, py = p
                    alpha = 1.0
                    
                self.plot_pixel(px, py, color="#FF5722", alpha=alpha)
            
            self.plot_pixel(x1, y1, color="green")
            if algo != "bres_circle":
                x2 = int(self.entry_x2.get())
                y2 = int(self.entry_y2.get())
                self.plot_pixel(x2, y2, color="red")    
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные")

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()
