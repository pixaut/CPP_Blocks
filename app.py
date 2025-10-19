import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from block_system import *


class EditDialog(tk.Toplevel):
    def __init__(self, parent, block):
        super().__init__(parent)
        self.block = block
        self.result = None
        self.title("Edit Block")
        self.geometry("300x200")
        self.transient(parent)
        self.grab_set()

        if isinstance(block, Function):
            self.create_function_dialog()
        elif isinstance(block, VariableBlock):
            self.create_variable_dialog()
        elif isinstance(block, AssignmentBlock):
            self.create_assignment_dialog()
        elif isinstance(block, ReturnBlock):
            self.create_return_dialog()

        ttk.Button(self, text="OK", command=self.ok).pack(pady=10)
        ttk.Button(self, text="Cancel", command=self.destroy).pack(pady=10)

    def create_function_dialog(self):
        ttk.Label(self, text="Return Type:").pack(pady=5)
        self.type_var = tk.StringVar(value=self.block.type)
        ttk.Entry(self, textvariable=self.type_var).pack(pady=5)

        ttk.Label(self, text="Name:").pack(pady=5)
        self.name_var = tk.StringVar(value=self.block.name)
        ttk.Entry(self, textvariable=self.name_var).pack(pady=5)

    def create_variable_dialog(self):
        ttk.Label(self, text="Type:").pack(pady=5)
        self.type_var = tk.StringVar(value=self.block.type)
        ttk.Entry(self, textvariable=self.type_var).pack(pady=5)

        ttk.Label(self, text="Name:").pack(pady=5)
        self.name_var = tk.StringVar(value=self.block.name)
        ttk.Entry(self, textvariable=self.name_var).pack(pady=5)

        ttk.Label(self, text="Initial Value (optional):").pack(pady=5)
        self.value_var = tk.StringVar(value=str(self.block.value) if self.block.value is not None else "")
        ttk.Entry(self, textvariable=self.value_var).pack(pady=5)

    def create_assignment_dialog(self):
        ttk.Label(self, text="Variable:").pack(pady=5)
        self.var_var = tk.StringVar(value=self.block.var_name)
        ttk.Entry(self, textvariable=self.var_var).pack(pady=5)

        ttk.Label(self, text="Expression:").pack(pady=5)
        self.expr_var = tk.StringVar(value=self.block.expression)
        ttk.Entry(self, textvariable=self.expr_var).pack(pady=5)

    def create_return_dialog(self):
        ttk.Label(self, text="Expression:").pack(pady=5)
        self.expr_var = tk.StringVar(value=self.block.expression)
        ttk.Entry(self, textvariable=self.expr_var).pack(pady=5)

    def ok(self):
        if isinstance(self.block, Function):
            self.block.type = self.type_var.get()
            self.block.name = self.name_var.get()
        elif isinstance(self.block, VariableBlock):
            self.block.type = self.type_var.get()
            self.block.name = self.name_var.get()
            val = self.value_var.get().strip()
            self.block.value = val if val else None
        elif isinstance(self.block, AssignmentBlock):
            self.block.var_name = self.var_var.get()
            self.block.expression = self.expr_var.get()
        elif isinstance(self.block, ReturnBlock):
            self.block.expression = self.expr_var.get()
        self.result = True
        self.destroy()


