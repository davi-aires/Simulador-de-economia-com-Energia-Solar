from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, PhotoImage, ttk, messagebox, END
import os
import shutil
import ctypes
import winreg


def installFont(font_filename):
    try:
        caminho_fonte = os.path.abspath(f"{os.getcwd()}/assets/fonts/{font_filename}")
        fonte_extensao = os.path.splitext(font_filename)[1].lower()  # .ttf ou .otf
        destino = os.path.join(os.environ['WINDIR'], 'Fonts', font_filename)

        if not os.path.exists(destino):
            shutil.copy(caminho_fonte, destino)
            print(f"Fonte {font_filename} copiada para a pasta de fontes do sistema.")

            # Instalar no registro
            font_name = os.path.splitext(font_filename)[0]  # ex: 'Consolas'
            font_registry_name = f"{font_name} ({'OpenType' if fonte_extensao == '.otf' else 'TrueType'})"

            font_reg_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, font_reg_key, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, font_registry_name, 0, winreg.REG_SZ, font_filename)

            # Atualiza cache de fontes
            ctypes.windll.gdi32.AddFontResourceW(destino)
            ctypes.windll.user32.SendMessageW(0xffff, 0x001D, 0, 0)

            print(f"Fonte {font_registry_name} instalada com sucesso.")
        else:
            print(f"Fonte {font_filename} já está instalada.")
    except:
        pass

