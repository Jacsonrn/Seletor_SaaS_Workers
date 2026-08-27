import struct
import sys
import os
import random

# =========================================================
# FASE 5: POLIMORFISMO (OPCODES DINAMICOS E JUNK CODE)
# =========================================================

# 1. Geracao Dinamica de OpCodes
# A cada execucao, os valores dos bytes mudam, quebrando assinaturas estaticas.
INSTRUCTION_NAMES = [
    'NOP', 'PUSH', 'POP', 'ADD', 'SUB', 'MUL', 'XOR', 
    'CMP', 'JMP', 'JE', 'JNE', 'LOAD_REG', 'STORE_REG', 'EXIT'
]

available_bytes = list(range(256))
random.shuffle(available_bytes)
OPCODES = {name: available_bytes.pop() for name in INSTRUCTION_NAMES}

def compile_source(source_code):
    """
    Compila codigo assembly customizado para bytecode.
    Suporta labels (ex: :inicio) e comentarios (#).
    """
    lines = source_code.splitlines()
    bytecode = []
    labels = {}      # Nome da label -> Endereco (byte index)
    jumps = []       # Lista de (index_no_bytecode, nome_label, instrucao) para resolver depois

    # --- PASSAGEM 1: Gerar bytecode e registrar labels ---
    for line in lines:
        # Remove comentarios inline para evitar sujeira no parsing
        if '#' in line:
            line = line.split('#')[0]
        if '//' in line:
            line = line.split('//')[0]
            
        line = line.strip()
        if not line:
            continue

        # Definicao de Label (ex: ":sucesso")
        if line.startswith(':'):
            label_name = line[1:]
            labels[label_name] = len(bytecode)
            continue

        parts = line.split()
        instr = parts[0].upper()
        args = parts[1:]

        if instr not in OPCODES:
            print(f"[ERRO] Instrucao desconhecida: {instr}")
            sys.exit(1)

        # FASE 5: Insercao de Junk Code (Instrucoes Lixo)
        # Insere NOPs aleatorios para mudar o offset e a assinatura do arquivo
        if random.random() < 0.3: # 30% de chance de inserir lixo antes da instrucao
            bytecode.append(OPCODES['NOP'])

        opcode = OPCODES[instr]
        bytecode.append(opcode)

        # Tratamento de argumentos por tipo de instrucao
        if instr == 'PUSH':
            # PUSH <int> (4 bytes)
            val = int(args[0])
            bytecode.extend(list(struct.pack('<i', val))) # <i = Little Endian Int32
            
        elif instr in ['JMP', 'JE', 'JNE']:
            # JMP <label> (4 bytes placeholder)
            target_label = args[0]
            # Remove os dois pontos se o usuario usou na referencia (ex: JMP :fim -> fim)
            if target_label.startswith(':'):
                target_label = target_label[1:]
            # Guardamos a posicao onde o offset deve ser escrito (len(bytecode))
            jumps.append((len(bytecode), target_label, instr))
            bytecode.extend([0, 0, 0, 0]) # Placeholder de 4 bytes
            
        elif instr in ['LOAD_REG', 'STORE_REG']:
            # LOAD_REG <index> (1 byte)
            val = int(args[0])
            bytecode.append(val)

    # --- PASSAGEM 2: Resolver Pulos (Labels) ---
    for jump_idx, label_name, instr in jumps:
        if label_name not in labels:
            print(f"[ERRO] Label nao encontrada: {label_name}")
            sys.exit(1)
        
        target_addr = labels[label_name]
        # O offset é relativo à instrução SEGUINTE ao salto na nossa VM simplificada?
        # Ou relativo ao inicio? Vamos usar relativo ao inicio da instrucao de salto para simplificar a VM.
        # VM: vIP += offset. Se offset for relativo, vIP = target.
        # Vamos calcular o offset relativo: target - (jump_idx + 4 bytes do arg)
        # Mas para simplificar a VM (vIP += offset), vamos gravar o offset relativo.
        
        # Na VM: vIP aponta para o proximo byte.
        # Quando lemos o offset (4 bytes), vIP avanca 4.
        # Entao o salto deve compensar.
        
        current_ip = jump_idx + 4 # Onde o IP estara apos ler o argumento
        offset = target_addr - current_ip
        
        # Escreve o offset calculado no lugar do placeholder
        offset_bytes = list(struct.pack('<i', offset))
        for i in range(4):
            bytecode[jump_idx + i] = offset_bytes[i]

    return bytecode

