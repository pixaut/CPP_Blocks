import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import tempfile
from block_system import BlockSystem
from code_generator import CodeGenerator

class CppBlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("C++ Block Programming")
        self.root.geometry("1200x800")
        
        # Инициализация компонентов
        self.block_system = BlockSystem()
        self.code_generator = CodeGenerator()
        
        # Переменные для хранения блоков
        self.blocks = []
        self.selected_block = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Меню Run
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Generate C++", command=self.generate_cpp)
        run_menu.add_command(label="Compile & Run", command=self.compile_and_run)
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - палитра блоков
        self.setup_blocks_palette(main_frame)
        
        # Центральная панель - рабочая область
        self.setup_workspace(main_frame)
        
        # Правая панель - код и вывод
        self.setup_code_panel(main_frame)
        
    def setup_blocks_palette(self, parent):
        # Фрейм для палитры блоков
        palette_frame = ttk.LabelFrame(parent, text="Блоки", width=200)
        palette_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        palette_frame.pack_propagate(False)
        
        # Категории блоков
        categories = {
            "Переменные": ["variable"],
            "Операторы": ["operator"], 
            "Функции": ["function"],
            "Кастомные функции": ["custom_function"],
            "Управление": ["return"]
        }
        
        for category, blocks in categories.items():
            cat_frame = ttk.LabelFrame(palette_frame, text=category)
            cat_frame.pack(fill=tk.X, padx=5, pady=2)
            
            for block_type in blocks:
                btn_text = {
                    "variable": "Переменная",
                    "operator": "Оператор",
                    "function": "Функция",
                    "custom_function": "Кастомная функция",
                    "return": "Return"
                }.get(block_type, block_type)
                
                btn = tk.Button(cat_frame, text=btn_text, 
                              command=lambda bt=block_type: self.add_block(bt),
                              width=15, height=2)
                btn.pack(fill=tk.X, padx=2, pady=1)
                
    def setup_workspace(self, parent):
        # Фрейм для рабочей области
        workspace_frame = ttk.LabelFrame(parent, text="Рабочая область")
        workspace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Canvas для drag-and-drop блоков
        self.canvas = tk.Canvas(workspace_frame, bg="white", 
                               scrollregion=(0, 0, 1000, 1000))
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(workspace_frame, orient=tk.VERTICAL, 
                                   command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(workspace_frame, orient=tk.HORIZONTAL, 
                                   command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set,
                             xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Привязка событий для drag-and-drop
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # ПКМ
        
        # Переменные для связей
        self.block_connections = {}  # Словарь связей между блоками
        self.connection_mode = False  # Режим создания связи
        self.source_block = None  # Блок-источник для связи
        
    def setup_code_panel(self, parent):
        # Фрейм для панели кода
        code_frame = ttk.LabelFrame(parent, text="C++ Код", width=300)
        code_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        code_frame.pack_propagate(False)
        
        # Текстовое поле для отображения сгенерированного кода
        self.code_text = tk.Text(code_frame, wrap=tk.WORD, font=("Consolas", 10))
        code_scrollbar = ttk.Scrollbar(code_frame, orient=tk.VERTICAL, 
                                      command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=code_scrollbar.set)
        
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки для генерации и выполнения
        button_frame = ttk.Frame(code_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Генерировать код", 
                  command=self.generate_cpp).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Выполнить", 
                  command=self.compile_and_run).pack(side=tk.LEFT, padx=2)
        
        # Область вывода
        output_frame = ttk.LabelFrame(code_frame, text="Вывод")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, 
                                  font=("Consolas", 9), height=8)
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, 
                                        command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_block(self, block_type):
        """Добавляет новый блок в рабочую область"""
        block = self.block_system.create_block(block_type)
        if block:
            self.blocks.append(block)
            self.draw_block(block)
            
    def draw_block(self, block):
        """Отрисовывает блок на canvas"""
        x, y = block.get_position()
        width, height = block.get_size()
        
        # Создаем прямоугольник для блока
        rect_id = self.canvas.create_rectangle(x, y, x + width, y + height,
                                             fill=block.get_color(), 
                                             outline="black", width=2)
        
        # Для кастомных функций добавляем дополнительную рамку
        if block.block_type == "custom_function":
            # Внешняя рамка для области функции
            outer_rect_id = self.canvas.create_rectangle(x-5, y-5, x + width+5, y + height+5,
                                                        fill="", outline="purple", width=3)
            block.set_outer_rect_id(outer_rect_id)
        
        # Добавляем текст с переносом строк
        text = block.get_text()
        # Разбиваем длинный текст на строки
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= 25:  # Примерно 25 символов на строку
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Создаем текст с переносом
        text_lines = "\n".join(lines)
        text_id = self.canvas.create_text(x + width//2, y + height//2,
                                        text=text_lines,
                                        font=("Arial", 9, "bold"),
                                        justify=tk.CENTER)
        
        # Сохраняем ID элементов в блоке
        block.set_canvas_ids(rect_id, text_id)
        
    def on_canvas_click(self, event):
        """Обработка клика по canvas"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.connection_mode:
            # Режим создания связи
            self.handle_connection_click(x, y)
            return
        
        # Ищем блок под курсором
        for block in self.blocks:
            bx, by = block.get_position()
            bw, bh = block.get_size()
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.selected_block = block
                self.drag_start_x = x - bx
                self.drag_start_y = y - by
                break
                
    def handle_connection_click(self, x, y):
        """Обрабатывает клик в режиме создания связи"""
        # Ищем блок под курсором
        target_block = None
        for block in self.blocks:
            bx, by = block.get_position()
            bw, bh = block.get_size()
            if bx <= x <= bx + bw and by <= y <= by + bh:
                target_block = block
                break
                
        if target_block and target_block != self.source_block:
            # Создаем связь
            self.create_connection(self.source_block, target_block)
            
        # Выходим из режима связи
        self.connection_mode = False
        self.source_block = None
        self.canvas.config(cursor="")
        self.update_status("")
        
    def create_connection(self, source_block, target_block):
        """Создает связь между блоками"""
        self.block_connections[source_block] = target_block
        self.redraw_connections()
        
    def redraw_connections(self):
        """Перерисовывает все связи между блоками"""
        # Удаляем старые линии связей
        self.canvas.delete("connection")
        
        # Рисуем новые связи
        for source, target in self.block_connections.items():
            self.draw_connection(source, target)
            
    def draw_connection(self, source_block, target_block):
        """Рисует связь между двумя блоками"""
        sx, sy = source_block.get_position()
        sw, sh = source_block.get_size()
        tx, ty = target_block.get_position()
        tw, th = target_block.get_size()
        
        # Координаты точек соединения
        source_x = sx + sw
        source_y = sy + sh // 2
        target_x = tx
        target_y = ty + th // 2
        
        # Рисуем линию связи
        self.canvas.create_line(source_x, source_y, target_x, target_y,
                               fill="blue", width=2, tags="connection")
        
        # Рисуем стрелку
        arrow_size = 8
        angle = 0  # Горизонтальная стрелка
        
        # Координаты стрелки
        arrow_x1 = target_x - arrow_size
        arrow_y1 = target_y - arrow_size // 2
        arrow_x2 = target_x - arrow_size
        arrow_y2 = target_y + arrow_size // 2
        
        self.canvas.create_polygon(target_x, target_y, arrow_x1, arrow_y1, arrow_x2, arrow_y2,
                                  fill="blue", outline="blue", tags="connection")
                
    def on_canvas_drag(self, event):
        """Обработка перетаскивания блока"""
        if self.selected_block:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            new_x = x - self.drag_start_x
            new_y = y - self.drag_start_y
            
            # Обновляем позицию блока
            self.selected_block.set_position(new_x, new_y)
            
            # Перерисовываем блок
            self.redraw_block(self.selected_block)
            
    def on_canvas_release(self, event):
        """Обработка отпускания блока"""
        self.selected_block = None
        
    def on_canvas_double_click(self, event):
        """Обработка двойного клика по блоку для настройки"""
        if self.connection_mode:
            return  # В режиме связи двойной клик не работает
            
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Ищем блок под курсором
        for block in self.blocks:
            bx, by = block.get_position()
            bw, bh = block.get_size()
            if bx <= x <= bx + bw and by <= y <= by + bh:
                # Открываем диалог настройки блока
                if hasattr(block, 'configure'):
                    block.root = self.root  # Устанавливаем ссылку на root
                    block.configure()
                    # Перерисовываем блок после изменения
                    self.redraw_block(block)
                break
                
    def on_canvas_right_click(self, event):
        """Обработка правого клика по блоку для контекстного меню"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Ищем блок под курсором
        clicked_block = None
        for block in self.blocks:
            bx, by = block.get_position()
            bw, bh = block.get_size()
            if bx <= x <= bx + bw and by <= y <= by + bh:
                clicked_block = block
                break
                
        if clicked_block:
            self.show_context_menu(event, clicked_block)
            
    def show_context_menu(self, event, block):
        """Показывает контекстное меню для блока"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Опция "Настроить"
        context_menu.add_command(label="Настроить", 
                                command=lambda: self.configure_block(block))
        
        # Опция "Связь"
        context_menu.add_command(label="Создать связь", 
                                command=lambda: self.start_connection(block))
        
        # Опция "Удалить"
        context_menu.add_command(label="Удалить", 
                                command=lambda: self.delete_block(block))
        
        # Показываем меню
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def configure_block(self, block):
        """Настраивает блок"""
        if hasattr(block, 'configure'):
            block.root = self.root
            block.configure()
            self.redraw_block(block)
            
    def start_connection(self, block):
        """Начинает создание связи с блоком"""
        self.connection_mode = True
        self.source_block = block
        
        # Изменяем курсор
        self.canvas.config(cursor="crosshair")
        
        # Обновляем статус
        self.update_status("Режим связи: кликните на целевой блок")
        
    def delete_block(self, block):
        """Удаляет блок"""
        # Удаляем связи с этим блоком
        self.remove_block_connections(block)
        
        # Удаляем визуальные элементы
        rect_id, text_id = block.get_canvas_ids()
        self.canvas.delete(rect_id)
        self.canvas.delete(text_id)
        
        # Удаляем внешнюю рамку если есть
        outer_rect_id = block.get_outer_rect_id()
        if outer_rect_id:
            self.canvas.delete(outer_rect_id)
        
        # Удаляем из списка блоков
        self.blocks.remove(block)
        
        # Перерисовываем связи
        self.redraw_connections()
        
    def remove_block_connections(self, block):
        """Удаляет все связи с блоком"""
        # Удаляем связи где блок является источником
        if block in self.block_connections:
            del self.block_connections[block]
            
        # Удаляем связи где блок является целью
        for source, target in list(self.block_connections.items()):
            if target == block:
                del self.block_connections[source]
                
    def update_status(self, message):
        """Обновляет статусное сообщение (если есть статус-бар)"""
        # Можно добавить статус-бар в будущем
        pass
        
    def redraw_block(self, block):
        """Перерисовывает блок на новой позиции"""
        rect_id, text_id = block.get_canvas_ids()
        x, y = block.get_position()
        width, height = block.get_size()
        
        # Обновляем позицию элементов
        self.canvas.coords(rect_id, x, y, x + width, y + height)
        
        # Обновляем внешнюю рамку если есть
        outer_rect_id = block.get_outer_rect_id()
        if outer_rect_id:
            self.canvas.coords(outer_rect_id, x-5, y-5, x + width+5, y + height+5)
        
        # Обновляем текст
        text = block.get_text()
        # Разбиваем длинный текст на строки
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= 25:  # Примерно 25 символов на строку
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Обновляем текст с переносом
        text_lines = "\n".join(lines)
        self.canvas.coords(text_id, x + width//2, y + height//2)
        self.canvas.itemconfig(text_id, text=text_lines)
        
        # Перерисовываем связи
        self.redraw_connections()
        
    def generate_cpp(self):
        """Генерирует C++ код из блоков"""
        try:
            cpp_code = self.code_generator.generate_code(self.blocks, self.block_connections)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, cpp_code)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации кода: {str(e)}")
            
    def compile_and_run(self):
        """Компилирует и выполняет C++ код"""
        try:
            cpp_code = self.code_text.get(1.0, tk.END).strip()
            if not cpp_code:
                messagebox.showwarning("Предупреждение", "Сначала сгенерируйте код!")
                return
                
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(cpp_code)
                temp_file = f.name
                
            # Компилируем
            compile_result = subprocess.run(['g++', temp_file, '-o', temp_file + '.exe'], 
                                          capture_output=True, text=True)
            
            if compile_result.returncode != 0:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(1.0, f"Ошибка компиляции:\n{compile_result.stderr}")
                return
                
            # Выполняем
            run_result = subprocess.run([temp_file + '.exe'], 
                                      capture_output=True, text=True)
            
            # Выводим результат
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, f"Вывод:\n{run_result.stdout}")
            if run_result.stderr:
                self.output_text.insert(tk.END, f"\nОшибки:\n{run_result.stderr}")
                
            # Удаляем временные файлы
            os.unlink(temp_file)
            if os.path.exists(temp_file + '.exe'):
                os.unlink(temp_file + '.exe')
                
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Компилятор g++ не найден! Установите MinGW или другую среду разработки C++.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения: {str(e)}")
            
    def new_project(self):
        """Создает новый проект"""
        self.blocks.clear()
        self.block_connections.clear()
        self.connection_mode = False
        self.source_block = None
        self.canvas.delete("all")
        self.code_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        
    def save_project(self):
        """Сохраняет проект в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Создаем словарь связей для сохранения
                connections_data = {}
                for source, target in self.block_connections.items():
                    source_id = id(source)
                    target_id = id(target)
                    connections_data[source_id] = target_id
                
                project_data = {
                    "blocks": [block.to_dict() for block in self.blocks],
                    "connections": connections_data
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успех", "Проект сохранен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
                
    def open_project(self):
        """Открывает проект из файла"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                self.new_project()
                
                # Загружаем блоки
                block_id_map = {}  # Карта ID блоков для восстановления связей
                for block_data in project_data["blocks"]:
                    block = self.block_system.create_block_from_dict(block_data)
                    if block:
                        self.blocks.append(block)
                        self.draw_block(block)
                        # Сохраняем соответствие ID блока
                        block_id_map[block_data.get("id", id(block))] = block
                
                # Восстанавливаем связи
                if "connections" in project_data:
                    for source_id, target_id in project_data["connections"].items():
                        source_block = block_id_map.get(int(source_id))
                        target_block = block_id_map.get(int(target_id))
                        if source_block and target_block:
                            self.block_connections[source_block] = target_block
                    
                    # Перерисовываем связи
                    self.redraw_connections()
                        
                messagebox.showinfo("Успех", "Проект загружен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

def main():
    root = tk.Tk()
    app = CppBlockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
