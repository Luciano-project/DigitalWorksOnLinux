# DigitalWorks em Docker (Wine + noVNC)

Container Docker para executar o **DigitalWorks** (simulador de circuitos digitais para Windows) em Linux, através do Wine, com acesso pelo navegador via noVNC. Não é preciso instalar Wine nem um servidor gráfico na máquina anfitriã.

> Este repositório **não inclui** o DigitalWorks. O programa é descarregado do site oficial (mecanique.co.uk) durante o `docker build`, através de [download_digitalworks_3.0.5.sh](download_digitalworks_3.0.5.sh).

## Como funciona

Durante o `docker build`, o DigitalWorks 3.0.5 é descarregado e instalado em `/app`, dentro da imagem.

Ao arrancar, o container ([start.sh](start.sh)):

1. Cria um ecrã virtual com **Xvfb**.
2. Inicia o **Openbox**, para poder mover e redimensionar janelas.
3. Inicia o **x11vnc**, acessível apenas dentro do container.
4. Disponibiliza o **noVNC** (cliente VNC web) na porta `6080`.
5. Inicia um servidor de downloads dos projetos na porta `6081`.
6. Ajusta a escala (DPI) do Wine, liga a unidade `P:` à pasta de projetos e executa `DigitalWorks.exe`.

## Requisitos

- Docker
- Acesso à internet durante o `docker build`

## Utilização

Construir a imagem:

```sh
docker build -t wine-digitalworks-web .
```

Executar o container:

```sh
docker run -d --rm --name digitalworks \
  -p 127.0.0.1:6080:6080 \
  -p 127.0.0.1:6081:6081 \
  -v "$(pwd)/projetos":/projetos \
  -v wine-prefix:/root/.wine \
  wine-digitalworks-web
```

Abra no navegador:

```
http://localhost:6080/vnc.html
```

Parar o container:

```sh
docker stop digitalworks
```

O volume `wine-prefix` guarda a configuração do Wine entre execuções, o que torna os arranques seguintes mais rápidos.

## Guardar e descarregar projetos

No DigitalWorks, guarde os circuitos na unidade **`P:`**. Essa unidade corresponde à pasta `/projetos` do container, que está ligada à pasta `projetos/` da máquina anfitriã.

Para descarregar os ficheiros pelo navegador, abra:

```
http://localhost:6081/
```

A página lista os ficheiros e as pastas de `P:`. Pode descarregar cada ficheiro ou uma pasta inteira em ZIP, incluindo todos os projetos de uma vez em **Descarregar esta pasta em ZIP**. Se `VNC_PASSWORD` estiver definida, a página pede essa senha (o nome de utilizador pode ser qualquer um).

## Configuração

Variáveis de ambiente que pode passar com `-e` no `docker run`:

| Variável       | Padrão         | Descrição                                                        |
|----------------|----------------|------------------------------------------------------------------|
| `RESOLUTION`   | `1280x800x24`  | Resolução e profundidade de cor do ecrã virtual.                 |
| `WINE_DPI`     | `96`           | Escala da interface: `96` = 100%, `144` = 150%, `192` = 200%.    |
| `VNC_PASSWORD` | *(sem senha)*  | Se definida, o noVNC e a página de downloads pedem esta senha.   |

Exemplo:

```sh
docker run -d --rm --name digitalworks \
  -p 127.0.0.1:6080:6080 \
  -p 127.0.0.1:6081:6081 \
  -v "$(pwd)/projetos":/projetos \
  -v wine-prefix:/root/.wine \
  -e RESOLUTION=1920x1080x24 \
  -e WINE_DPI=144 \
  -e VNC_PASSWORD=minhasenha \
  wine-digitalworks-web
```

## Segurança

Por padrão, as portas só ficam acessíveis em `127.0.0.1`. Para aceder a partir de outra máquina, retire o `127.0.0.1:` das opções `-p` e defina `VNC_PASSWORD`. A senha é enviada sem encriptação (HTTP), por isso, numa rede pouco fiável, use um proxy reverso com HTTPS ou um túnel SSH.

## Resolução de problemas

- **Página em branco ou erro de ligação**: o primeiro arranque demora mais porque o Wine cria o prefixo. Aguarde alguns segundos e recarregue. Veja os logs com `docker logs digitalworks`.
- **Interface muito pequena ou grande**: ajuste `WINE_DPI`.
- **A unidade `P:` não aparece**: reinicie o container. A ligação é criada a cada arranque.
- **Atualizar ou voltar a descarregar o DigitalWorks**: `docker build --no-cache -t wine-digitalworks-web .`
- **Repor a configuração do Wine**: `docker volume rm wine-prefix`.

## Licença

Este repositório é um projeto académico, criado como ferramenta de apoio a materiais de estudo. O código (Dockerfile, scripts e documentação) está sob a licença [MIT](LICENSE).

A licença **não se aplica ao DigitalWorks**. O programa pertence ao seu autor (Mecanique), não é distribuído neste repositório e é descarregado diretamente do site oficial durante o `docker build`. O uso do DigitalWorks segue os termos definidos pelo autor.