class Gui:
    def __init__(self):
        self.window = Tk()
        self.images = []

    def iniciarTela(self):
        diretorioAtual = os.getcwd()
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(rf"{diretorioAtual}\assets\frame0")
        ICON_PATH = rf"{diretorioAtual}\assets\logo.ico"

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        def configScreen(altura, largura):
            posX = self.window.winfo_screenwidth() / 2 - largura / 2
            posY = self.window.winfo_screenheight() / 2 - altura / 2
            self.window.geometry("%dx%d+%d+%d" % (largura, altura, posX, posY))
            self.window.title("Meu Sistema Solar")
            self.window.iconbitmap(ICON_PATH)

        def hover(event):
            event.widget.configure(cursor="hand2")

        def unHover(event):
            event.widget.configure(cursor="")

        def configBtn(btn):
            btn.bind("<Enter>", hover)
            btn.bind("<Leave>", unHover)

        def realizar_simulacao():
            consumo = entry_1.get()  # consumo atual (opcional)
            custo = entry_2.get()  # custo do sistema (R$)
            potencia = entry_3.get()  # potência do sistema (kWp)

            if not custo or not consumo or not potencia:
                messagebox.showerror(title="Dados incorretos", message="Preencha todos os 3 campos.")
                return

            try:
                consumo = float(consumo.replace(".", "").replace(",", "."))
                custo = float(custo.replace(".", "").replace(",", ".").replace("R$", "").strip())
                potencia = float(potencia.replace(".", "").replace(",", ".")) / 1000

                # parâmetros fixos
                tarifa = 0.95  # R$/kWh
                fator_producao = 130  # kWh por kWp por mês

                # geração mensal
                geracao_mensal = potencia * fator_producao

                # economia mensal (não pode ultrapassar o consumo)
                economia_mensal = min(geracao_mensal, consumo) * tarifa

                # payback
                payback_meses = custo / economia_mensal
                payback_anos = payback_meses / 12

                # monta mensagem base
                mensagem = (
                    f"Geração estimada: {geracao_mensal:.0f} kWh/mês\n"
                    f"Economia mensal: R$ {economia_mensal:.2f}\n"
                    f"Payback estimado: {payback_meses:.1f} meses ({payback_anos:.1f} anos)"
                )

                # adiciona aviso se gerar mais do que consome
                if geracao_mensal > consumo:
                    mensagem += f"\n\nATENÇÃO: O sistema está gerando {geracao_mensal-consumo}kWh a mais do que o consumo necessário.\nO excedente não gera economia adicional."

                # mostra tudo junto
                messagebox.showinfo(title="Resultado", message=mensagem)

                canvas.itemconfig(mesesNecessarios, text=f"{payback_meses:.1f}")
                if (payback_meses < 100) and payback_meses < 10:
                    canvas.coords(mesesNecessarios, 230, 267)
                elif payback_meses >= 100:
                    canvas.coords(mesesNecessarios, 225, 267)
                else:
                    canvas.coords(mesesNecessarios, 228, 267)

            except ValueError:
                messagebox.showerror(title="Erro", message="Digite apenas números válidos.")

        def validar_numero(valor):
            return valor.isdigit() or valor == ""  # permite apenas números ou vazio

        def formatar_moeda(event=None):
            # pega apenas números do texto
            texto = ''.join([c for c in entry_2.get() if c.isdigit()])

            if texto == "":
                entry_2.delete(0, END)
                entry_2.insert(0, "R$ 0,00")
                return

            valor = int(texto)
            texto_formatado = f"R$ {valor / 100:,.2f}"
            texto_formatado = texto_formatado.replace(",", "v").replace(".", ",").replace("v", ".")

            entry_2.delete(0, END)
            entry_2.insert(0, texto_formatado)
            entry_2.icursor(END)  # mantém o cursor no final

        style = ttk.Style()
        style.configure(
            "Custom.TButton",
            borderwidth=0,
            relief="flat",
            padding=(-4, -4, 0, 0),
            background="#FFD54F"
        )

        font = ("FiraCode-Regular", 8)

        installFont('FiraCode-Regular.ttf')
        configScreen(489, 324)

        canvas = Canvas(
            self.window,
            bg="#41C0B1",
            height=489,
            width=324,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)

        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            162.0,
            244.0,
            image=image_image_1
        )

        image_image_2 = PhotoImage(
            file=relative_to_assets("image_2.png"))
        image_2 = canvas.create_image(
            160.0,
            122.0,
            image=image_image_2
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = ttk.Button(
            image=button_image_1,
            command=lambda: realizar_simulacao(),
            style="Custom.TButton"
        )
        button_1.place(
            x=45.0,
            y=397.0,
            width=231.0,
            height=54.0
        )
        configBtn(button_1)

        interrogacao = PhotoImage(
            file=relative_to_assets("image_13.png"))
        button_2 = ttk.Button(
            image=interrogacao,
            command=lambda : messagebox.showinfo(
            title="Ajuda de preenchimento para simulação",
            message="""Em "Seu consumo mensal" preencha seu consumo mensal de kWh de energia\n
Em "Custo" preencha em R$ qual será o preço do seu sistema completo\n
Em "Potência" preencha em Wp a potência total do seu sistema\n\n
A preço do kWh/R$ está fixado em 0.95 então os valores podem variar um pouco, isto é apenas uma simulação!"""),
            style="Custom.TButton"
        )
        button_2.place(
            x=168.0,
            y=242.0,
            width=20.0,
            height=20.0
        )
        configBtn(button_2)


        image_image_3 = PhotoImage(
            file=relative_to_assets("image_3.png"))
        image_3 = canvas.create_image(
            119.0,
            309.0,
            image=image_image_3
        )

        image_image_4 = PhotoImage(
            file=relative_to_assets("image_4.png"))
        image_4 = canvas.create_image(
            239.0,
            309.0,
            image=image_image_4
        )

        mesesNecessarios = canvas.create_text(
            235.0,
            267.0,
            anchor="nw",
            text="X",
            fill="#32A42D",
            font=("Inter", 11, "bold")
        )

        image_image_5 = PhotoImage(
            file=relative_to_assets("image_5.png"))
        image_5 = canvas.create_image(
            161.0,
            219.0,
            image=image_image_5
        )

        image_image_6 = PhotoImage(
            file=relative_to_assets("image_6.png"))
        image_6 = canvas.create_image(
            164.0,
            45.0,
            image=image_image_6
        )

        image_image_7 = PhotoImage(
            file=relative_to_assets("image_7.png"))
        image_7 = canvas.create_image(
            160.0,
            78.0,
            image=image_image_7
        )

        vcmd = (self.window.register(validar_numero), "%P")

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            160.0,
            73.5,
            image=entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#FDFDFD",
            fg="#263238",
            highlightthickness=0,
            font=font,
            validate='key',
            validatecommand=vcmd
        )
        entry_1.place(
            x=51.0,
            y=65.0,
            width=214.0,
            height=15.0
        )

        image_image_8 = PhotoImage(
            file=relative_to_assets("image_8.png"))
        image_8 = canvas.create_image(
            100.0,
            148.0,
            image=image_image_8
        )

        image_image_9 = PhotoImage(
            file=relative_to_assets("image_9.png"))
        image_9 = canvas.create_image(
            100.0,
            174.0,
            image=image_image_9
        )

        image_image_10 = PhotoImage(
            file=relative_to_assets("image_10.png"))
        image_10 = canvas.create_image(
            60.0,
            184.0,
            image=image_image_10
        )

        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            100.0,
            169.5,
            image=entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#FDFDFD",
            fg="#263238",
            highlightthickness=0,
            font=font
        )
        entry_2.place(
            x=52.0,
            y=161.0,
            width=92.0,
            height=15.0
        )

        image_image_11 = PhotoImage(
            file=relative_to_assets("image_11.png"))
        image_11 = canvas.create_image(
            222.0,
            148.0,
            image=image_image_11
        )

        image_image_12 = PhotoImage(
            file=relative_to_assets("image_12.png"))
        image_12 = canvas.create_image(
            222.0,
            174.0,
            image=image_image_12
        )

        entry_image_3 = PhotoImage(
            file=relative_to_assets("entry_3.png"))
        entry_bg_3 = canvas.create_image(
            222.0,
            169.5,
            image=entry_image_3
        )
        entry_3 = Entry(
            bd=0,
            bg="#FDFDFD",
            fg="#263238",
            highlightthickness=0,
            font=font,
            validate='key',
            validatecommand=vcmd
        )
        entry_3.place(
            x=174.0,
            y=161.0,
            width=92.0,
            height=15.0
        )

        entry_2.bind("<KeyRelease>", formatar_moeda)

        self.window.resizable(False, False)
        self.window.mainloop()

if __name__ == '__main__':
    tela = Gui()
    tela.iniciarTela()