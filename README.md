# 5T4RBUG

MVP de uma ferramenta pessoal de gestão de tarefas, feito para estudo com Python, Flask, SQLite e Jinja.

## Rodar localmente

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"
export SECRET_KEY="cole-a-chave-gerada-aqui"
.venv/bin/python run.py
```

Abra <http://127.0.0.1:5000>.

O banco é criado em `instance/5t4rbug.sqlite3`. Ele está no `.gitignore` porque contém dados pessoais. Nunca coloque a `SECRET_KEY` no Git.

## O que este MVP oferece

- Cadastro com e-mail e senha forte (mínimo de 12 caracteres).
- Senhas armazenadas com hash adaptativo `scrypt`, nunca em texto puro.
- Sessão server-side em SQLite: o cookie de autenticação contém somente um token aleatório e o banco guarda apenas seu hash.
- Logout que revoga a sessão.
- Proteção CSRF para operações que alteram dados.
- Cada usuário só consulta e altera suas próprias tarefas.
- Tarefas com prioridade, status, descrição e prazo.
- Cabeçalhos HTTP básicos e limite de requisição.

## Publicar na internet com Render

O arquivo `render.yaml` já contém a configuração de deploy. O MVP usa SQLite, então o serviço precisa de um Persistent Disk: sem ele, o filesystem da aplicação é temporário e o banco poderia ser perdido em reinícios ou novos deploys. O disco está montado em `/var/data`, e `DATABASE_PATH` aponta o banco para esse local.

1. Crie um repositório privado no GitHub e envie este projeto, sem incluir `.venv`, `.env` ou `instance/*.sqlite3`.
2. Crie uma conta em [Render](https://render.com/) e conecte sua conta GitHub.
3. No painel, escolha **New → Blueprint** e selecione o repositório.
4. Confirme o `render.yaml`. Ele cria um Web Service Python com Gunicorn, HTTPS gerenciado, segredo aleatório e disco persistente de 1 GB.
5. Aguarde o deploy e abra o endereço `*.onrender.com` fornecido pela plataforma.
6. No primeiro acesso, crie sua conta normalmente.

O plano com Persistent Disk é pago e o disco só preserva arquivos escritos em `/var/data`. O SQLite deste MVP funciona com uma única instância; não habilite escala horizontal. Para mais usuários, migre o banco para PostgreSQL antes de escalar.

Referências oficiais: [Web Services](https://render.com/docs/web-services), [Persistent Disks](https://render.com/docs/disks), [variáveis e segredos](https://render.com/docs/configure-environment-variables) e [Blueprint YAML](https://render.com/docs/blueprint-spec).

## Limites importantes

Este é um MVP educacional. HTTPS e segredo ficam configurados no Render, mas ainda são necessários rate limiting persistente, backups protegidos testados, monitoramento, política de privacidade, canal para solicitações de titulares, regras de retenção/eliminação e revisão profissional de segurança e LGPD. O código não é certificação de conformidade jurídica.

## Como estudar o código

1. Comece em `run.py`: ele cria a aplicação.
2. Siga `app/__init__.py`: factory, banco, hooks e cabeçalhos.
3. Leia `app/auth/service.py` para entender hash, sessão e CSRF.
4. Leia `app/auth/routes.py` para acompanhar cadastro e login.
5. Leia `app/main/routes.py` para o CRUD de tarefas.
6. Veja `app/schema.sql` para relacionamentos e restrições do banco.
