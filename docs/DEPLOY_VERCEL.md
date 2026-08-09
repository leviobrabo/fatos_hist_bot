# Deploy da Mini App na Vercel

## Arquitetura

- `public/`: interface estática do Museu Histórico.
- `api/index.py`: Python Function no runtime atual da Vercel.
- MongoDB: estado persistente compartilhado com o bot.
- Telegram: identidade validada no servidor pelo HMAC de `initData`.

A API de gerenciamento da Vercel não é necessária durante a execução da Mini App. Ela serve para automatizar projetos, deployments e variáveis. A conexão de runtime é feita pelo domínio HTTPS da Function e pelo MongoDB configurado em ambiente.

## Variáveis obrigatórias

Configure nos ambientes Production, Preview e Development do projeto Vercel:

- `BOT_TOKEN`: token do BotFather; nunca exponha no frontend.
- `MONGO_CON`: conexão MongoDB com acesso ao banco `fatoshistbot`.
- `OWNER_ID`: ID numérico do proprietário, usado para liberar o painel administrativo e preparar sugestões aprovadas.

No processo principal do bot, configure também:

- `MINI_APP_URL=https://seu-projeto.vercel.app`
- `CLUB_STARS=100` (ou outro preço inteiro em Stars)

## Publicação

1. Importe o repositório na Vercel ou execute `vercel` na raiz.
2. Cadastre as variáveis acima no painel da Vercel.
3. Faça o deployment e teste `https://seu-dominio/api?action=health`.
4. No BotFather, defina o domínio/menu button da Mini App para a URL publicada.
5. Atualize `MINI_APP_URL` onde o bot principal roda e reinicie o processo.

Não use a URL de Preview no BotFather para produção. O backend rejeita `initData` inválido ou com mais de 24 horas.

### Rede do MongoDB

As Functions usam endereços de saída dinâmicos por padrão. Se o MongoDB exigir allowlist de IP, use **Static IPs** da Vercel (Pro/Enterprise), selecione uma região próxima do cluster em `Connectivity` e autorize no MongoDB somente o par de IPs fornecido. Em Enterprise, Secure Compute permite uma rede privada dedicada. Evite liberar `0.0.0.0/0`; se isso for indispensável em um protótipo, use credencial exclusiva, senha forte, TLS e permissões mínimas no banco.

O `MongoClient` fica em cache entre invocações quentes, reduzindo conexões e latência. Ainda assim, mantenha a Function e o cluster na mesma região sempre que possível.

## Automação opcional pela API da Vercel

Se houver CI próprio, use um token de acesso Vercel somente no CI para criar deployments e gerenciar variáveis. Esse token não pertence ao bot nem ao navegador da Mini App. Prefira integração Git para o fluxo normal.
