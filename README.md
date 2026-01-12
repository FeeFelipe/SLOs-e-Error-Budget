# 🧭 SLO & Error Budget Lab (Docker Edition)

Projeto completo para praticar conceitos de **SLO**, **Error Budget** e **Burn Rate**, com tudo rodando em **containers Docker**.

---

## 🚀 Visão Geral

Este laboratório sobe dois componentes principais:

1. **API Demo** (FastAPI)  
   - Endpoint `/simulate` gera respostas **200** ou **500** com probabilidade configurável.  
   - Permite simular falhas e testar o comportamento da aplicação sob erro.

2. **Error Monitor** (Python)  
   - Mede taxa de sucesso da API em uma **janela deslizante**.  
   - Compara com o **SLO definido** e calcula o **Burn Rate**.  
   - Gera alertas quando o **SLO entra em risco** ou é **violado**.

---

## 📂 Estrutura do Projeto

```
slo-error-budget-lab/
├─ docker-compose.yml
├─ .env
├─ README.md
├─ services/
│  └─ api/
│     ├─ Dockerfile
│     └─ app.py
└─ tools/
   └─ error_monitor/
      ├─ Dockerfile
      ├─ entrypoint.sh
      └─ error_budget_monitor.py
```

---

## ⚙️ Subindo o Ambiente

### 1️⃣ Clonar e construir

```bash
git clone https://github.com/FeeFelipe/SLOs-e-Error-Budget.git
cd SLOs-e-Error-Budget
docker compose up --build -d
```

> **Observação:** Todas as variáveis de ambiente dos serviços estão centralizadas no arquivo `docker-compose.yml`. Não é necessário (nem recomendado) usar um arquivo `.env` neste laboratório. Para experimentar diferentes cenários, altere os valores diretamente no bloco `environment` do serviço desejado e reinicie os containers.

---

### 2️⃣ API Demo disponível

Acesse:
```
http://localhost:8080/health
```

Endpoints disponíveis:
| Endpoint | Descrição |
|-----------|------------|
| `/health` | Verifica se a API está ativa. |
| `/simulate` | Retorna 200 ou 500 com base em probabilidade (`SIM_SUCCESS_PROB`). |
| `/status/200,500` | Alterna códigos fixos, útil para simulações. |

Configuração padrão:  
`SIM_SUCCESS_PROB=0.97` → 97% das requisições retornam sucesso.

---

### 3️⃣ Monitor de Erros

O container `error-monitor` inicia automaticamente e realiza medições conforme os parâmetros:

| Variável | Descrição | Exemplo |
|-----------|------------|----------|
| `TARGET_URL` | URL alvo da API | `http://api:8080/simulate` |
| `RPM` | Requisições por minuto | `60` |
| `DURATION` | Duração do teste (s) | `600` |
| `WINDOW` | Janela deslizante (s) | `300` |
| `SLO` | Meta de sucesso (%) | `99.5` |
| `VERBOSE` | Log detalhado | `true/false` |

---

## 🔎 Logs e Alertas

Ver logs do monitor:
```bash
docker logs -f error-monitor
```

Saída típica:
```
[2025-10-21T20:15:00] window=5m samples=300 success=99.6% error=0.4% burn≈0.8x (SLO 99.5%)
[2025-10-21T20:20:00] window=5m samples=300 success=98.7% error=1.3% burn≈2.6x (SLO 99.5%) ⚠️ RISCO/VIOLAÇÃO
```

---

## 🧮 Interpretação

- **SLO 99,5%** → orçamento de erro (**Error Budget**) = 0,5%.  
- Se a taxa de erro observada for **1,5%**, então:

```
Burn Rate = 1,5 ÷ 0,5 = 3×
```

➡️ O sistema está **consumindo o Error Budget 3x mais rápido** do que o esperado.  
➡️ Alerta de risco: pode **violar o SLO** antes do final do período.

---

## 🧠 Conceitos-Chave

| Conceito | Definição |
|-----------|-----------|
| **SLI (Service Level Indicator)** | Métrica observável da experiência do usuário (ex.: taxa de sucesso). |
| **SLO (Service Level Objective)** | Meta de confiabilidade desejada (ex.: 99,9%). |
| **Error Budget** | Margem de erro permitida = `1 - SLO`. |
| **Burn Rate** | Taxa de consumo do orçamento = `Erro observado ÷ Error Budget`. |

---

## 🧩 Ajustando o Teste

Você pode alterar a probabilidade de sucesso diretamente:
```bash
curl "http://localhost:8080/simulate?ok=0.95"
```
ou ajustar no `docker-compose.yml`:
```yaml
environment:
  - SIM_SUCCESS_PROB=0.95
```

---

## 💡 Exemplo de Cenário

| Configuração | Resultado esperado |
|---------------|--------------------|
| `SLO = 99.5%`, `SIM_SUCCESS_PROB = 0.97` | dentro do esperado |
| `SLO = 99.5%`, `SIM_SUCCESS_PROB = 0.95` | violações frequentes |
| `SLO = 99.9%`, `SIM_SUCCESS_PROB = 0.97` | burn rate alto → risco alto |

---

## 📘 Próximos Passos

1. Adicionar **Prometheus + Grafana** para visualização.  
2. Integrar com **alertas automáticos (Slack / e-mail)**.  
3. Experimentar diferentes **SLIs/SLOs por endpoint**.  

---

## 🛠️ Dicas e Troubleshooting

Se você encontrar problemas ao subir o ambiente (ex: erro de build no serviço `error-monitor`), verifique se a pasta `tools/error_monitor/` e seus arquivos (`Dockerfile`, `entrypoint.sh`, `error_budget_monitor.py`) estão presentes. Caso contrário, solicite ao instrutor ou baixe novamente o repositório.

Este laboratório foi desenvolvido para fins educacionais, permitindo que você experimente conceitos de SLO, Error Budget e Burn Rate de forma prática. Explore, quebre, ajuste parâmetros e observe o impacto nos indicadores!

## 🧑‍💻 Autor
**FIAP | DevOps & SRE Lab**  
Baseado em práticas do livro *Site Reliability Engineering (Google)*.  
Adaptado para o curso de SLOs & Error Budget.
