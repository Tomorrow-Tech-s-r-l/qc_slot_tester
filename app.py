import threading
import time

import customtkinter as ctk
import serial
import serial.tools.list_ports

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_GREEN       = "#2ecc71"
_GREEN_HOVER = "#27ae60"
_RED         = "#e74c3c"
_RED_HOVER   = "#c0392b"


class QCSlotTester(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QC Slot Tester")
        self.geometry("480x580")
        self.resizable(False, False)

        self.serial_conn = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2, 3), weight=1)

        # ── Header ───────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, pady=(20, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="QC Slot Tester",
                     font=("Arial", 28, "bold")).grid(row=0, column=0)
        ctk.CTkLabel(header, text="Quality Control — Station Hardware",
                     font=("Arial", 13), text_color="gray").grid(row=1, column=0)

        # ── LED Control ──────────────────────────────────────────────────────
        led_frame = ctk.CTkFrame(self)
        led_frame.grid(row=1, column=0, padx=20, pady=8, sticky="nsew")
        led_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(led_frame, text="LED", font=("Arial", 11, "bold"),
                     text_color="gray").grid(row=0, column=0, columnspan=2, pady=(10, 4))

        self.on_btn = ctk.CTkButton(
            led_frame, text="ON", height=52,
            fg_color=_GREEN, hover_color=_GREEN_HOVER,
            font=("Arial", 15, "bold"),
            command=lambda: self.send_command("LED_ON"), state="disabled"
        )
        self.on_btn.grid(row=1, column=0, padx=(14, 7), pady=(0, 14), sticky="nsew")

        self.off_btn = ctk.CTkButton(
            led_frame, text="OFF", height=52,
            fg_color=_RED, hover_color=_RED_HOVER,
            font=("Arial", 15, "bold"),
            command=lambda: self.send_command("LED_OFF"), state="disabled"
        )
        self.off_btn.grid(row=1, column=1, padx=(7, 14), pady=(0, 14), sticky="nsew")

        # ── Lock Control ─────────────────────────────────────────────────────
        lock_frame = ctk.CTkFrame(self)
        lock_frame.grid(row=2, column=0, padx=20, pady=8, sticky="nsew")
        lock_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(lock_frame, text="LOCK", font=("Arial", 11, "bold"),
                     text_color="gray").grid(row=0, column=0, columnspan=2, pady=(10, 4))

        self.lock_on_btn = ctk.CTkButton(
            lock_frame, text="ON", height=52,
            fg_color=_GREEN, hover_color=_GREEN_HOVER,
            font=("Arial", 15, "bold"),
            command=lambda: self.send_command("Lock_ON"), state="disabled"
        )
        self.lock_on_btn.grid(row=1, column=0, padx=(14, 7), pady=(0, 14), sticky="nsew")

        self.lock_off_btn = ctk.CTkButton(
            lock_frame, text="OFF", height=52,
            fg_color=_RED, hover_color=_RED_HOVER,
            font=("Arial", 15, "bold"),
            command=lambda: self.send_command("Lock_OFF"), state="disabled"
        )
        self.lock_off_btn.grid(row=1, column=1, padx=(7, 14), pady=(0, 14), sticky="nsew")

        # ── Connection ───────────────────────────────────────────────────────
        conn_frame = ctk.CTkFrame(self)
        conn_frame.grid(row=3, column=0, padx=20, pady=8, sticky="nsew")
        conn_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(conn_frame, text="CONNECTION", font=("Arial", 11, "bold"),
                     text_color="gray").grid(row=0, column=0, columnspan=2, pady=(10, 4))

        self.port_var = ctk.StringVar(value="Select Port")
        self.port_menu = ctk.CTkOptionMenu(conn_frame, variable=self.port_var,
                                           values=self._get_ports())
        self.port_menu.grid(row=1, column=0, padx=(14, 7), pady=(0, 8), sticky="ew")

        self.connect_btn = ctk.CTkButton(conn_frame, text="Connect", width=110,
                                         command=self._toggle_connection)
        self.connect_btn.grid(row=1, column=1, padx=(7, 14), pady=(0, 8))

        self.refresh_btn = ctk.CTkButton(
            conn_frame, text="Refresh Ports",
            fg_color="gray40", hover_color="gray30",
            command=self._refresh_ports
        )
        self.refresh_btn.grid(row=2, column=0, columnspan=2,
                              padx=14, pady=(0, 14), sticky="ew")

        # ── Status bar ───────────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(self, height=38, fg_color=("gray80", "gray17"),
                                  corner_radius=0)
        status_bar.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        status_bar.grid_columnconfigure(1, weight=1)
        status_bar.grid_propagate(False)

        self.dot_label = ctk.CTkLabel(status_bar, text="●", font=("Arial", 16),
                                      text_color="gray", width=28)
        self.dot_label.grid(row=0, column=0, padx=(14, 2), pady=8)

        self.status_label = ctk.CTkLabel(status_bar, text="Disconnected",
                                         font=("Arial", 12), text_color="gray",
                                         anchor="w")
        self.status_label.grid(row=0, column=1, padx=(0, 14), pady=8, sticky="ew")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _set_status(self, text, color):
        self.dot_label.configure(text_color=color)
        self.status_label.configure(text=text, text_color=color)

    def _get_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports if ports else ["No Ports Found"]

    def _refresh_ports(self):
        ports = self._get_ports()
        self.port_menu.configure(values=ports)
        if self.port_var.get() not in ports:
            self.port_var.set(ports[0])

    def _set_controls_state(self, state):
        for btn in (self.on_btn, self.off_btn, self.lock_on_btn, self.lock_off_btn):
            btn.configure(state=state)

    # ── Connection management ─────────────────────────────────────────────────

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
        self._set_status("Disconnected", "gray")

    def _start_connect(self):
        port = self.port_var.get()
        if port in ("Select Port", "No Ports Found"):
            self._set_status("Select a port first", _RED)
            return

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None

        self.connect_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        self._set_status("Connecting — waiting for Arduino reset...", "orange")
        self.update()

        threading.Thread(target=self._connect_worker, args=(port,), daemon=True).start()

    def _connect_worker(self, port):
        try:
            conn = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)
            self.after(0, self._on_connect_success, conn, port)
        except Exception as e:
            self.after(0, self._on_connect_failure, str(e))

    def _on_connect_success(self, conn, port):
        self.serial_conn = conn
        self._set_controls_state("normal")
        self.connect_btn.configure(text="Disconnect", state="normal")
        self.refresh_btn.configure(state="normal")
        self._set_status(f"Connected: {port}", _GREEN)

    def _on_connect_failure(self, error_msg):
        self.serial_conn = None
        self.connect_btn.configure(text="Connect", state="normal")
        self.refresh_btn.configure(state="normal")
        self._set_status(f"Error: {error_msg}", _RED)

    # ── Command sending ───────────────────────────────────────────────────────

    def send_command(self, cmd):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._set_status("Not connected", _RED)
            self._set_controls_state("disabled")
            self.connect_btn.configure(text="Connect")
            return

        try:
            self.serial_conn.write(f"{cmd}\n".encode("utf-8"))
            self._set_status(f"Sent: {cmd}", _GREEN)
        except serial.SerialException as e:
            self._set_status(f"Send error: {e}", _RED)
            self.serial_conn = None
            self._set_controls_state("disabled")
            self.connect_btn.configure(text="Connect")
        except Exception as e:
            self._set_status(f"Unexpected error: {e}", _RED)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def _on_close(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.destroy()


if __name__ == "__main__":
    app = QCSlotTester()
    app.mainloop()
