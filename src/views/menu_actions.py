import tkinter as tk
from controllers.queue_controller import queue_controller
from controllers.player_controller import player_controller
from controllers.favori_controller import favori_controller
from controllers.playlist_controller import playlist_controller
from controllers.library_controller import library_controller


def build_song_context_menu(
    parent_widget,
    song_ids: list[int],
    on_after_action=None,
    favori_state: bool | None = None,
    on_toggle_favori=None,
    on_details=None,
    play_label: str = "Lire",
):
    """Construit le menu ⋮ commun (album/artiste/morceau).

    song_ids : identifiants de morceaux concernés par cette entrée (un seul
    pour un morceau, tous ceux de l'album/artiste sinon).
    favori_state / on_toggle_favori : uniquement pertinent pour un morceau
    unique, pour proposer "Ajouter"/"Retirer des favoris".
    on_details : callback optionnel pour "Voir les détails".
    """
    menu = tk.Menu(parent_widget, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")

    def _finish():
        if on_after_action:
            on_after_action()

    def _play():
        if song_ids:
            queue_controller.clear_queue()
            for id_song in song_ids:
                queue_controller.add_song(id_song)
            player_controller.play_song(song_ids[0])
        _finish()

    def _add_queue():
        for id_song in song_ids:
            queue_controller.add_song(id_song)
        _finish()

    def _add_favori():
        for id_song in song_ids:
            favori_controller.add_favori(id_song)
        _finish()

    def _remove_favori():
        for id_song in song_ids:
            favori_controller.remove_favori(id_song)
        _finish()

    def _add_to_playlist(id_playlist):
        for id_song in song_ids:
            playlist_controller.add_song(id_playlist, id_song)
        _finish()

    menu.add_command(label=play_label, command=_play)
    menu.add_command(label="Ajouter à la file d'attente", command=_add_queue)

    if favori_state is not None and on_toggle_favori is not None:
        if favori_state:
            menu.add_command(label="Retirer des favoris", command=on_toggle_favori)
        else:
            menu.add_command(label="Ajouter aux favoris", command=on_toggle_favori)
    else:
        menu.add_command(label="Ajouter aux favoris", command=_add_favori)

    playlist_menu = tk.Menu(menu, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")
    playlists = library_controller.list_playlists()
    if not playlists:
        playlist_menu.add_command(label="Aucune playlist", state="disabled")
    for playlist in playlists:
        playlist_menu.add_command(
            label=playlist.name,
            command=lambda p=playlist: _add_to_playlist(p.id)
        )
    menu.add_cascade(label="Ajouter à une playlist", menu=playlist_menu)

    if on_details:
        menu.add_separator()
        menu.add_command(label="Voir les détails", command=on_details)

    return menu
