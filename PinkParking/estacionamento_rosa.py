"""
=============================================================================
  SISTEMA DE GESTÃO DE ESTACIONAMENTO FEMININO — "VAGAS ROSA"
  Desenvolvido em Python 3 | Tkinter + SQLite3 | POO
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  PALETA DE CORES E ESTILOS
# ─────────────────────────────────────────────────────────────────────────────
COR_FUNDO          = "#F9F0F4"   # Rosa muito claro (fundo geral)
COR_PAINEL         = "#FFFFFF"   # Branco para painéis internos
COR_ROSA_PRIMARIO  = "#D63384"   # Rosa vibrante (botões principais)
COR_ROSA_HOVER     = "#B02B6E"   # Rosa escuro (hover)
COR_ROSA_SUAVE     = "#F4C2D7"   # Rosa suave (cabeçalhos de tabela)
COR_CINZA_ESCURO   = "#3D3340"   # Cinza-roxo escuro (textos)
COR_CINZA_MEDIO    = "#8A7F8E"   # Cinza médio (subtítulos)
COR_CINZA_BORDA    = "#E0D0DA"   # Cinza-rosado (bordas)
COR_VERDE_OK       = "#28A745"   # Verde (confirmações)
COR_VERMELHO_ERR   = "#DC3545"   # Vermelho (erros)
COR_LINHA_PAR      = "#FDF3F7"   # Linha par da tabela
COR_LINHA_IMPAR    = "#FFFFFF"   # Linha ímpar da tabela
COR_SELECAO        = "#F4C2D7"   # Linha selecionada
COR_ABA_ATIVA      = "#D63384"   # Cor da aba ativa
FONTE_TITULO       = ("Georgia", 20, "bold")
FONTE_SUBTITULO    = ("Georgia", 13, "bold")
FONTE_LABEL        = ("Helvetica", 10, "bold")
FONTE_ENTRY        = ("Helvetica", 11)
FONTE_BOTAO        = ("Helvetica", 10, "bold")
FONTE_TABELA_CAB   = ("Helvetica", 9, "bold")
FONTE_TABELA       = ("Helvetica", 10)
FONTE_TOTAL        = ("Helvetica", 12, "bold")


# ─────────────────────────────────────────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────────────────────────────────────────
class BancoDeDados:
    """Gerencia toda a persistência SQLite do sistema."""

    def __init__(self, caminho: str = "estacionamento_rosa.db"):
        self.caminho = caminho
        self._criar_tabela()

    def _conectar(self):
        return sqlite3.connect(self.caminho)

    def _criar_tabela(self):
        """Cria a tabela movimentacao caso ainda não exista."""
        sql = """
        CREATE TABLE IF NOT EXISTS movimentacao (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            placa               TEXT    NOT NULL,
            modelo              TEXT    NOT NULL,
            nome_cliente        TEXT    NOT NULL,
            contato_emergencia  TEXT    NOT NULL,
            hora_entrada        TEXT    NOT NULL,
            hora_saida          TEXT,
            valor_pago          REAL,
            status              TEXT    NOT NULL DEFAULT 'Ativo'
        );
        """
        with self._conectar() as con:
            con.execute(sql)

    # ── Leitura ──────────────────────────────────────────────────────────────

    def listar_ativos(self):
        """Retorna todos os veículos com status 'Ativo'."""
        sql = """
        SELECT id, placa, modelo, nome_cliente, contato_emergencia, hora_entrada
        FROM movimentacao
        WHERE status = 'Ativo'
        ORDER BY hora_entrada DESC;
        """
        with self._conectar() as con:
            return con.execute(sql).fetchall()

    def listar_historico(self):
        """Retorna todo o histórico de movimentações."""
        sql = """
        SELECT id, placa, modelo, nome_cliente, hora_entrada,
               hora_saida, valor_pago, status
        FROM movimentacao
        ORDER BY id DESC;
        """
        with self._conectar() as con:
            return con.execute(sql).fetchall()

    def placa_ativa(self, placa: str) -> bool:
        """Verifica se já existe uma vaga ativa com a placa informada."""
        sql = "SELECT 1 FROM movimentacao WHERE placa=? AND status='Ativo';"
        with self._conectar() as con:
            return con.execute(sql, (placa.upper(),)).fetchone() is not None

    def buscar_ativo_por_id(self, registro_id: int):
        """Busca um veículo ativo pelo ID primário."""
        sql = """
        SELECT id, placa, hora_entrada
        FROM movimentacao
        WHERE id=? AND status='Ativo';
        """
        with self._conectar() as con:
            return con.execute(sql, (registro_id,)).fetchone()

    def faturamento_total(self) -> float:
        """Calcula o faturamento total de todos os registros finalizados."""
        sql = "SELECT COALESCE(SUM(valor_pago), 0) FROM movimentacao WHERE status='Finalizado';"
        with self._conectar() as con:
            resultado = con.execute(sql).fetchone()
            return resultado[0] if resultado else 0.0

    # ── Escrita ───────────────────────────────────────────────────────────────

    def registrar_entrada(self, placa, modelo, nome, contato) -> bool:
        """Insere novo registro de entrada. Retorna False se placa já estiver ativa."""
        if self.placa_ativa(placa):
            return False
        sql = """
        INSERT INTO movimentacao (placa, modelo, nome_cliente, contato_emergencia, hora_entrada, status)
        VALUES (?, ?, ?, ?, ?, 'Ativo');
        """
        with self._conectar() as con:
            con.execute(sql, (placa.upper(), modelo, nome, contato,
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True

    def registrar_saida(self, registro_id: int, hora_saida: str, valor: float):
        """Atualiza o registro com hora de saída, valor e status Finalizado."""
        sql = """
        UPDATE movimentacao
        SET hora_saida=?, valor_pago=?, status='Finalizado'
        WHERE id=?;
        """
        with self._conectar() as con:
            con.execute(sql, (hora_saida, valor, registro_id))


# ─────────────────────────────────────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────
TARIFA_HORA = 15.00   # R$ 15,00 por hora

def calcular_valor(hora_entrada_str: str, hora_saida: datetime) -> tuple:
    """
    Calcula tempo de permanência e valor a pagar.
    Retorna (minutos_totais, valor_float, texto_duracao).
    """
    hora_entrada = datetime.strptime(hora_entrada_str, "%Y-%m-%d %H:%M:%S")
    delta = hora_saida - hora_entrada
    minutos = max(int(delta.total_seconds() / 60), 1)   # mínimo 1 minuto
    horas_proporcional = minutos / 60
    valor = round(horas_proporcional * TARIFA_HORA, 2)
    horas_int = minutos // 60
    mins_rest = minutos % 60
    texto = f"{horas_int}h {mins_rest:02d}min"
    return minutos, valor, texto


def criar_botao(parent, texto, comando, cor=COR_ROSA_PRIMARIO, fg="white", **kwargs):
    """Fábrica de botões com estilo padrão do sistema."""
    btn = tk.Button(
        parent, text=texto, command=comando,
        bg=cor, fg=fg, font=FONTE_BOTAO,
        relief="flat", cursor="hand2",
        padx=18, pady=8,
        activebackground=COR_ROSA_HOVER, activeforeground="white",
        **kwargs
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COR_ROSA_HOVER if cor == COR_ROSA_PRIMARIO else "#1a7a32"))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))
    return btn


def gerar_relatorio_pdf(caminho_arquivo, registros, faturamento_total):
    """Cria um PDF com o histórico de movimentações e faturamento acumulado."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return _gerar_relatorio_pdf_sem_reportlab(caminho_arquivo, registros, faturamento_total)

    largura, altura = landscape(A4)
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=(largura, altura),
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloPDF",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#D63384"),
        spaceAfter=4 * mm,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloPDF",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6F5273"),
        spaceAfter=2 * mm,
    )
    estilo_texto = ParagraphStyle(
        "TextoPDF",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#3D3340"),
    )
    estilo_celula = ParagraphStyle(
        "CelulaPDF",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#3D3340"),
    )

    story = [
        Paragraph("Relatório de Movimentação - Vagas Rosa", estilo_titulo),
        Paragraph("<font color='#8A7F8E'>Vagas Rosa — histórico de entradas, saídas e faturamento</font>", estilo_subtitulo),
        Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilo_texto),
        Paragraph(f"Faturamento total acumulado: R$ {faturamento_total:.2f}", estilo_texto),
        Spacer(1, 8 * mm),
    ]

    headers = ["Nº", "Placa", "Modelo", "Cliente", "Entrada", "Saída", "Valor", "Status"]
    data = [headers]

    def formatar_data(valor):
        if not valor:
            return "—"
        try:
            return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        except Exception:
            return valor

    for reg in registros:
        data.append([
            Paragraph(str(reg[0]), estilo_celula),
            Paragraph(reg[1], estilo_celula),
            Paragraph(reg[2], estilo_celula),
            Paragraph(reg[3], estilo_celula),
            Paragraph(formatar_data(reg[4]), estilo_celula),
            Paragraph(formatar_data(reg[5]), estilo_celula),
            Paragraph(f"R$ {reg[6]:.2f}" if reg[6] is not None else "—", estilo_celula),
            Paragraph(reg[7], estilo_celula),
        ])

    if len(data) == 1:
        story.append(Paragraph("Nenhum registro encontrado.", estilo_texto))
    else:
        col_widths = [24 * mm, 30 * mm, 40 * mm, 60 * mm, 32 * mm, 32 * mm, 24 * mm, 24 * mm]
        tabela = Table(data, colWidths=col_widths, repeatRows=1)
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4C2D7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#3D3340")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (1, 0), (3, -1), "LEFT"),
            ("ALIGN", (4, 0), (-1, -1), "CENTER"),
            ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E0D0DA")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFF0F5"), colors.white]),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D63384")),
        ]))
        story.append(tabela)

    doc.build(story)


