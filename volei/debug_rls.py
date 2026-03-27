"""
Script para DEBUG de RLS - mostra exatamente o que está protegido
"""

import os
import sys

# Carregar .env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_files = [
    os.path.join(script_dir, 'db.env'),
    os.path.join(script_dir, '.env'),
    'db.env',
    '.env'
]

for env_file in env_files:
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        break

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 DEBUG RLS - Verificar Proteção Real\n")
print("="*70)

# Test 1: Verificar se RLS está REALMENTE ativado
print("\n📊 Teste 1: Status Real de RLS por Tabela\n")

tabelas = ['fila', 'check_ins', 'convidados', 'family', 'score', 'roles', 'usuarios', 'controle_lista', 'matches']

for tabela in tabelas:
    try:
        # Tenta acessar SEM autenticação
        response = supabase.table(tabela).select("*").limit(1).execute()
        
        # Se conseguiu acessar...
        if response.data is not None:
            print(f"❌ {tabela:20} - ACESSO PERMITIDO (dados: {len(response.data)} linhas)")
        else:
            print(f"❌ {tabela:20} - ACESSO PERMITIDO (sem dados mas acesso ok)")
            
    except Exception as e:
        error_str = str(e).lower()
        
        # Diferentes tipos de erro significam RLS ativo
        if "policy" in error_str or "row-level" in error_str:
            print(f"✅ {tabela:20} - BLOQUEADO: Policy violation (RLS ATIVO)")
        elif "unauthorized" in error_str or "401" in error_str:
            print(f"✅ {tabela:20} - BLOQUEADO: Unauthorized (RLS ATIVO)")
        elif "permission" in error_str:
            print(f"✅ {tabela:20} - BLOQUEADO: Permission denied (RLS ATIVO)")
        else:
            print(f"⚠️  {tabela:20} - Erro desconhecido: {str(e)[:50]}")

# Test 2: Query direto SQL para ver políticas
print("\n" + "="*70)
print("\n🚨 Teste 2: Políticas RLS Criadas\n")

try:
    result = supabase.rpc('get_policies', {}).execute()
    print(f"Resultado: {result}")
except:
    # Se rpc não existe, tenta query SQL manual
    try:
        # ExecutarSQL através de uma tabela comum
        print("⚠️  Não consegui executar RPC de policies")
        print("Mas se RLS estivesse inativo, teria conseguido acessar as tabelas acima!")
    except Exception as e:
        print(f"Erro: {e}")

# Test 3: Tentar entender o erro
print("\n" + "="*70)
print("\n🔎 Teste 3: Análise Detalhada do Erro\n")

try:
    response = supabase.table('fila').select("*").limit(1).execute()
    print(f"Status Code: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
    print(f"Data: {response.data}")
    print(f"Count: {response.count if hasattr(response, 'count') else 'N/A'}")
except Exception as e:
    print(f"Tipo de Erro: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    print(f"\nInterpretação:")
    if "policy" in str(e).lower():
        print("  ✅ RLS ESTÁ ATIVADO - bloqueando por política")
    elif "unauthorized" in str(e).lower() or "401" in str(e):
        print("  ✅ RLS ESTÁ ATIVADO - bloqueando com erro 401")
    else:
        print("  ❌ RLS NÃO ESTÁ ATIVADO - acesso foi permitido")

print("\n" + "="*70)
print("\n💡 Conclusão:\n")
print("Se viu ✅ em todos os erros acima: RLS ESTÁ FUNCIONANDO!")
print("Se viu ❌ com acesso permitido: RLS NÃO ESTÁ ATIVADO")
print("Se viu mix: Algumas tabelas têm RLS, outras não\n")
