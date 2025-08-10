
# Transcritor de Mídia com IA

Um script de linha de comando eficiente para transcrever arquivos de áudio e vídeo em legendas `.srt` usando a tecnologia **Whisper**.

## 📖 Sobre o Projeto

Este projeto foi criado para automatizar a tarefa de transcrever aulas, palestras, reuniões e outros conteúdos de mídia. Utilizando o poder dos modelos de IA da família Whisper, este script oferece uma solução robusta e flexível que pode ser executada localmente, com suporte para aceleração via GPU para um desempenho ainda maior.

O objetivo é fornecer uma ferramenta simples, mas poderosa, para que usuários possam obter transcrições de alta qualidade sem depender de serviços online.

## ✨ Funcionalidades Principais

- **Menu Interativo**: Selecione facilmente qual arquivo transcrever a partir de uma lista de mídias válidas no diretório.
- **Suporte a Vários Formatos**: Transcreva os formatos de áudio e vídeo mais comuns (mp3, mp4, wav, m4a, webm, etc.).
- **Saída em .srt**: Gera arquivos de legenda no formato SubRip (.srt), prontos para uso em players de vídeo ou para leitura.
- **Aceleração por GPU**: Suporte total para processamento em GPUs NVIDIA (CUDA) para uma transcrição significativamente mais rápida.
- **Seleção de Modelo**: Escolha entre diferentes tamanhos de modelo (`tiny`, `base`, `small`, `medium`, `large-v3`) para balancear velocidade e precisão.
- **Feedback em Tempo Real**: Acompanhe o progresso da transcrição diretamente no seu terminal.

## 📂 Documentação Completa

Toda a documentação formal do projeto, incluindo a **Especificação de Requisitos do Usuário (URS)**, a **Especificação de Requisitos do Software (SRS)**, o **Desenho da Arquitetura (SDS)** com fluxogramas está disponível na pasta `/docs` deste repositório.

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes softwares instalados:

- **Python 3.12**
- **astral-uv**


Para aceleração GPU, instale:
- Nvidia Cuda ToolKit
- Nvidia cuNND
- Nvidia CuBlas

## 🚀 Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/thawancomt/whisper-transcript.git
   cd whisper-transcript
   ```

2. Instale as dependencias:

   ```bash
   uv sync
   ```


## (Como Usar)

1. Coloque os arquivos de áudio ou vídeo que você deseja transcrever na pasta do projeto.
2. Execute o script no seu terminal.



### Uso Básico (com CPU):

(Modelos disponíveis: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`)

```bash
python app.py [--cpu-threads] [--model=modelo_desejado]
```

O script irá listar os arquivos disponíveis e você poderá escolher um número para iniciar a transcrição.

### Uso com GPU (Requer NVIDIA CUDA) e drivers instalados no sistema:

```bash
python app.py --cuda [--cpu-threads] [--model=modelo_desejado]
```



## 📜 Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.


# Instalação para rodar no linux