def _escapar_pdf_texto(texto):
    texto = texto if texto is not None else ""
    return texto.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)').replace('\n', '\\n')


def _gerar_relatorio_pdf_sem_reportlab(caminho_arquivo, registros, faturamento_total):
    def formatar_data(valor):
        if not valor:
            return "—"
        try:
            return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        except Exception:
            return valor

    linhas = [
        "Relatório de Movimentação - Vagas Rosa",
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"Faturamento total acumulado: R$ {faturamento_total:.2f}",
        "",
        "Nº  Placa        Modelo           Cliente                Entrada           Saida             Valor     Status",
        "-------------------------------------------------------------------------------------------",
    ]

    for reg in registros:
        valor = f"R$ {reg[6]:.2f}" if reg[6] is not None else "—"
        linhas.append(
            f"{str(reg[0]):<3} {str(reg[1]):<12} {str(reg[2]):<15} {str(reg[3]):<22} "
            f"{formatar_data(reg[4]):<17} {formatar_data(reg[5]):<17} {valor:<10} {str(reg[7]):<10}"
        )

    with open(caminho_arquivo, "wb") as f:
        f.write(b"%PDF-1.4\n")
        objects = []

        content = "BT\n/F1 10 Tf\n40 820 Td\n"
        for i, line in enumerate(linhas):
            if i > 0:
                content += "0 -14 Td\n"
            content += f"({_escapar_pdf_texto(line)}) Tj\n"
        content += "ET\n"
        content_bytes = content.encode('latin-1', 'replace')

        objects.append((1, b"<< /Type /Catalog /Pages 2 0 R >>"))
        objects.append((2, b"<< /Type /Pages /Count 1 /Kids [4 0 R] >>"))
        objects.append((3, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))
        objects.append((4, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 3 0 R >> >> /Contents 5 0 R >>"))
        objects.append((5, b"<< /Length %d >>\nstream\n%b\nendstream" % (len(content_bytes), content_bytes)))

        offsets = []
        for obj_id, obj_bytes in objects:
            offsets.append(f.tell())
            f.write(f"{obj_id} 0 obj\n".encode())
            f.write(obj_bytes)
            f.write(b"\nendobj\n")

        xref_offset = f.tell()
        f.write(b"xref\n")
        f.write(f"0 {len(objects)+1}\n".encode())
        f.write(b"0000000000 65535 f \n")
        for offset in offsets:
            f.write(f"{offset:010d} 00000 n \n".encode())
        f.write(b"trailer\n")
        f.write(b"<< /Size %d /Root 1 0 R >>\n" % (len(objects)+1))
        f.write(b"startxref\n")
        f.write(f"{xref_offset}\n".encode())
        f.write(b"%%EOF\n")


def campo_label(parent, texto, row, col=0, sticky="w", padx=(0, 8), pady=(10, 2)):
    """Label padrão de formulário."""
    lbl = tk.Label(parent, text=texto, font=FONTE_LABEL,
                   fg=COR_CINZA_ESCURO, bg=COR_PAINEL)
    lbl.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
    return lbl


def campo_entry(parent, row, col=1, largura=32, padx=(0, 0), pady=(10, 2)):
    """Entry padrão de formulário."""
    entry = ttk.Entry(parent, width=largura, font=FONTE_ENTRY)
    entry.grid(row=row, column=col, sticky="ew", padx=padx, pady=pady)
    return entry


# ─────────────────────────────────────────────────────────────────────────────
#  ABA — ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
class AbaEntrada(tk.Frame):
    """Formulário para registrar a entrada de um veículo."""

    def __init__(self, parent, db: BancoDeDados, callback_refresh):
        super().__init__(parent, bg=COR_FUNDO)
        self.db = db
        self.callback_refresh = callback_refresh
        self._construir()

    def _construir(self):
        # ── Cabeçalho ────────────────────────────────────────────────────────
        cab = tk.Frame(self, bg=COR_ROSA_PRIMARIO)
        cab.pack(fill="x")
        tk.Label(cab, text="🌸  Registro de Entrada",
                 font=FONTE_TITULO, bg=COR_ROSA_PRIMARIO, fg="white",
                 pady=18).pack()
        tk.Label(cab, text="Vagas Rosa — Segurança e Conforto Feminino",
                 font=("Helvetica", 10, "italic"), bg=COR_ROSA_PRIMARIO,
                 fg="#FFCCE8", pady=4).pack()

        # ── Painel do formulário ──────────────────────────────────────────────
        painel = tk.Frame(self, bg=COR_PAINEL, bd=0,
                          highlightbackground=COR_CINZA_BORDA, highlightthickness=1)
        painel.pack(padx=60, pady=30, fill="both", expand=True)
        painel.columnconfigure(1, weight=1)

        tk.Label(painel, text="Dados do Veículo e da Cliente",
                 font=FONTE_SUBTITULO, fg=COR_ROSA_PRIMARIO,
                 bg=COR_PAINEL).grid(row=0, column=0, columnspan=2,
                                     pady=(20, 4), padx=20, sticky="w")

        # Separador decorativo
        sep = tk.Frame(painel, bg=COR_ROSA_SUAVE, height=2)
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))

        # Campos
        campo_label(painel, "Placa do Veículo *", 2, padx=(20, 8))
        self.entry_placa = campo_entry(painel, 2, padx=(0, 20))

        campo_label(painel, "Modelo do Veículo *", 3, padx=(20, 8))
        self.entry_modelo = campo_entry(painel, 3, padx=(0, 20))

        campo_label(painel, "Nome da Cliente *", 4, padx=(20, 8))
        self.entry_nome = campo_entry(painel, 4, padx=(0, 20))

        campo_label(painel, "Telefone de Emergência *", 5, padx=(20, 8))
        self.entry_contato = campo_entry(painel, 5, padx=(0, 20))

        # Nota de campos obrigatórios
        tk.Label(painel, text="* Campos obrigatórios",
                 font=("Helvetica", 8, "italic"), fg=COR_CINZA_MEDIO,
                 bg=COR_PAINEL).grid(row=6, column=0, columnspan=2,
                                     sticky="w", padx=20, pady=(6, 0))

        # Botões
        frame_btns = tk.Frame(painel, bg=COR_PAINEL)
        frame_btns.grid(row=7, column=0, columnspan=2, pady=24, padx=20, sticky="e")

        criar_botao(frame_btns, "🗑  Limpar", self._limpar,
                    cor="#6C757D").pack(side="left", padx=(0, 10))
        criar_botao(frame_btns, "✔  Confirmar Entrada", self._confirmar).pack(side="left")

    def _limpar(self):
        for entry in (self.entry_placa, self.entry_modelo,
                      self.entry_nome, self.entry_contato):
            entry.delete(0, "end")
        self.entry_placa.focus()

    def _confirmar(self):
        placa   = self.entry_placa.get().strip()
        modelo  = self.entry_modelo.get().strip()
        nome    = self.entry_nome.get().strip()
        contato = self.entry_contato.get().strip()

        # Validação de campos obrigatórios
        if not all([placa, modelo, nome, contato]):
            messagebox.showwarning("Campos Incompletos",
                                   "Por favor, preencha todos os campos obrigatórios.")
            return

        # Validação de placa duplicada
        sucesso = self.db.registrar_entrada(placa, modelo, nome, contato)
        if not sucesso:
            messagebox.showerror("Placa Já Estacionada",
                                 f"A placa {placa.upper()} já possui uma vaga ativa.\n"
                                 "Registre a saída antes de uma nova entrada.")
            return

        messagebox.showinfo("Entrada Confirmada ✅",
                            f"Veículo {placa.upper()} registrado com sucesso!\n"
                            f"Hora de entrada: {datetime.now().strftime('%H:%M:%S')}")
        self._limpar()
        self.callback_refresh()   # Atualiza as outras abas


