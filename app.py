import threading
import time

import customtkinter as ctk
import serial
import serial.tools.list_ports


class GridSerialApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TestBoard Control")
        self.geometry("500x520")
        self.resizable(False, False)

        self.serial_conn = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Configure grid
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((1, 2), weight=1)

        # Header
        self.label = ctk.CTkLabel(self, text="Hardware Control Pad", font=("Arial", 22, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=20)

        # Row 1: LED controls
        self.on_btn = ctk.CTkButton(
            self, text="LED ON", fg_color="#2ecc71", hover_color="#27ae60",
            command=lambda: self.send_command("LED_ON"), state="disabled"
        )
        self.on_btn.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.off_btn = ctk.CTkButton(
            self, text="LED OFF", fg_color="#e74c3c", hover_color="#c0392b",
            command=lambda: self.send_command("LED_OFF"), state="disabled"
        )
        self.off_btn.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        # Row 2: Lock controls
        self.lock_on_btn = ctk.CTkButton(
            self, text="Lock ON", fg_color="#2ecc71", hover_color="#27ae60",
            command=lambda: self.send_command("Lock_ON"), state="disabled"
        )
        self.lock_on_btn.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.lock_off_btn = ctk.CTkButton(
            self, text="Lock OFF", fg_color="#e74c3c", hover_color="#c0392b",
            command=lambda: self.send_command("Lock_OFF"), state="disabled"
        )
        self.lock_off_btn.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")

        # Row 3: Port dropdown + connect/disconnect
        self.port_var = ctk.StringVar(value="Select Port")
        self.port_menu = ctk.CTkOptionMenu(self, variable=self.port_var, values=self._get_ports())
        self.port_menu.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.connect_btn = ctk.CTkButton(self, text="Connect", command=self._toggle_connection)
        self.connect_btn.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # Row 4: Refresh ports button
        self.refresh_btn = ctk.CTkButton(
            self, text="Refresh Ports", fg_color="gray40", hover_color="gray30",
            command=self._refresh_ports
        )
        self.refresh_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        # Row 5: Status label
        self.status_label = ctk.CTkLabel(self, text="Status: Disconnected", text_color="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)

    # --- Port helpers ---

    def _get_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports if ports else ["No Ports Found"]

    def _refresh_ports(self):
        ports = self._get_ports()
        self.port_menu.configure(values=ports)
        current = self.port_var.get()
        if current not in ports:
            self.port_var.set(ports[0])

    # --- Connection management ---

    def _set_controls_state(self, state):
        for btn in (self.on_btn, self.off_btn, self.lock_on_btn, self.lock_off_btn):
            btn.configure(state=state)

    def _toggle_connection(self):
        if self.serial_conn and self.serial_conn.is_open:
            self._disconnect()
        else:
            self._start_connect()

    def _disconnect(self):
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.serial_conn = None
        self._set_controls_state("disabled")
        self.connect_btn.configure(text="Connect", state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text="Status: Disconnected", text_color="gray")

    def _start_connect(self):
        port = self.port_var.get()
        if port in ("Select Port", "No Ports Found"):
            self.status_label.configure(text="Error: Select a port first", text_color="red")
            return

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None

        # Disable buttons while connecting to prevent double-clicks
        self.connect_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        self.status_label.configure(text="Connecting — waiting for Arduino reset...", text_color="orange")
        self.update()

        # Run blocking connect in a background thread so the UI stays responsive
        threading.Thread(target=self._connect_worker, args=(port,), daemon=True).start()

    def _connect_worker(self, port):
        try:
            conn = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino boot
            self.after(0, self._on_connect_success, conn, port)
        except serial.SerialException as e:
            self.after(0, self._on_connect_failure, str(e))
        except Exception as e:
            self.after(0, self._on_connect_failure, str(e))

    def _on_connect_success(self, conn, port):
        self.serial_conn = conn
        self._set_controls_state("normal")
        self.connect_btn.configure(text="Disconnect", state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text=f"Connected: {port}", text_color="green")

    def _on_connect_failure(self, error_msg):
        self.serial_conn = None
        self.connect_btn.configure(text="Connect", state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text=f"Error: {error_msg}", text_color="red")

    # --- Command sending ---

    def send_command(self, cmd):
        if not self.serial_conn or not self.serial_conn.is_open:
            self.status_label.configure(text="Error: Not connected", text_color="red")
            self._set_controls_state("disabled")
            self.connect_btn.configure(text="Connect")
            return

        try:
            self.serial_conn.write(f"{cmd}\n".encode("utf-8"))
            self.status_label.configure(text=f"Sent: {cmd}", text_color="green")
        except serial.SerialException as e:
            self.status_label.configure(text=f"Send error: {e}", text_color="red")
            self.serial_conn = None
            self._set_controls_state("disabled")
            self.connect_btn.configure(text="Connect")
        except Exception as e:
            self.status_label.configure(text=f"Unexpected error: {e}", text_color="red")

    # --- Cleanup ---

    def _on_close(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.destroy()


if __name__ == "__main__":
    app = GridSerialApp()
    app.mainloop()
