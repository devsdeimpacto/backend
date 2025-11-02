# Endpoint N8N

## Configuração

Adicione no arquivo `.env` o token bearer fixo para o N8N:

```
N8N_BEARER_TOKEN=seu_token_secreto_aqui
```

## Endpoint

**POST** `/n8n/data`

### Autenticação

O endpoint requer um Bearer Token no header:

```
Authorization: Bearer seu_token_secreto_aqui
```

### Request Body

O endpoint aceita um JSON com as seguintes entidades (todas opcionais):

```json
{
  "user": {
    "whatsapp_number": "5511999999999",
    "whatsapp_id": "123456",
    "name": "João Silva"
  },
  "report": {
    "user_id": "uuid-do-usuario",
    "latitude": -23.550520,
    "longitude": -46.633308,
    "address": "Rua Exemplo, 123",
    "description": "Descrição do problema",
    "image_url": "https://exemplo.com/imagem.jpg",
    "category": "lixo_doméstico",
    "status": "pending"
  },
  "classification": {
    "report_id": "uuid-do-report",
    "problema_identificado": true,
    "category": "lixo_doméstico",
    "confidence": 0.95,
    "ai_model": "gpt-4",
    "local_aparente": "Via pública",
    "tipo_despejo": ["lixo doméstico", "entulho"],
    "gravidade": "alta",
    "risco_saude": true,
    "impacto_meio_ambiente": "Alto impacto ambiental",
    "populacao_prejudicada": "Comunidade local",
    "descricao_resumida": "Descarte irregular de lixo",
    "acoes_recomendadas": [
      "Limpeza imediata",
      "Fiscalização"
    ]
  }
}
```

### Resposta

**Status 201 - Created**

```json
{
  "message": "Dados criados com sucesso: User uuid, Report uuid, Classification uuid"
}
```

**Status 401 - Unauthorized**

```json
{
  "detail": "Token inválido"
}
```

**Status 400 - Bad Request**

```json
{
  "detail": "Erro ao criar dados: detalhes do erro"
}
```

## Exemplo de uso com curl

```bash
curl -X POST "http://localhost:8000/n8n/data" \
  -H "Authorization: Bearer seu_token_secreto_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "whatsapp_number": "5511999999999",
      "whatsapp_id": "123456",
      "name": "João Silva"
    },
    "report": {
      "user_id": "uuid-do-usuario",
      "latitude": -23.550520,
      "longitude": -46.633308,
      "description": "Problema identificado"
    }
  }'
```

## Observações

- Você pode enviar apenas uma entidade, duas ou todas as três
- Todas as entidades são opcionais no body
- O token é fixo e deve estar no arquivo `.env`
- O endpoint valida o token antes de processar os dados
- Se houver erro, a transação é revertida (rollback)

