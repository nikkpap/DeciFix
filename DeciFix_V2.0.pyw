# -*- coding: utf-8 -*-
"""
DecimalSettingsHelper_v2.1.pyw

Windows GUI app for survey-friendly numeric settings:
• Apply: dot (.) as decimal & no thousands grouping (Current User / HKCU)
• Restore: typical Greek defaults (comma decimal, dot thousands, 3-digit grouping)
• Open classic Region dialog (intl.cpl)
• Reboot (needs admin)
• LED indicator (green/red) shows current system state
• Auto-refresh of LED every 2 seconds (catches manual Region changes)
• Optional Admin elevation prompt on startup
• Help menu with Instructions (F1) and About

Keep Excel: Options → Advanced → ✅ Use system separators
"""

import os
import sys
import tempfile
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import winreg
except Exception:
    winreg = None

APP_TITLE = "DeciFix v2.0"

# ---- .REG blobs ---------------------------------------------------------------

DOT_REG = r'''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Control Panel\International]
"sDecimal"="."
"sThousand"=" "
"sGrouping"="0"
"sMonDecimalSep"="."
"sMonThousandSep"=" "
"sList"=";"
'''

RESTORE_REG = r'''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Control Panel\International]
"sDecimal"=","
"sThousand"="."
"sGrouping"="3;0"
"sMonDecimalSep"=","
"sMonThousandSep"="."
"sList"=";"
'''

# ---- Helpers -----------------------------------------------------------------

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def write_temp_reg(contents: str, name: str) -> str:
    fd, path = tempfile.mkstemp(prefix=name, suffix=".reg")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)
    return path