# ─────────────────────────────────────────────────────────────────────────────
#  ABA — GESTÃO DO PÁTIO
# ─────────────────────────────────────────────────────────────────────────────
class AbaPateo(tk.Frame):
    """Painel em tempo real com veículos estacionados e controle de saída."""

    COLUNAS = ("id", "placa", "modelo", "nome_cliente", "contato", "entrada")
    CABECALHOS = ("Nº", "Placa", "Modelo", "Cliente", "Emergência", "Entrada")
    LARGURAS   = (40, 100, 140, 170, 130, 150)

    def __init__(self, parent, db: BancoDeDados, callback_refresh):
        super().__init__(parent, bg=COR_FUNDO)
        self.db = db
        self.callback_refresh = callback_refresh
        self._construir()

    def _construir(self):
        # ── Cabeçalho ────────────────────────────────────────────────────────
        cab = tk.Frame(self, bg=COR_ROSA_PRIMARIO)
        cab.pack(fill="x")
        tk.Label(cab, text="🅿  Gestão do Pátio — Vagas Ativas",
                 font=FONTE_TITULO, bg=COR_ROSA_PRIMARIO, fg="white",
                 pady=18).pack()

        # ── Contador de vagas ─────────────────────────────────────────────────
        self.lbl_contador = tk.Label(
            self, text="", font=("Helvetica", 11, "bold"),
            fg=COR_ROSA_PRIMARIO, bg=COR_FUNDO
        )
        self.lbl_contador.pack(pady=(12, 0))

        # ── Tabela ────────────────────────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg=COR_FUNDO)
        frame_tabela.pack(fill="both", expand=True, padx=30, pady=10)

        self.tree = ttk.Treeview(
            frame_tabela, columns=self.COLUNAS,
            show="headings", selectmode="browse"
        )

        for col, cab_txt, larg in zip(self.COLUNAS, self.CABECALHOS, self.LARGURAS):
            self.tree.heading(col, text=cab_txt)
            self.tree.column(col, width=larg, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(frame_tabela, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame_tabela.rowconfigure(0, weight=1)
        frame_tabela.columnconfigure(0, weight=1)

        # Tags de linha alternada
        self.tree.tag_configure("par",    background=COR_LINHA_PAR)
        self.tree.tag_configure("impar",  background=COR_LINHA_IMPAR)
        self.tree.tag_configure("select", background=COR_SELECAO)

        # ── Barra de ações ────────────────────────────────────────────────────
        barra = tk.Frame(self, bg=COR_FUNDO)
        barra.pack(pady=12)

        criar_botao(barra, "🔄  Atualizar", self.atualizar).pack(side="left", padx=8)
        criar_botao(barra, "🚗  Registrar Saída", self._registrar_saida,
                    cor=COR_VERDE_OK).pack(side="left", padx=8)

        self.atualizar()

    def atualizar(self):
        """Recarrega a tabela com os dados mais recentes do banco."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        registros = self.db.listar_ativos()
        for i, reg in enumerate(registros):
            # Formatar hora de entrada para exibição
            try:
                hora_fmt = datetime.strptime(reg[5], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            except Exception:
                hora_fmt = reg[5]

            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end",
                             values=(reg[0], reg[1], reg[2], reg[3], reg[4], hora_fmt),
                             tags=(tag,))

        total = len(registros)
        self.lbl_contador.config(
            text=f"🌸  {total} vaga{'s' if total != 1 else ''} ocupada{'s' if total != 1 else ''} no momento"
        )

    def _registrar_saida(self):
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Nenhum Veículo Selecionado",
                                   "Selecione um veículo na tabela para registrar a saída.")
            return

        valores = self.tree.item(selecionado, "values")
        registro_id = int(valores[0])
        placa        = valores[1]

        # Buscar hora de entrada no banco para cálculo preciso
        reg = self.db.buscar_ativo_por_id(registro_id)
        if not reg:
            messagebox.showerror("Erro", "Registro não encontrado ou já finalizado.")
            self.atualizar()
            return

        hora_saida = datetime.now()
        _, valor, duracao = calcular_valor(reg[2], hora_saida)

        # Pop-up de confirmação com resumo financeiro
        confirmar = messagebox.askyesno(
            "Confirmar Saída 🌸",
            f"  Placa:          {placa}\n"
            f"  Tempo total:    {duracao}\n"
            f"  Valor a pagar:  R$ {valor:.2f}\n\n"
            "Confirmar o registro de saída?"
        )
        if confirmar:
            self.db.registrar_saida(
                registro_id,
                hora_saida.strftime("%Y-%m-%d %H:%M:%S"),
                valor
            )
            messagebox.showinfo("Saída Registrada ✅",
                                f"Saída de {placa} registrada.\n"
                                f"Valor cobrado: R$ {valor:.2f}\n\n"
                                "Obrigada pela visita! 🌸")
            self.atualizar()
            self.callback_refresh()


# ─────────────────────────────────────────────────────────────────────────────
#  ABA — RELATÓRIOS
# ─────────────────────────────────────────────────────────────────────────────
class AbaRelatorios(tk.Frame):
    """Histórico completo e faturamento acumulado."""

    COLUNAS   = ("id", "placa", "modelo", "cliente", "entrada", "saida", "valor", "status")
    CABECALHOS = ("Nº", "Placa", "Modelo", "Cliente", "Entrada", "Saída", "Valor R$", "Status")
    LARGURAS   = (40, 90, 130, 160, 145, 145, 80, 80)

    def __init__(self, parent, db: BancoDeDados):
        super().__init__(parent, bg=COR_FUNDO)
        self.db = db
        self._construir()

    def _construir(self):
        # ── Cabeçalho ────────────────────────────────────────────────────────
        cab = tk.Frame(self, bg=COR_ROSA_PRIMARIO)
        cab.pack(fill="x")
        tk.Label(cab, text="📋  Relatórios e Faturamento",
                 font=FONTE_TITULO, bg=COR_ROSA_PRIMARIO, fg="white",
                 pady=18).pack()

        # ── Faturamento total ─────────────────────────────────────────────────
        self.lbl_fat = tk.Label(
            self, text="", font=FONTE_TOTAL,
            fg=COR_ROSA_PRIMARIO, bg=COR_FUNDO
        )
        self.lbl_fat.pack(pady=(12, 0))

        # ── Tabela ────────────────────────────────────────────────────────────
        frame_tabela = tk.Frame(self, bg=COR_FUNDO)
        frame_tabela.pack(fill="both", expand=True, padx=30, pady=10)

        self.tree = ttk.Treeview(
            frame_tabela, columns=self.COLUNAS,
            show="headings", selectmode="browse"
        )

        for col, cab_txt, larg in zip(self.COLUNAS, self.CABECALHOS, self.LARGURAS):
            self.tree.heading(col, text=cab_txt)
            self.tree.column(col, width=larg, anchor="center")

        vsb = ttk.Scrollbar(frame_tabela, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame_tabela.rowconfigure(0, weight=1)
        frame_tabela.columnconfigure(0, weight=1)

        # Tags visuais por status
        self.tree.tag_configure("ativo",      background="#FFF0F5", foreground="#D63384")
        self.tree.tag_configure("finalizado", background="#F0FFF4", foreground="#1a7a32")
        self.tree.tag_configure("par_fin",    background="#E8F5E9", foreground="#1a7a32")

        # ── Botões de ação ──────────────────────────────────────────────────
        frame_botoes = tk.Frame(self, bg=COR_FUNDO)
        frame_botoes.pack(pady=10)

        criar_botao(frame_botoes, "📄  Exportar PDF", self._exportar_pdf,
                    cor="#6C757D").pack(side="left", padx=8)
        criar_botao(frame_botoes, "🔄  Atualizar Relatório", self.atualizar).pack(side="left", padx=8)

        self.atualizar()

    def _exportar_pdf(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar relatório em PDF"
        )
        if not caminho:
            return

        try:
            gerar_relatorio_pdf(
                caminho,
                self.db.listar_historico(),
                self.db.faturamento_total()
            )
            messagebox.showinfo("PDF Gerado ✅",
                                f"Relatório exportado com sucesso!\n\n{caminho}")
        except ImportError:
            messagebox.showerror(
                "Dependência Ausente",
                "O pacote reportlab não está instalado.\n"
                "Instale com: pip install reportlab"
            )
        except Exception as exc:
            messagebox.showerror("Erro ao Exportar PDF",
                                 f"Não foi possível gerar o PDF.\n\n{exc}")

    def atualizar(self):
        """Recarrega o histórico completo."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        registros = self.db.listar_historico()
        for reg in registros:
            # Formatar datas
            def fmt(dt_str):
                if not dt_str:
                    return "—"
                try:
                    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                except Exception:
                    return dt_str

            status = reg[7]
            valor  = f"R$ {reg[6]:.2f}" if reg[6] is not None else "—"
            tag    = "ativo" if status == "Ativo" else "finalizado"

            self.tree.insert("", "end",
                             values=(reg[0], reg[1], reg[2], reg[3],
                                     fmt(reg[4]), fmt(reg[5]), valor, status),
                             tags=(tag,))

        # Atualiza faturamento total
        fat = self.db.faturamento_total()
        self.lbl_fat.config(text=f"💰  Faturamento Total Acumulado:  R$ {fat:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
#  APLICAÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    """Janela raiz e orquestrador das abas do sistema."""

    def __init__(self):
        super().__init__()
        self.title("🌸 Vagas Rosa — Sistema de Gestão de Estacionamento Feminino")
        self.geometry("860x640")
        self.minsize(760, 540)
        self.configure(bg=COR_FUNDO)
        self.resizable(True, True)

        # Ícone de janela (texto unicode como fallback)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # Banco de dados
        self.db = BancoDeDados()

        # Estilos ttk
        self._aplicar_estilos()

        # Notebook principal
        self._criar_notebook()

    def _aplicar_estilos(self):
        """Configura o tema visual do ttk."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # ── Notebook (abas) ───────────────────────────────────────────────────
        style.configure("TNotebook",
                        background=COR_FUNDO,
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=COR_CINZA_BORDA,
                        foreground=COR_CINZA_ESCURO,
                        font=("Helvetica", 10, "bold"),
                        padding=(18, 8))
        style.map("TNotebook.Tab",
                  background=[("selected", COR_ROSA_PRIMARIO),
                               ("active",   COR_ROSA_SUAVE)],
                  foreground=[("selected", "white"),
                               ("active",   COR_CINZA_ESCURO)])

        # ── Treeview ──────────────────────────────────────────────────────────
        style.configure("Treeview",
                        background=COR_PAINEL,
                        foreground=COR_CINZA_ESCURO,
                        fieldbackground=COR_PAINEL,
                        font=FONTE_TABELA,
                        rowheight=28,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=COR_ROSA_SUAVE,
                        foreground=COR_CINZA_ESCURO,
                        font=FONTE_TABELA_CAB,
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", COR_SELECAO)],
                  foreground=[("selected", COR_CINZA_ESCURO)])

        # ── Entry ─────────────────────────────────────────────────────────────
        style.configure("TEntry",
                        fieldbackground=COR_PAINEL,
                        foreground=COR_CINZA_ESCURO,
                        bordercolor=COR_CINZA_BORDA,
                        lightcolor=COR_CINZA_BORDA,
                        darkcolor=COR_CINZA_BORDA,
                        insertcolor=COR_CINZA_ESCURO)

        # ── Scrollbar ─────────────────────────────────────────────────────────
        style.configure("Vertical.TScrollbar",
                        background=COR_ROSA_SUAVE,
                        troughcolor=COR_FUNDO)
        style.configure("Horizontal.TScrollbar",
                        background=COR_ROSA_SUAVE,
                        troughcolor=COR_FUNDO)

    def _criar_notebook(self):
        """Cria as abas do sistema."""
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        # Instâncias das abas
        self.aba_entrada   = AbaEntrada(nb,   self.db, self._refresh_todas)
        self.aba_patio     = AbaPateo(nb,     self.db, self._refresh_todas)
        self.aba_relatorio = AbaRelatorios(nb, self.db)

        nb.add(self.aba_entrada,   text="  🚗  Entrada  ")
        nb.add(self.aba_patio,     text="  🅿  Gestão do Pátio  ")
        nb.add(self.aba_relatorio, text="  📋  Relatórios  ")

        # Atualiza ao trocar de aba
        nb.bind("<<NotebookTabChanged>>", self._ao_trocar_aba)
        self._nb = nb

    def _ao_trocar_aba(self, event):
        """Atualiza dados ao mudar de aba para manter informações em tempo real."""
        idx = self._nb.index(self._nb.select())
        if idx == 1:
            self.aba_patio.atualizar()
        elif idx == 2:
            self.aba_relatorio.atualizar()

    def _refresh_todas(self):
        """Atualiza todas as abas dinâmicas."""
        self.aba_patio.atualizar()
        self.aba_relatorio.atualizar()


# ─────────────────────────────────────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