class BlockWidget:
    """UI-обёртка для блока"""

    def __init__(self, canvas: tk.Canvas, block: Block, x: int, y: int, text: str, app):
        self.canvas = canvas
        self.block = block
        self.text = text
        self.x, self.y = x, y
        self.app = app
        self.selected = False

        # Different colors for different block types
        colors = {
            Function: ("lightblue", "#5070ff"),
            VariableBlock: ("lightgreen", "#007000"),
            AssignmentBlock: ("orange", "#ff8000"),
            ReturnBlock: ("lightpink", "#cc0000"),
        }
        block_type = type(block)
        if block_type in colors:
            self.normal_fill, self.normal_outline = colors[block_type]
        else:
            self.normal_fill, self.normal_outline = "#d0e0ff", "#5070ff"
        self.selected_fill = "#ffff99"
        self.selected_outline = "#ff0000"

        width = 140
        height = 40
        self.rect = canvas.create_rectangle(x, y, x + width, y + height, fill=self.normal_fill, outline=self.normal_outline, width=2)
        self.label = canvas.create_text(x + 70, y + 20, text=text)
        self.drag_data = {"x": 0, "y": 0}

        self.has_input = not isinstance(block, Function)
        self.has_output = not isinstance(block, ReturnBlock)
        self.input_port = None
        self.output_port = None

        if self.has_input:
            self.input_port = canvas.create_oval(x - 10, y + 15, x, y + 25, fill="blue", tags="input_port")
        if self.has_output:
            self.output_port = canvas.create_oval(x + 140, y + 15, x + 150, y + 25, fill="green")
            canvas.tag_bind(self.output_port, "<ButtonPress-1>", self.start_connect)

        # Bind drag to rect and label
        canvas.tag_bind(self.rect, "<ButtonPress-1>", self.start_drag)
        canvas.tag_bind(self.label, "<ButtonPress-1>", self.start_drag)
        canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.label, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.rect, "<ButtonRelease-1>", self.stop_drag)
        canvas.tag_bind(self.label, "<ButtonRelease-1>", self.stop_drag)

        # Context menu on rect and label
        canvas.tag_bind(self.rect, "<Button-3>", self.show_context_menu)
        canvas.tag_bind(self.label, "<Button-3>", self.show_context_menu)
        if self.has_input:
            canvas.tag_bind(self.input_port, "<Button-3>", self.show_context_menu)

        self.temp_line = None
        self.start_x = 0
        self.start_y = 0

    def select(self):
        if not self.selected:
            self.selected = True
            self.canvas.itemconfig(self.rect, fill=self.selected_fill, outline=self.selected_outline)
            self.app.selected_blocks.add(self)

    def deselect(self):
        if self.selected:
            self.selected = False
            self.canvas.itemconfig(self.rect, fill=self.normal_fill, outline=self.normal_outline)
            self.app.selected_blocks.discard(self)

    def get_port_center(self, port):
        bbox = self.canvas.coords(port)
        return (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2

    def update_connections(self):
        # Update outgoing connections
        if hasattr(self.block, 'outgoing_connections'):
            for conn in self.block.outgoing_connections:
                line = conn['line']
                target = conn['target']
                target_widget = next((w for w in self.app.blocks_ui if w.block == target), None)
                if target_widget and target_widget.has_input:
                    tx, ty = target_widget.get_port_center(target_widget.input_port)
                    sx, sy = self.get_port_center(self.output_port)
                    self.canvas.coords(line, sx, sy, tx, ty)

        # Update incoming connections
        if hasattr(self.block, 'incoming_connections'):
            for conn in self.block.incoming_connections:
                line = conn['line']
                source = conn['source']
                source_widget = next((w for w in self.app.blocks_ui if w.block == source), None)
                if source_widget and source_widget.has_output:
                    sx, sy = source_widget.get_port_center(source_widget.output_port)
                    tx, ty = self.get_port_center(self.input_port)
                    self.canvas.coords(line, sx, sy, tx, ty)

    def start_drag(self, event):
        # Handle selection
        ctrl = bool(event.state & 0x0004)
        if ctrl:
            self.app.toggle_select(self)
        else:
            self.app.clear_selection()
            self.select()
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.label, dx, dy)
        if self.has_input:
            self.canvas.move(self.input_port, dx, dy)
        if self.has_output:
            self.canvas.move(self.output_port, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.x += dx
        self.y += dy
        # Update connections during drag
        self.update_connections()

    def stop_drag(self, event):
        grid_size = 20
        self.x = round(self.x / grid_size) * grid_size
        self.y = round(self.y / grid_size) * grid_size
        width = 140
        height = 40
        self.canvas.coords(self.rect, self.x, self.y, self.x + width, self.y + height)
        self.canvas.coords(self.label, self.x + 70, self.y + 20)
        if self.has_input:
            self.canvas.coords(self.input_port, self.x - 10, self.y + 15, self.x, self.y + 25)
        if self.has_output:
            self.canvas.coords(self.output_port, self.x + 140, self.y + 15, self.x + 150, self.y + 25)
        # Final update of connections
        self.update_connections()

    def clear_function_body(self):
        func = self.block
        connections = func.connections[:]
        if connections:
            # Remove line from function to first block
            first = connections[0]
            for conn in func.outgoing_connections[:]:
                if conn['target'] == first:
                    self.canvas.delete(conn['line'])
                    func.outgoing_connections.remove(conn)
                    break
            for conn in first.incoming_connections[:]:
                if conn['source'] == func:
                    first.incoming_connections.remove(conn)
                    break
        # Remove internal lines
        for i in range(1, len(connections)):
            prev = connections[i-1]
            curr = connections[i]
            for conn in prev.outgoing_connections[:]:
                if conn['target'] == curr:
                    self.canvas.delete(conn['line'])
                    prev.outgoing_connections.remove(conn)
                    break
            for conn in curr.incoming_connections[:]:
                if conn['source'] == prev:
                    curr.incoming_connections.remove(conn)
                    break
        # Unassign all
        for block in connections:
            block.owner = None
        func.connections = []

    def start_connect(self, event):
        if not self.has_output:
            return
        if hasattr(self.block, 'outgoing_connections') and self.block.outgoing_connections:
            if isinstance(self.block, Function):
                self.clear_function_body()
            else:
                # Remove existing connection for non-function
                old_conn = self.block.outgoing_connections.pop(0)
                self.canvas.delete(old_conn['line'])
                old_target = old_conn['target']
                if hasattr(old_target, 'incoming_connections'):
                    old_target.incoming_connections = [c for c in old_target.incoming_connections if c['line'] != old_conn['line']]
                if hasattr(self.block, 'owner') and self.block.owner:
                    try:
                        self.block.owner.connections.remove(old_target)
                    except ValueError:
                        pass
            self.update_connections()
        # Always start new connection
        if self.app.connecting is not None and self.app.connecting != self:
            prev = self.app.connecting
            self.app.canvas.delete(prev.temp_line)
            prev.temp_line = None
            self.app.canvas.unbind("<B1-Motion>")
            self.app.canvas.unbind("<ButtonRelease-1>")
        self.app.connecting = self
        ox, oy = self.get_port_center(self.output_port)
        self.start_x = ox
        self.start_y = oy
        self.temp_line = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill="red", width=2)
        self.canvas.bind("<B1-Motion>", self.on_connect_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_connect)

    def on_connect_drag(self, event):
        if self.temp_line is None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.temp_line, self.start_x, self.start_y, x, y)

    def end_connect(self, event):
        if self.temp_line is None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.delete(self.temp_line)
        self.temp_line = None

        # Find target input port
        overlapping = self.canvas.find_overlapping(x - 10, y - 10, x + 10, y + 10)
        target_widget = None
        for item in overlapping:
            tags = self.canvas.gettags(item)
            if "input_port" in tags:
                for w in self.app.blocks_ui:
                    if w.input_port == item:
                        target_widget = w
                        break
                if target_widget:
                    break

        if target_widget and target_widget.has_input:
            # Check if target already has incoming
            if hasattr(target_widget.block, 'incoming_connections') and target_widget.block.incoming_connections:
                messagebox.showerror("Error", "Target already has an incoming connection.")
                return

            ix, iy = target_widget.get_port_center(target_widget.input_port)
            sx, sy = self.get_port_center(self.output_port)
            line = self.canvas.create_line(sx, sy, ix, iy, fill="black", width=1, arrow=tk.LAST, tags=("connection",))
            self.app.connect_blocks(self.block, target_widget.block)
            # Update connections lists
            if not hasattr(self.block, 'outgoing_connections'):
                self.block.outgoing_connections = []
            self.block.outgoing_connections.append({'line': line, 'target': target_widget.block})
            if not hasattr(target_widget.block, 'incoming_connections'):
                target_widget.block.incoming_connections = []
            target_widget.block.incoming_connections.append({'line': line, 'source': self.block})
            # Update visuals
            self.update_connections()

        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.app.connecting = None

    def show_context_menu(self, event):
        menu = tk.Menu(self.canvas.winfo_toplevel(), tearoff=0)
        menu.add_command(label="Edit", command=self.edit_block)

        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self.app.delete_block(self.block))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def edit_block(self):
        dialog = EditDialog(self.canvas.winfo_toplevel(), self.block)
        self.canvas.winfo_toplevel().wait_window(dialog)
        if dialog.result:
            if isinstance(self.block, Function):
                self.text = f"{self.block.type} {self.block.name}()"
            elif isinstance(self.block, VariableBlock):
                if self.block.value is not None:
                    self.text = f"{self.block.type} {self.block.name} = {self.block.value}"
                else:
                    self.text = f"{self.block.type} {self.block.name}"
            elif isinstance(self.block, AssignmentBlock):
                self.text = f"{self.block.var_name} = {self.block.expression}"
            elif isinstance(self.block, ReturnBlock):
                self.text = f"return {self.block.expression}"
            self.canvas.itemconfig(self.label, text=self.text)