def import_reg(path: str) -> None:
    completed = subprocess.run(["reg", "import", path],
                               capture_output=True, text=True, shell=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

def open_region_dialog():
    subprocess.Popen(["control", "intl.cpl"])

# ---- UI widgets ---------------------------------------------------------------

class LedIndicator(ttk.Frame):
    def __init__(self, master, diameter: int = 14, **kwargs):
        super().__init__(master, **kwargs)
        self._canvas = tk.Canvas(self, width=diameter, height=diameter,
                                 highlightthickness=0, bd=0)
        self._canvas.grid(row=0, column=0, padx=(0, 6))
        self._label = ttk.Label(self, text="Unknown")
        self._label.grid(row=0, column=1, sticky="w")
        self._oval = self._canvas.create_oval(2, 2, diameter - 2, diameter - 2,
                                              fill="#b3b3b3", outline="#888")

    def set_state(self, ok: bool, text_ok="Configured", text_bad="Not configured"):
        color = "#0aa60f" if ok else "#c0392b"
        self._canvas.itemconfig(self._oval, fill=color, outline="#444")
        self._label.configure(text=text_ok if ok else text_bad)

# ---- Main App -----------------------------------------------------------------

class DecimalSettingsHelperApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("560x280")
        self.resizable(False, False)
        self._refresh_job = None

        self._build_style()
        self._build_menu()
        self._build_main()
        self.bind("<F1>", lambda e: self.show_instructions())

        self.after(150, self.refresh_led)
        self._start_auto_refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_style(self):
        try:
            self.call("tk", "scaling", 1.2)
        except Exception:
            pass

    def _build_menu(self):
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Instructions\tF1",
                              command=self.show_instructions, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _build_main(self):
        pad = 14

        ttk.Label(self, text="DeciFix",
                  font=("Segoe UI", 13, "bold")).pack(pady=(pad, 4))

        # LED
        status_fr = ttk.Frame(self)
        status_fr.pack(pady=(0, pad))
        ttk.Label(status_fr, text="Current status:").grid(row=0, column=0, padx=(0, 8))
        self.led = LedIndicator(status_fr)
        self.led.grid(row=0, column=1, padx=(0, 8))

        # Buttons
        btn_fr = ttk.Frame(self); btn_fr.pack()
        ttk.Button(btn_fr, text="Apply dot-decimals (no thousands)", width=36,
                   command=self.apply_dot_settings).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(btn_fr, text="Restore Greek defaults", width=36,
                   command=self.restore_greek_defaults).grid(row=1, column=0, padx=6, pady=6)
        ttk.Button(btn_fr, text="Open Region settings (intl.cpl)", width=36,
                   command=open_region_dialog).grid(row=2, column=0, padx=6, pady=6)

        ttk.Button(self, text="Reboot now", width=18,
                   command=self.reboot_now).pack(pady=(8, pad))

        admin_text = "Running as ADMIN ✅" if is_admin() else "Running as standard user"
        admin_fg = "#0a7b00" if is_admin() else "#555"
        self.admin_lbl = ttk.Label(self, text=admin_text, foreground=admin_fg)
        self.admin_lbl.pack()

    # ---- Logic ----

    def _read_international_values(self):
        r"""Read values from HKCU\Control Panel\International. Returns dict or None."""
        if winreg is None:
            return None
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\International") as k:
                def get(name):
                    try:
                        val, _ = winreg.QueryValueEx(k, name)
                        return str(val)
                    except FileNotFoundError:
                        return ""
                return {
                    "sDecimal": get("sDecimal"),
                    "sThousand": get("sThousand"),
                    "sGrouping": get("sGrouping"),
                    "sMonDecimalSep": get("sMonDecimalSep"),
                    "sMonThousandSep": get("sMonThousandSep"),
                    "sList": get("sList"),
                }
        except Exception:
            return None

    def _is_configured(self) -> bool:
        vals = self._read_international_values()
        if not vals:
            return False
        s_dec = vals.get("sDecimal", "")
        s_mon_dec = vals.get("sMonDecimalSep", "")
        s_thou = vals.get("sThousand", "")
        s_mon_thou = vals.get("sMonThousandSep", "")
        s_group = vals.get("sGrouping", "")
        dec_ok = (s_dec == ".") and (s_mon_dec == ".")
        no_sep_visual = (s_thou.strip() == "" and s_mon_thou.strip() == "")
        no_group_rule = (s_group in ("0", ""))
        return dec_ok and (no_group_rule or no_sep_visual)

    def refresh_led(self):
        ok = self._is_configured()
        self.led.set_state(ok,
                           text_ok="Configured (dot / no thousands)",
                           text_bad="Not configured")
        self.admin_lbl.configure(
            text=("Running as ADMIN ✅" if is_admin() else "Running as standard user"),
            foreground=("#0a7b00" if is_admin() else "#555")
        )

    def _start_auto_refresh(self, interval_ms: int = 2000):
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)
        def _tick():
            self.refresh_led()
            self._refresh_job = self.after(interval_ms, _tick)
        _tick()

    def _on_close(self):
        if self._refresh_job:
            try:
                self.after_cancel(self._refresh_job)
            except Exception:
                pass
        self.destroy()

    def _apply_reg_blob(self, blob: str, temp_name: str):
        path = None
        try:
            path = write_temp_reg(blob, temp_name)
            import_reg(path)
        finally:
            if path:
                try:
                    os.remove(path)
                except Exception:
                    pass

    def apply_dot_settings(self):
        try:
            self._apply_reg_blob(DOT_REG, "set_dot_no_thousands_")
            messagebox.showinfo(APP_TITLE,
                                "Applied: dot-decimals & no thousands (Current User).\n"
                                "Sign-out or reboot to apply everywhere.")
            self.refresh_led()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to import .reg:\n{e}")

    def restore_greek_defaults(self):
        try:
            self._apply_reg_blob(RESTORE_REG, "restore_greek_defaults_")
            messagebox.showinfo(APP_TITLE,
                                "Restored Greek defaults.\n"
                                "Sign-out or reboot to apply everywhere.")
            self.refresh_led()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to import .reg:\n{e}")

    def reboot_now(self):
        if not is_admin():
            if messagebox.askyesno(APP_TITLE,
                                   "Reboot needs Administrator rights.\nRelaunch as admin now?"):
                relaunch_as_admin()
            return
        if messagebox.askyesno(APP_TITLE, "Are you sure you want to reboot now?"):
            try:
                subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Reboot failed:\n{e}")

    # ---- Help ----

    def show_instructions(self):
        win = tk.Toplevel(self)
        win.title("Instructions")
        win.transient(self)
        win.grab_set()
        win.geometry("760x460")
        win.resizable(True, True)

        txt = tk.Text(win, wrap="word")
        vsb = ttk.Scrollbar(win, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        content = (
            "Windows Control Panel ↔ Registry mapping\n\n"
            "| GUI (Control Panel > Region > Additional Settings > Numbers) | Registry Key      | Example Value |\n"
            "| ------------------------------------------------------------ | ----------------- | -------------- |\n"
            "| Decimal symbol | sDecimal | . |\n"
            "| Digit grouping symbol | sThousand | (space) or . |\n"
            "| Digit grouping | sGrouping | 3;0 or 0 |\n"
            "| List separator | sList | ; |\n"
            "| Measurement system | iMeasure | 0 = Metric |\n"
            "| Number of digits after decimal | iDigits | 2 |\n"
            "| Negative number format | iNegNumber | 1 |\n"
            "| Currency tab → Decimal symbol | sMonDecimalSep | . |\n"
            "| Currency tab → Digit grouping symbol | sMonThousandSep | (space) or . |\n"
            "| Currency tab → Digit grouping | sMonGrouping | 3;0 or 0 |\n\n"
            "Excel tip: keep 'Use system separators' checked.\n"
            "LED: Green = already configured; Red = not configured.\n"
            "Apply changes -> Sign out or reboot to apply everywhere."
        )
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        win.bind("<Escape>", lambda e: win.destroy())
        self._center_over_parent(win)

    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Decimal Settings Helper",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 6))
        ttk.Label(body, justify="center",
                  text=("A simple Windows utility to ensure consistent\n"
                        "numeric formatting for topographic / survey work.\n\n"
                        "Sets dot-decimals, disables thousands grouping,\n"
                        "and restores Greek defaults when needed.\n\n"
                        "© 2025 ALU DEV TEAM by nikkpap (nikkpap@gmail.com)")).pack(pady=(0, 10))

        ttk.Button(body, text="OK", command=win.destroy, width=10).pack()
        win.bind("<Escape>", lambda e: win.destroy())
        self._center_over_parent(win)

    def _center_over_parent(self, win: tk.Toplevel):
        win.update_idletasks()
        px, py = self.winfo_rootx(), self.winfo_rooty()
        pw, ph = self.winfo_width(), self.winfo_height()
        ww, wh = win.winfo_width(), win.winfo_height()
        x = px + (pw - ww) // 2
        y = py + (ph - wh) // 2
        win.geometry(f"+{max(0, x)}+{max(0, y)}")

# ---- Startup -----------------------------------------------------------------

def main():
    root = tk.Tk(); root.withdraw()
    if not is_admin():
        if messagebox.askyesno(APP_TITLE, "Run as Administrator? (needed for Reboot)"):
            relaunch_as_admin()
            return
    root.destroy()
    app = DecimalSettingsHelperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
