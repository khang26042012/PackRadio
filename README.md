# PikaRadio - nhac that trong game (resource pack)

Tha file `.mp3` vao `songs/` + push -> GitHub Actions tu convert sang OGG + build 2 pack:
- `PikaRadio-Java.zip` — cho Java (dat link vao `server.properties` -> `resource-pack=`)
- `PikaRadio-Bedrock.mcpack` — cho Bedrock (copy vao `plugins/Geyser-Spigot/packs/`)

Phat nhac: `/playsound pikaradio.<tenbai> music @a` (Java) / `/playsound radio.<tenbai>` (Bedrock)
Dung: `/stopsound @a music pikaradio.<tenbai>`