class ScratchApp(tk.Tk):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.title("C++ Scratch — визуальный генератор")
        self.geometry("1000x700")

        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side="top", fill="x")

        self.canvas = tk.Canvas(self, bg="#f0f0f0")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.palette = tk.Frame(self, relief="raised", bd=2, bg="lightgray", width=150)
        self.palette.pack(side="right", fill="y")
        self.palette.propagate(False)

        self.blocks_ui = []
        self.selected_blocks = set()
        self.selected_lines = set()
        self.connecting = None
        self.rubber_id = None
        self.select_start_x = 0
        self.select_start_y = 0

        self.bind("<Delete>", self.delete_selected)
        self.canvas.bind("<Delete>", self.delete_selected)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", self.redraw_grid)
        self.focus_set()

        self.create_palette_items()
        self.redraw_grid()

        ttk.Button(self.toolbar, text="Сгенерировать код", command=self.show_generated_code).pack(side="right", padx=4, pady=4)

    def on_canvas_click(self, event):
        over = self.canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1)
        connection_items = [item for item in over if "connection" in self.canvas.gettags(item)]
        block_items = set()
        for w in self.blocks_ui:
            block_items.add(w.rect)
            block_items.add(w.label)
            if w.has_input:
                block_items.add(w.input_port)
            if w.has_output:
                block_items.add(w.output_port)
        block_over = any(item in block_items for item in over)

        if connection_items:
            self.clear_selection()  # Clear block selection when selecting lines
            ctrl = bool(event.state & 0x0004)
            if ctrl:
                for item in connection_items:
                    if item in self.selected_lines:
                        self.deselect_line(item)
                    else:
                        self.select_line(item)
            else:
                self.clear_line_selection()
                for item in connection_items:
                    self.select_line(item)
            return
        elif block_over:
            return  # Let block handle
        # Start rubber band selection
        self.clear_selection()
        self.clear_line_selection()
        self.select_start_x = event.x
        self.select_start_y = event.y
        self.rubber_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="gray", dash=(5, 5), width=1)
        self.canvas.bind("<B1-Motion>", self.on_rubber_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_rubber_release)

    def select_line(self, line_id):
        if line_id not in self.selected_lines:
            self.selected_lines.add(line_id)
            self.canvas.itemconfig(line_id, fill="red", width=3)

    def deselect_line(self, line_id):
        if line_id in self.selected_lines:
            self.selected_lines.discard(line_id)
            self.canvas.itemconfig(line_id, fill="black", width=1)

    def clear_line_selection(self):
        for line_id in list(self.selected_lines):
            self.deselect_line(line_id)

    def on_rubber_drag(self, event):
        if self.rubber_id is None:
            return
        x1, y1 = self.select_start_x, self.select_start_y
        x2, y2 = event.x, event.y
        self.canvas.coords(self.rubber_id, x1, y1, x2, y2)

    def on_rubber_release(self, event):
        if self.rubber_id is None:
            return
        x1 = min(self.select_start_x, event.x)
        y1 = min(self.select_start_y, event.y)
        x2 = max(self.select_start_x, event.x)
        y2 = max(self.select_start_y, event.y)
        if abs(x2 - x1) < 5 and abs(y2 - y1) < 5:
            # Small area, just click - deselect all
            self.clear_selection()
            self.clear_line_selection()
        else:
            # Select blocks and lines in box
            for widget in self.blocks_ui:
                wx1, wy1, wx2, wy2 = widget.x, widget.y, widget.x + 140, widget.y + 40
                if not (x2 < wx1 or x1 > wx2 or y2 < wy1 or y1 > wy2):
                    widget.select()
            for item in self.canvas.find_overlapping(x1, y1, x2, y2):
                if "connection" in self.canvas.gettags(item):
                    self.select_line(item)
        self.canvas.delete(self.rubber_id)
        self.rubber_id = None
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def clear_selection(self):
        for widget in list(self.selected_blocks):
            widget.deselect()

    def toggle_select(self, widget):
        if widget in self.selected_blocks:
            widget.deselect()
        else:
            widget.select()

    def select(self, widget):
        widget.select()

    def delete_selected(self, event=None):
        # Delete blocks
        to_delete_blocks = list(self.selected_blocks)
        for widget in to_delete_blocks:
            self.delete_block(widget.block)
        self.selected_blocks.clear()
        # Delete lines
        to_delete_lines = list(self.selected_lines)
        for line_id in to_delete_lines:
            self.canvas.delete(line_id)
            # Clean up logical connections
            for widget in self.blocks_ui:
                if hasattr(widget.block, 'outgoing_connections'):
                    widget.block.outgoing_connections = [c for c in widget.block.outgoing_connections if c['line'] != line_id]
                if hasattr(widget.block, 'incoming_connections'):
                    widget.block.incoming_connections = [c for c in widget.block.incoming_connections if c['line'] != line_id]
                # If function, remove the target from connections
                if isinstance(widget.block, Function):
                    for c in widget.block.outgoing_connections:
                        target = c['target']
                        if target in widget.block.connections:
                            widget.block.connections.remove(target)
        self.selected_lines.clear()

    def redraw_grid(self, event=None):
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        grid_size = 20
        for i in range(0, width, grid_size):
            self.canvas.create_line(i, 0, i, height, fill="lightgray", dash=(4, 4), tags="grid")
        for i in range(0, height, grid_size):
            self.canvas.create_line(0, i, width, i, fill="lightgray", dash=(4, 4), tags="grid")

    def create_palette_items(self):
        palette_items = [
            ("Function", lambda: Function("int", f"func{len([b for b in self.blocks_ui if isinstance(b.block, Function)])}")),
            ("Variable", lambda: VariableBlock("int", f"var{len(self.blocks_ui)}", None)),
            ("Assignment", lambda: AssignmentBlock("result", "0")),
            ("Return", lambda: ReturnBlock("0")),
        ]
        for name, creator in palette_items:
            item = tk.Label(self.palette, text=name, bg="white", relief="ridge", padx=10, pady=5, cursor="hand2")
            item.pack(pady=5, fill="x")
            item.bind("<ButtonPress-1>", lambda e, cr=creator, nt=name: self.start_drag_new(e, cr, nt))

    def start_drag_new(self, event, creator, ghost_text):
        self.creator = creator
        self.ghost_text = ghost_text
        self.ghost_rect = self.canvas.create_rectangle(0, 0, 140, 40, fill="#d0e0ff", outline="#5070ff", stipple="gray25", tags="ghost")
        self.ghost_label = self.canvas.create_text(70, 20, text=ghost_text, tags="ghost")
        self.canvas.tag_raise("ghost")
        self.bind("<B1-Motion>", self.on_drag_new)
        self.bind("<ButtonRelease-1>", self.drop_new)

    def on_drag_new(self, event):
        if not hasattr(self, 'ghost_rect'):
            return
        wx = event.x_root - self.canvas.winfo_rootx()
        wy = event.y_root - self.canvas.winfo_rooty()
        cx = self.canvas.canvasx(wx)
        cy = self.canvas.canvasy(wy)
        self.canvas.coords(self.ghost_rect, cx - 70, cy - 20, cx + 70, cy + 20)
        self.canvas.coords(self.ghost_label, cx, cy)

    def drop_new(self, event):
        if not hasattr(self, 'creator'):
            return
        wx = event.x_root - self.canvas.winfo_rootx()
        wy = event.y_root - self.canvas.winfo_rooty()
        cx = self.canvas.canvasx(wx)
        cy = self.canvas.canvasy(wy)
        grid_size = 20
        x = round(cx / grid_size) * grid_size
        y = round(cy / grid_size) * grid_size

        block = self.creator()
        if isinstance(block, Function):
            text = f"{block.type} {block.name}()"
        elif isinstance(block, VariableBlock):
            if block.value is not None:
                text = f"{block.type} {block.name} = {block.value}"
            else:
                text = f"{block.type} {block.name}"
        elif isinstance(block, AssignmentBlock):
            text = f"{block.var_name} = {block.expression}"
        elif isinstance(block, ReturnBlock):
            text = f"return {block.expression}"
        else:
            text = "block"

        widget = BlockWidget(self.canvas, block, x, y, text, self)
        self.blocks_ui.append(widget)
        block.owner = None
        self.canvas.delete(self.ghost_rect)
        self.canvas.delete(self.ghost_label)
        if hasattr(self, 'ghost_rect'):
            del self.ghost_rect
        if hasattr(self, 'ghost_label'):
            del self.ghost_label
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")
        self.creator = None

    def connect_blocks(self, source, target):
        if source == target:
            return
        if isinstance(source, Function):
            func = source
        else:
            if source.owner is None:
                messagebox.showerror("Error", "Cannot connect unassigned block.")
                return
            func = source.owner
        if target.owner is not None and target.owner != func:
            try:
                target.owner.connections.remove(target)
            except ValueError:
                pass
            target.owner = None

        # Check for multiple returns
        if isinstance(target, ReturnBlock):
            if any(isinstance(c, ReturnBlock) for c in func.connections):
                messagebox.showerror("Error", "Function already has a return statement.")
                return

        if isinstance(source, Function):
            if target not in func.connections:
                func.connections.append(target)
            target.owner = func
        else:
            if target in func.connections:
                func.connections.remove(target)
            idx = func.connections.index(source)
            func.connections.insert(idx + 1, target)
            target.owner = func

    def delete_block(self, block):
        # Delete lines
        if hasattr(block, 'outgoing_connections'):
            for conn in block.outgoing_connections:
                line = conn['line']
                self.canvas.delete(line)
                self.selected_lines.discard(line)
                target = conn['target']
                if target and hasattr(target, 'incoming_connections'):
                    target.incoming_connections = [c for c in target.incoming_connections if c['line'] != line]
        if hasattr(block, 'incoming_connections'):
            for conn in block.incoming_connections:
                line = conn['line']
                self.canvas.delete(line)
                self.selected_lines.discard(line)
                source = conn['source']
                if source and hasattr(source, 'outgoing_connections'):
                    source.outgoing_connections = [c for c in source.outgoing_connections if c['line'] != line]

        if hasattr(block, 'owner') and block.owner:
            try:
                block.owner.connections.remove(block)
            except ValueError:
                pass
        for widget in self.blocks_ui[:]:
            if widget.block == block:
                self.canvas.delete(widget.rect)
                self.canvas.delete(widget.label)
                if hasattr(widget, 'input_port'):
                    self.canvas.delete(widget.input_port)
                if hasattr(widget, 'output_port'):
                    self.canvas.delete(widget.output_port)
                if widget in self.selected_blocks:
                    self.selected_blocks.remove(widget)
                self.blocks_ui.remove(widget)
                break

    def show_generated_code(self):
        code = "\n\n".join(f.generate_code() for f in [b.block for b in self.blocks_ui if isinstance(b.block, Function)])
        messagebox.showinfo("Сгенерированный код", code)


if __name__ == "__main__":
    app = ScratchApp()
    app.mainloop()