import hashlib
import re
import datetime

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def checar_rodizio(tipo, placa):
    if tipo == "Moto" or not placa: return "Isento"
    numeros = re.findall(r'\d', placa)
    if not numeros: return "Sem Rodízio"
    ultimo_digito = int(numeros[-1])
    dia_semana = datetime.date.today().weekday()
    regras = {0: [1, 2], 1: [3, 4], 2: [5, 6], 3: [7, 8], 4: [9, 0]}
    if dia_semana in regras and ultimo_digito in regras[dia_semana]: return "No Rodízio"
    return "Sem Rodízio"

