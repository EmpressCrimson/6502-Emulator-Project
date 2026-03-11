"""
EmulatorDashboard — 6502 CPU state visualiser
A pure-display widget: setter-only, no getters.
"""

import tkinter as tk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex2(val: int) -> str:
    return f"${val & 0xFF:02X}"

def _hex4(val: int) -> str:
    return f"${val & 0xFFFF:04X}"

def _bin8(val: int) -> str:
    return f"%{val & 0xFF:08b}"

def _dec(val: int) -> str:
    return str(val & 0xFF)


# ---------------------------------------------------------------------------
# EmulatorDashboard
# ---------------------------------------------------------------------------

class EmulatorDashboard(tk.Tk):
    """
    6502 CPU state dashboard.

    Setters
    -------
    set_pc(value: int)          — always updates, even in Turbo mode
    set_a(value: int)
    set_x(value: int)
    set_y(value: int)
    set_sp(value: int)
    set_status(value: int)      — updates P register display
    set_turbo(enabled: bool)    — programmatic Turbo toggle
    """

    # Ordered flag names for the status register (bit 7 → bit 0)
    _FLAG_NAMES = ["N", "V", "-", "B", "D", "I", "Z", "C"]

    def __init__(self):
        super().__init__()
        self.title("6502 CPU Dashboard")
        self.resizable(False, False)
        self._turbo_var = tk.BooleanVar(value=False)
        self._turbo: bool = False
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        BACKGROUND       = "#1e1e2e"
        BACKGROUND_CELL  = "#181825"
        BACKGROUND_EDGE  = "#313244"
        FOREGROUND_TITLE = "#cdd6f4"
        FOREGROUND_NAME  = "#a6e3a1"
        FOREGROUND_VALUE   = "#cdd6f4"
        FOREGROUND_DIM   = "#6c7086"
        MONO     = ("Courier", 11, "bold")
        MONO_SM  = ("Courier", 13, "bold")

        outer = tk.Frame(self, bg=BACKGROUND, padx=12, pady=12)
        outer.pack(fill="both", expand=True)

        # ── Title ────────────────────────────────────────────────────────
        tk.Label(outer, text="6502  CPU  DASHBOARD",
                 font=("Courier", 14, "bold"),
                 bg=BACKGROUND, fg=FOREGROUND_TITLE).pack(pady=(0, 10))

        SEP = ("Courier", 11)   # dimmed separator between values

        def card(parent, name: str) -> tk.Frame:
            """A titled card; values are packed horizontally inside it."""
            border = tk.Frame(parent, bg=BACKGROUND_EDGE, padx=1, pady=1)
            border.pack(side="left", padx=4, pady=2)
            inner = tk.Frame(border, bg=BACKGROUND_CELL, padx=10, pady=6)
            inner.pack(fill="both", expand=True)
            tk.Label(inner, text=name, bg=BACKGROUND_CELL, fg=FOREGROUND_NAME,
                     font=MONO_SM, anchor="w").pack(anchor="w")
            val_row = tk.Frame(inner, bg=BACKGROUND_CELL)
            val_row.pack(anchor="w")
            return val_row

        def val(parent, initial: str) -> tk.StringVar:
            """One value chunk on the horizontal value row."""
            var = tk.StringVar(value=initial)
            tk.Label(parent, textvariable=var, bg=BACKGROUND_CELL, fg=FOREGROUND_VALUE,
                     font=MONO).pack(side="left")
            return var

        def sep(parent):
            tk.Label(parent, text="  ", bg=BACKGROUND_CELL, font=SEP,
                     fg=FOREGROUND_DIM).pack(side="left")

        # ── Row 1: PC  |  SP ─────────────────────────────────────────────
        row1 = tk.Frame(outer, bg=BACKGROUND)
        row1.pack(fill="x", pady=2)

        vr = card(row1, "PC")
        self._pc_hex = val(vr, "$0000")

        vr = card(row1, "SP")
        self._sp_hex = val(vr, "$FF")
        sep(vr)
        self._sp_dec = val(vr, "255")

        # ── Row 2: A  |  X  |  Y ─────────────────────────────────────────
        row2 = tk.Frame(outer, bg=BACKGROUND)
        row2.pack(fill="x", pady=2)

        vr = card(row2, "A")
        self._a_hex = val(vr, "$00")
        sep(vr)
        self._a_dec = val(vr, "0")
        sep(vr)
        self._a_bin = val(vr, "%00000000")

        vr = card(row2, "X")
        self._x_hex = val(vr, "$00")
        sep(vr)
        self._x_dec = val(vr, "0")
        sep(vr)
        self._x_bin = val(vr, "%00000000")

        vr = card(row2, "Y")
        self._y_hex = val(vr, "$00")
        sep(vr)
        self._y_dec = val(vr, "0")
        sep(vr)
        self._y_bin = val(vr, "%00000000")

        # ── Row 3: Status register ────────────────────────────────────────
        row3 = tk.Frame(outer, bg=BACKGROUND)
        row3.pack(fill="x", pady=2)

        # For the status card we need both the val_row AND the inner frame
        sr_border = tk.Frame(row3, bg=BACKGROUND_EDGE, padx=1, pady=1)
        sr_border.pack(side="left", padx=4, pady=2)
        sr_card = tk.Frame(sr_border, bg=BACKGROUND_CELL, padx=10, pady=6)
        sr_card.pack(fill="both", expand=True)
        tk.Label(sr_card, text="P  (Status)", bg=BACKGROUND_CELL, fg=FOREGROUND_NAME,
                 font=MONO_SM, anchor="w").pack(anchor="w")
        sr_vr = tk.Frame(sr_card, bg=BACKGROUND_CELL)
        sr_vr.pack(anchor="w")
        self._sr_hex = val(sr_vr, "$00")
        sep(sr_vr)

        # "%" prefix then one label per bit — guarantees flag names align below
        tk.Label(sr_vr, text="%", bg=BACKGROUND_CELL, fg=FOREGROUND_VALUE,
                 font=MONO).pack(side="left")
        self._bit_labels: list[tk.Label] = []
        for _ in range(8):
            bl = tk.Label(sr_vr, text="0", bg=BACKGROUND_CELL, fg=FOREGROUND_VALUE,
                          font=MONO, width=2, anchor="center")
            bl.pack(side="left")
            self._bit_labels.append(bl)

        # Flag-name strip — sits directly under the bit labels
        flag_row = tk.Frame(sr_card, bg=BACKGROUND_CELL)
        flag_row.pack(anchor="w")

        # Spacer to match "$XX  %" prefix so names sit under bits
        tk.Label(flag_row, text="      ", bg=BACKGROUND_CELL,
                 font=MONO).pack(side="left")

        self._flag_labels: list[tk.Label] = []
        for name in self._FLAG_NAMES:
            lbl = tk.Label(flag_row, text=name,
                           bg=BACKGROUND_CELL, fg="#89b4fa",
                           font=MONO, width=2, anchor="center")
            lbl.pack(side="left")
            self._flag_labels.append(lbl)

        # ── Turbo checkbox ────────────────────────────────────────────────
        turbo_frame = tk.Frame(outer, bg=BACKGROUND)
        turbo_frame.pack(fill="x", pady=(10, 0))

        self._turbo_var.trace_add("write", lambda *_: self._sync_turbo())
        tk.Checkbutton(
            turbo_frame,
            text=" ⚡ Turbo  (PC-only updates)",
            variable=self._turbo_var,
            bg=BACKGROUND, fg="#f38ba8",
            selectcolor=BACKGROUND_EDGE,
            activebackground=BACKGROUND,
            activeforeground="#f38ba8",
            font=("Courier", 11, "bold"),
            cursor="hand2",
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Public setters
    # ------------------------------------------------------------------

    def set_pc(self, value: int):
        """Always updates — even in Turbo mode."""
        self._pc_hex.set(_hex4(value))

    def _set_byte_register(self, hex_var, bin_var, dec_var, value: int):
        hex_var.set(_hex2(value))
        bin_var.set(_bin8(value))
        dec_var.set(_dec(value))

    def set_a(self, value: int):
        if self._turbo:
            return
        self._set_byte_register(self._a_hex, self._a_bin, self._a_dec, value)

    def set_x(self, value: int):
        if self._turbo:
            return
        self._set_byte_register(self._x_hex, self._x_bin, self._x_dec, value)

    def set_y(self, value: int):
        if self._turbo:
            return
        self._set_byte_register(self._y_hex, self._y_bin, self._y_dec, value)

    def set_sp(self, value: int):
        if self._turbo:
            return
        self._sp_hex.set(_hex2(value))
        self._sp_dec.set(_dec(value))

    def set_status(self, value: int):
        """
        Update the P (status) register display.
        Each bit is its own label so flag names align perfectly below.
        Set bits → bright amber digit + bright flag name; clear → dim.
        """
        if self._turbo:
            return
        v = value & 0xFF
        self._sr_hex.set(_hex2(v))
        for i, (bl, fl) in enumerate(zip(self._bit_labels, self._flag_labels)):
            bit = (v >> (7 - i)) & 1
            bl.config(text=str(bit),
                      fg="#f9e2af" if bit else "#585b70")
            fl.config(fg="#f9e2af" if bit else "#45475a")

    def set_turbo(self, enabled: bool):
        """Programmatic turbo toggle (mirrors the checkbox)."""
        self._turbo = enabled
        self._turbo_var.set(enabled)

    def _sync_turbo(self):
        """Called when the checkbox changes; keeps the bool in sync."""
        self._turbo = self._turbo_var.get()


# ---------------------------------------------------------------------------
# Quick smoke-test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = EmulatorDashboard()
    app.set_pc(0x1234)
    app.set_a(0xAB)
    app.set_x(0x0F)
    app.set_y(0xFF)
    app.set_sp(0xFD)
    app.set_status(0b10110001)   # N, B, D, C set
    app.mainloop()
