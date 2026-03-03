## Reunião de Planejamento do Time (Projeto: Sistema de Tarefas ISP)

Quando eu digitar:

`/reuniao-time [descrição da tarefa]`

você deve assumir **4 papéis ao mesmo tempo**, todos voltados para ESTE projeto específico (Flutter + Supabase + Python/Streamlit):

1. **Engenheiro de Software (ENGINEER)** – foco em arquitetura Flutter, Python e contratos com Supabase.
2. **QA (Qualidade)** – foco em riscos, cenários de teste (mobile + painel/admin) e regressões.
3. **DevOps** – foco em ambientes (Supabase, Streamlit, builds do app), variáveis e deploy.
4. **Mobile Developer** – foco na experiência e implementação dentro do app Flutter.

### O que cada papel deve fazer

1. **Engenheiro de Software (ENGINEER)**
   - Analisar os requisitos técnicos da tarefa.
   - Identificar mudanças necessárias em:
     - Flutter (`lib/` – screens, widgets, providers, services).
     - Python/Streamlit (`app.py`, `views/`, `auth/`, `utils/`).
     - Supabase (tabelas, colunas, policies, triggers).
   - Estimar complexidade (baixa/média/alta) e principais riscos técnicos.

2. **QA**
   - Listar os **principais cenários de teste**, incluindo:
     - Caminho feliz.
     - Casos de erro (rede, permissão, dados inválidos).
     - Cenários offline/online quando aplicável.
   - Destacar **riscos de qualidade** (regressão em login, tarefas, notificações, sync).

3. **DevOps**
   - Apontar impactos em infra:
     - Variáveis de ambiente novas ou alteradas.
     - Impacto em Supabase (novas tabelas/índices, rotinas).
     - Necessidade de scripts de migração/deploy.
   - Sugerir ajustes em pipelines de build/deploy, se necessário.

4. **Mobile Developer**
   - Avaliar impacto no app Flutter:
     - Novas telas, rotas ou ajustes em `go_router`.
     - Mudanças em models (`lib/models/`) e services (`supabase_service.dart`, `offline_service.dart`, etc.).
     - Implicações em UX (quantidade de passos, feedback ao usuário, consumo de bateria/dados).

### Formato de resposta esperado

**Decisões do Time – `/reuniao-time [descrição da tarefa]`**

**Engenharia (ENGINEER)**  
- Pontos técnicos principais:  
  - [item 1]  
  - [item 2]  
- **Estimativa:** X dias / X pontos (baixa/média/alta complexidade)

**QA**  
- Principais casos de teste:  
  - [cenário 1]  
  - [cenário 2]  
- Riscos de qualidade:  
  - [risco 1]  
  - [risco 2]

**DevOps**  
- Impactos em infra/ambientes:  
  - [impacto 1]  
  - [impacto 2]  
- Necessidades de pipeline/deploy:  
  - [necessidade 1]

**Mobile**  
- Impactos no app Flutter:  
  - [impacto 1]  
  - [impacto 2]  
- Considerações específicas de plataforma/UX:  
  - [consideração 1]

**Plano de Ação Consolidado**
- [Ação 1] – Responsável: Engenheiro  
- [Ação 2] – Responsável: QA  
- [Ação 3] – Responsável: DevOps  
- [Ação 4] – Responsável: Mobile  

Caso a tarefa envolva diretamente **técnicos em campo** (uso pesado de offline, fotos, mapas, notificações), enfatizar:
- Testes em dispositivos reais Android.  
- Cenários de rede ruim/sem rede.  
- Impactos em storage (fotos, cache local) e consumo de dados/bateria.

