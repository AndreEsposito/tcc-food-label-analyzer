from pathlib import Path


PROVIDER_XML = """
        <provider
            android:name="br.com.ingresense.IngreSenseFileProvider"
            android:authorities="br.com.ingresense.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true" />
"""


def before_apk_assemble(toolchain):
    manifest_path = Path("src/main/AndroidManifest.xml")
    if not manifest_path.exists():
        print("[p4a_hooks] AndroidManifest.xml nao encontrado para inserir provider.")
        return

    manifest = manifest_path.read_text(encoding="utf-8")
    if "br.com.ingresense.IngreSenseFileProvider" in manifest:
        return

    manifest = manifest.replace("    </application>", PROVIDER_XML + "    </application>")
    manifest_path.write_text(manifest, encoding="utf-8")
    print("[p4a_hooks] Provider da camera inserido no AndroidManifest.xml.")
