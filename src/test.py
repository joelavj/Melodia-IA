from pathlib import Path

from controllers.lyrics_controller import lyrics_controller


def mini_lyrics_view():
    print("=== Mini vue paroles ===")
    song_id = int(input("Entrer l'id du morceau: "))

    print("\n1) Importer un fichier LRC")
    file_path = input("Chemin du fichier (.lrc ou .txt): (vide pour ignorer): ").strip()
    imported_lines = []
    if file_path:
        imported_lines = lyrics_controller.import_lyrics_file(file_path)
    else:
        imported_lines = [
            "Bonjour",
            "le monde",
            "Merci d'avoir choisi Melodia IA",
        ]

    print("\n2) Modifier les lignes importées")
    edited_lines = input("Entrer les lignes modifiées séparées par '|' (optionnel): ").strip()
    if edited_lines:
        imported_lines = lyrics_controller.edit_lyrics(imported_lines, edited_lines.split("|"))

    print("\n3) Générer la synchronisation manuelle")
    timestamps = [10.0, 24.0, 38.0]
    generated = lyrics_controller.generate_manual_sync(imported_lines, timestamps)
    for line in generated:
        print(line)

    print("\n4) Enregistrer les paroles")
    lyrics_controller.save_lyrics(song_id, generated)

    print("\n5) Vérification de synchronisation")
    for time_value in [5, 15, 25, 35, 45]:
        lyric = lyrics_controller.sync_lyrics(song_id, time_value)
        print(f"Temps {time_value}s -> {lyric}")


if __name__ == "__main__":
    mini_lyrics_view()