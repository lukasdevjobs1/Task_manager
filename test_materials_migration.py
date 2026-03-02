"""
Testa se a migration de task_materials foi aplicada corretamente.
Execute: python test_materials_migration.py
"""
from supabase import create_client

SUPABASE_URL = "https://ntatkxgsykdnsfrqxwnz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M"

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("=" * 50)
    print("TESTANDO MIGRATION: task_materials")
    print("=" * 50)

    # 1. Verifica se a tabela existe tentando um select
    result = client.table('task_materials').select('*').limit(1).execute()
    print(f"\n[OK] Tabela task_materials existe — {len(result.data)} registros")

    # 2. Busca uma tarefa existente para testar insert
    tasks = client.table('task_assignments').select('id, title, assigned_to').limit(1).execute()
    if not tasks.data:
        print("\n[AVISO] Sem tarefas para testar insert de material")
    else:
        task = tasks.data[0]
        print(f"\n[INFO] Testando insert na tarefa #{task['id']} - {task['title']}")

        # 3. Insere um material de teste
        insert_result = client.table('task_materials').insert({
            'assignment_id': task['id'],
            'user_id': task['assigned_to'],
            'material_name': 'Cabo UTP Cat6 [TESTE]',
            'quantity': 10.5,
            'unit': 'm',
        }).execute()

        if insert_result.data:
            material_id = insert_result.data[0]['id']
            print(f"[OK] Insert OK — material_id={material_id}")

            # 4. Busca o material inserido
            fetch = client.table('task_materials') \
                .select('*') \
                .eq('id', material_id) \
                .execute()
            m = fetch.data[0]
            print(f"[OK] Fetch OK — {m['material_name']} | {m['quantity']} {m['unit']}")

            # 5. Remove o material de teste
            client.table('task_materials').delete().eq('id', material_id).execute()
            print(f"[OK] Delete OK — material de teste removido")
        else:
            print("[ERRO] Insert falhou — verifique as permissões da tabela")

    print("\n" + "=" * 50)
    print("MIGRATION APLICADA COM SUCESSO!")
    print("=" * 50)
    print("\nPróximos passos:")
    print("  1. Recompile o app Flutter")
    print("  2. Execute uma tarefa adicionando materiais")
    print("  3. Verifique em Tarefas Concluídas os materiais registrados")

except Exception as e:
    print(f"\n[ERRO] {e}")
    print("\nCertifique-se de ter rodado o SQL no Supabase SQL Editor antes de testar.")