def generate_header(bytecode, output_file="LicenseLogic.h"):
    var_name = "LICENSE_CHECK_BYTECODE"
    
    # FASE 3: Criptografia Estatica (XOR)
    # Usamos uma chave fixa (0xAA) para ofuscar o bytecode no disco.
    # Na Fase 4, a VM descriptografara byte a byte em tempo de execucao.
    xor_key = 0xAA
    encrypted_bytecode = [b ^ xor_key for b in bytecode]
    
    content = f"""#ifndef LICENSE_LOGIC_H
#define LICENSE_LOGIC_H

// ARQUIVO GERADO AUTOMATICAMENTE PELO VM_COMPILER.PY
// NAO EDITE MANUALMENTE.
// Tamanho: {len(bytecode)} bytes
// Criptografia: XOR (Key: 0x{xor_key:02X})

const unsigned char LICENSE_CHECK_KEY = 0x{xor_key:02X};

const unsigned char {var_name}[] = {{
"""
    
    # Formata como hex C++ (12 bytes por linha)
    hex_bytes = [f"0x{b:02X}" for b in encrypted_bytecode]
    for i in range(0, len(hex_bytes), 12):
        row = hex_bytes[i:i+12]
        content += "    " + ", ".join(row) + ",\n"
        
    content += f"""}};

const int {var_name}_SIZE = {len(bytecode)};

#endif // LICENSE_LOGIC_H
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    print(f"[SUCESSO] {output_file} gerado com sucesso!")

def generate_opcodes_header(output_file="VMOpcodes.h"):
    """
    Gera o arquivo header C++ com os OpCodes aleatorios definidos nesta execucao.
    """
    content = "#ifndef VM_OPCODES_H\n#define VM_OPCODES_H\n\n"
    content += "#include <cstdint>\n\n"
    content += "// ARQUIVO GERADO DINAMICAMENTE - NAO EDITE\n"
    content += "// FASE 5: Polimorfismo de OpCodes\n"
    content += "enum VMOpCode : uint8_t {\n"
    
    for name, val in OPCODES.items():
        content += f"    VM_{name} = 0x{val:02X},\n"
        
    content += "};\n\n#endif // VM_OPCODES_H\n"
    
    with open(output_file, "w") as f:
        f.write(content)
    print(f"[SUCESSO] {output_file} gerado com sucesso!")

# --- LOGICA DE VALIDACAO (CODIGO FONTE ASSEMBLY) ---
# R0 = Input (Checksum da resposta do servidor)
# R4 = Output (Resultado do calculo secreto)
# Logica: Se R0 == 368, retorna (R0 + 1000) * 2. Senao retorna 0.
# Resultado esperado para 368: (368 + 1000) * 2 = 2736
# 2736 em hex = 0x0AB0. Byte baixo = 0xB0 (176).
SOURCE_CODE = """
    LOAD_REG 0      # Carrega o valor de entrada (R0) para a pilha
    PUSH 368        # Empilha o checksum esperado de "VALID"
    CMP             # Compara
    JNE :falha      # Se nao for igual, pula para :falha
    
    # Sucesso: Realiza calculo secreto
    LOAD_REG 0      # Carrega 368 de novo
    PUSH 1000       # Soma 1000 -> 1368
    ADD
    PUSH 2          # Multiplica por 2 -> 2736
    MUL
    STORE_REG 4     # R4 = Resultado
    EXIT

:falha
    PUSH 0
    STORE_REG 4     # R4 = 0
    EXIT
"""

if __name__ == "__main__":
    bc = compile_source(SOURCE_CODE)
    generate_opcodes_header() # Gera o header C++ com os opcodes sorteados
    generate_header(bc)