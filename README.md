# 5T4RBUG

MVP de uma ferramenta pessoal de gestão de tarefas, feito para estudo com Python, Flask, Jinja e SQLite/PostgreSQL.

## Rodar localmente com SQLite

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"
export SECRET_KEY="cole-a-chave-gerada-aqui"
.venv/bin/python run.py
```

Abra <http://127.0.0.1:5000>.

Sem `DATABASE_URL`, o banco local é criado em `instance/5t4rbug.sqlite3`. Ele está no `.gitignore` porque contém dados pessoais. Nunca coloque a `SECRET_KEY` ou uma URL de banco no Git.

## O que este MVP oferece

- Cadastro com e-mail e senha forte (mínimo de 12 caracteres).
- Senhas armazenadas com hash adaptativo `scrypt`, nunca em texto puro.
- Sessão server-side: o cookie de autenticação contém somente um token aleatório e o banco guarda apenas seu hash.
- Logout que revoga a sessão.
- Proteção CSRF para operações que alteram dados.
- Cada usuário só consulta e altera suas próprias tarefas.
- Tarefas com prioridade, status, descrição e prazo.
- Cabeçalhos HTTP básicos e limite de requisição.
- SQLite local para estudo e PostgreSQL quando `DATABASE_URL` estiver configurado.

## Publicar gratuitamente para teste: Render Free + Neon Free

Esta é a opção recomendada para colocar o beta nas mãos dos seus amigos sem Persistent Disk pago:

```text
GitHub → Render Web Service Free → Neon PostgreSQL Free
```

O Render Free não deve guardar o SQLite: o filesystem é temporário e o serviço pode dormir depois de 15 minutos sem acesso. Por isso, o código usa PostgreSQL externo quando `DATABASE_URL` existe. A aplicação pode demorar cerca de um minuto para acordar no primeiro acesso.

### 1. Criar o banco no Neon

1. Crie uma conta em [Neon](https://neon.tech/).
2. Crie um projeto PostgreSQL gratuito.
3. Copie a connection string, mantendo o `sslmode=require` quando ele aparecer.
4. Não publique essa string no GitHub; ela contém senha do banco.

O plano Free atual do Neon informa US$ 0/mês, sem cartão obrigatório, 100 projetos, 100 CU-hours por projeto/mês e 0,5 GB de armazenamento por projeto. Consulte [Neon Pricing](https://neon.com/pricing), pois limites podem mudar.

### 2. Criar o Blueprint no Render

1. Acesse [Render](https://render.com/) e entre com GitHub.
2. Escolha **New → Blueprint**.
3. Selecione o repositório privado `H3C4SCR/5t4rbug`.
4. Confirme o `render.yaml`.
5. Quando o painel pedir `DATABASE_URL`, cole a connection string do Neon.
6. Confirme o plano **Free** e crie o serviço.
7. Aguarde o deploy e abra o endereço `*.onrender.com`.

O `render.yaml` configura o plano Free, Gunicorn, HTTPS gerenciado e `SESSION_COOKIE_SECURE=true`. A `SECRET_KEY` é gerada pela Render. Não há Persistent Disk nem cobrança de servidor nesse Blueprint.

A documentação oficial informa que Web Services Free têm filesystem efêmero, dormem após 15 minutos sem tráfego e contam com horas mensais incluídas. O Render Postgres Free expira após 30 dias, por isso este projeto usa Neon para não depender desse prazo. Consulte [Render Free](https://render.com/docs/free) e [Render Web Services](https://render.com/docs/web-services).

### 3. Testar com os amigos

Use apenas dados fictícios nesta fase. Teste cadastro, login, tarefas, filtros e acesso por celular. O primeiro acesso após inatividade pode ser lento por causa do modo de suspensão.

Antes de usar informações reais, confirme que você possui uma política de privacidade, retenção/exclusão de dados, backups e revisão de segurança. Esta configuração gratuita é para beta e aprendizado, não uma garantia de disponibilidade ou conformidade jurídica.

## Deploy pago anterior

O arquivo `render.yaml` atual é a configuração gratuita com Neon. Para uma versão paga com banco local persistente, seria necessário voltar a usar Persistent Disk e SQLite ou migrar para um banco gerenciado pago.

## Como estudar o código

1. Comece em `run.py`: ele cria a aplicação.
2. Siga `app/__init__.py`: factory, banco, hooks e cabeçalhos.
3. Leia `app/db.py`: ele escolhe SQLite local ou PostgreSQL por `DATABASE_URL`.
4. Leia `app/auth/service.py` para entender hash, sessão e CSRF.
5. Leia `app/auth/routes.py` para acompanhar cadastro e login.
6. Leia `app/main/routes.py` para o CRUD de tarefas.
7. Veja `app/schema.sql` e `app/schema_postgres.sql` para comparar os bancos.

## Limites importantes

Este é um MVP educacional. HTTPS e segredo ficam configurados no Render, mas ainda são necessários rate limiting persistente, backups protegidos testados, monitoramento, política de privacidade, canal para solicitações de titulares, regras de retenção/eliminação e revisão profissional de segurança e LGPD. O código não é certificação de conformidade jurídica.
