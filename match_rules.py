# match_rules.py

def match_produto(texto, produto):

    texto = texto.lower()
    p = produto.lower()

    regras = {
        "windows": [
            "windows",
            "microsoft",
            "patch tuesday",
            "windows server",
            "active directory",
            "ntlm",
            "lsass",
            "smb",
            "kerberos"
        ],
        "visual studio code": [
            "visual studio code",
            "vs code",
            "vscode",
            "visual studio marketplace",
            "openvsx"
        ],
        "docker": [
            "docker",
            "container",
            "kubernetes",
            "runc",
            "containerd"
        ]
    }

    if p in regras:
        return any(k in texto for k in regras[p])

    return p in texto
