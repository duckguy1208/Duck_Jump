$prompt = Get-Content -Raw -Path .\prompt.md
gemini -y $prompt
