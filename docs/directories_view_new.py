import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox
from controllers.library_controller import library_controller
from controllers.directory_controller import directory_controller


class DirectoriesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#2c3e50", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header,
            text="Répertoires",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        add_btn = ctk.CTkButton(
            header,
            text="+ Ajouter",
            command=self.add_directory,
            fg_color="#1abc9c",
            text_color="white",
            width=100
        )
        add_btn.pack(side="right", padx=5, pady=10)

        self.scan_all_btn = ctk.CTkButton(
            header,
            text="Scanner tous",
            command=self.scan_all_directories,
            fg_color="#3498db",
            text_color="white",
            width=100
        )
        self.scan_all_btn.pack(side="right", padx=5, pady=10)

        self.status_var = ctk.StringVar(value="")
        status_label = ctk.CTkLabel(
            header, textvariable=self.status_var, text_color="#1abc9c", font=("Arial", 10)
        )
        status_label.pack(side="right", padx=10)

        # ===== CONTENT =====
        self.content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        self.content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh_directories()

    def refresh(self):
        """Point d'entrée utilisé par la navigation (App.changer_page)."""
        self.refresh_directories()

    def refresh_directories(self):
        """Refresh directory list"""
        for child in self.content.winfo_children():
            child.destroy()

        try:
            directories = library_controller.list_directories()

            if not directories:
                empty_label = ctk.CTkLabel(
                    self.content,
                    text="Aucun répertoire configuré",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
            else:
                for directory in directories:
                    dir_frame = ctk.CTkFrame(self.content, fg_color="#2d2d2d", corner_radius=5)
                    dir_frame.pack(fill="x", padx=5, pady=3)

                    path_label = ctk.CTkLabel(
                        dir_frame,
                        text=str(directory.path),
                        text_color="white",
                        font=("Arial", 11)
                    )
                    path_label.pack(fill="x", padx=10, pady=(8, 5))

                    btn_frame = ctk.CTkFrame(dir_frame, fg_color="#2d2d2d")
                    btn_frame.pack(fill="x", padx=10, pady=(5, 8))

                    scan_btn = ctk.CTkButton(
                        btn_frame,
                        text="Scanner",
                        command=lambda d=directory: self.scan_directory(d),
                        fg_color="#3498db",
                        text_color="white",
                        width=80,
                        height=25,
                        font=("Arial", 9)
                    )
                    scan_btn.pack(side="left", padx=5)

                    delete_btn = ctk.CTkButton(
                        btn_frame,
                        text="Supprimer",
                        command=lambda d=directory: self.delete_directory(d),
                        fg_color="#e74c3c",
                        text_color="white",
                        width=80,
                        height=25,
                        font=("Arial", 9)
                    )
                    delete_btn.pack(side="left", padx=5)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)

    def add_directory(self):
        """Add a new directory"""
        path = filedialog.askdirectory(title="Sélectionner un répertoire")
        if path:
            try:
                directory_controller.add(path)
                self.refresh_directories()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def delete_directory(self, directory):
        """Delete a directory"""
        if messagebox.askyesno("Confirmation", f"Supprimer {directory.path} ?"):
            try:
                directory_controller.remove(directory.id)
                self.refresh_directories()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

    # ----- Scan (exécuté en tâche de fond pour ne pas geler l'UI) -----

    def scan_directory(self, directory):
        self._run_scan(
            lambda: directory_controller.scan(directory.id),
            f"Scan de {directory.path} en cours..."
        )

    def scan_all_directories(self):
        self._run_scan(
            lambda: directory_controller.scan_all(),
            "Scan de tous les répertoires en cours..."
        )

    def _run_scan(self, work, message):
        self.scan_all_btn.configure(state="disabled")
        self.status_var.set(message)

        def _work():
            try:
                work()
            except Exception as e:
                print(f"Erreur pendant le scan : {e}")
            finally:
                if self.winfo_exists():
                    self.after(0, self._on_scan_done)

        threading.Thread(target=_work, daemon=True).start()

    def _on_scan_done(self):
        if not self.winfo_exists():
            return
        self.status_var.set("Scan terminé.")
        self.scan_all_btn.configure(state="normal")
        self.refresh_directories()
