import base64
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.ddd_estados import DDD_ESTADOS
import json
from datetime import datetime


@csrf_exempt 
def index(request):
    if request.method == "POST":
        param = request.GET.get("param")

        if not param:
            return JsonResponse(
                {"Erro: Insira um parâmetro válido!": str(e)}, status=404 # type: ignore
            )
        try:
            data = json.loads(request.body)
            response = []

            if param == "telefones":
                telefones = data.get("telefones", [])
                titulo = data.get("titulo")

                estados = []
                for telefone in telefones:
                    ddd = str(telefone)[2:4]
                    estado = DDD_ESTADOS.get(ddd)
                    if estado:
                        estados.append(estado)

                df = pd.DataFrame(estados, columns=["Estado"])
                estado_counts = df["Estado"].value_counts()
                string = [f"{estado}: {count}" for estado, count in estado_counts.items()]
                response = string

                plt.figure(figsize=(12, 8))
                sns.barplot(x=estado_counts.index, y=estado_counts.values, palette="Blues_d")
                plt.title(titulo, fontsize=16)
                plt.xlabel("Estado", fontsize=12)
                plt.ylabel("Quantidade", fontsize=12)
                plt.xticks(rotation=15)
                for i, v in enumerate(estado_counts.values):
                    plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=8)

                response = string

            elif param == "datas":
                datas = data.get("datas", [])
                datas_convertidas = [
                    datetime.strptime(data_str, "%d/%m/%Y") for data_str in datas
                ]

                df = pd.DataFrame(datas_convertidas, columns=["Data"])
                df["Ano"] = df["Data"].dt.year
                df["Mês"] = df["Data"].dt.month
                df["Trimestre"] = ((df["Mês"] - 1) // 3) + 1
                df["Trimestre_Ano"] = df["Ano"].astype(str) + " - T" + df["Trimestre"].astype(str)
                trimestre_counts = df["Trimestre_Ano"].value_counts().sort_index()

                string = [f"{trimestre}: {count}" for trimestre, count in trimestre_counts.items()]

                plt.figure(figsize=(12, 8))
                sns.barplot(x=trimestre_counts.index, y=trimestre_counts.values, color='skyblue')
                plt.xlabel("Trimestre/Ano")
                plt.ylabel("Contagem")
                plt.title("Contagem de Datas por Trimestre/Ano")
                plt.xticks(rotation=45)
                plt.tight_layout()

                for i, v in enumerate(trimestre_counts.values):
                    plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10)

                response = string

            elif param == "dispositivos":
                dispositivos = data.get("dispositivos", [])
                df = pd.DataFrame(dispositivos, columns=["Dispositivos"])
                if not dispositivos:
                    return JsonResponse(
                        {"Erro": "Nenhum dispositivo fornecido"}, status=404
                    )

                dispositivos_counts = df["Dispositivos"].value_counts()
                string = [f"{dispositivo}: {count}" for dispositivo, count in dispositivos_counts.items()]


                fig, ax = plt.subplots(figsize=(12, 8))
                ax.bar(dispositivos_counts.index, dispositivos_counts.values) # type: ignore
                ax.set_xlabel("Dispositivos")
                ax.set_ylabel("Contagem")
                ax.set_title("Contagem de Dispositivos")
                ax.set_xticklabels(dispositivos_counts.index, rotation=45)

                response = string

            elif param == "canais_posicionamento":
                canais = data.get("canais_posicionamento", [])
                df = pd.DataFrame(canais, columns=["Canais"])
                canais_counts = df["Canais"].value_counts()
                string = [f"{canal}: {count}" for canal, count in canais_counts.items()]


                fig, ax = plt.subplots(figsize=(12, 8))
                ax.bar(
                    canais_counts.index,
                    canais_counts.values, # type: ignore
                    color=["blue", "green", "orange"],
                )
                ax.set_xlabel("Canais")
                ax.set_ylabel("Quantidade")
                ax.set_title("Contagem de Canais de Posicionamento")
                ax.set_xticklabels(canais_counts.index, rotation=45)

                response = string

            elif param == "orcamentos_medidas":
                orcamentos = data.get("orcamentos", [])
                df = pd.DataFrame(orcamentos, columns=["Valores"])

                max_valor = df["Valores"].max().item()
                min_valor = df["Valores"].min().item()
                mediana = df["Valores"].median().item() # type: ignore
                soma = df["Valores"].sum().item()
                media = df["Valores"].mean().item() # type: ignore

                return JsonResponse(
                    {
                        "mensagem": "Relatório dos orçamentos gerado com sucesso.",
                        "valores": {
                            "maximo": max_valor,
                            "minimo": min_valor,
                            "mediana": mediana,
                            "soma": soma,
                            "media": media,
                        },
                    },
                    status=200,
                )

            elif param == "orcamentos_grafico":
                orcamentos = data.get("orcamentos", [])
                df = pd.DataFrame(orcamentos, columns=["Valores"])
                bins = [5000, 10000, 20000, 50000, 100000, 200000, 300000, 500000, 1000000] 
                labels = ['5k-10k', '10k-20k', '20k-50k', '50k-100k', '100k-200k', '200k-300k', '300k-500k', '500k-1m'] 
                df['Faixas'] = pd.cut(df['Valores'], bins=bins, labels=labels, include_lowest=True)
                faixa_counts = df['Faixas'].value_counts().sort_index()    
                string = [f"{faixa}: {count}" for faixa, count in faixa_counts.items()]
       
                plt.figure(figsize=(12, 8))
                sns.set_style("whitegrid")
                bar_plot = sns.barplot(x=faixa_counts.index, y=faixa_counts.values, palette="Blues_r")

                for p in bar_plot.patches:
                    bar_plot.annotate(f'{p.get_height()}',  # type: ignore
                                    (p.get_x() + p.get_width() / 2., p.get_height()),  # type: ignore
                                    ha='center', va='center', 
                                    fontsize=12, color='black', 
                                    xytext=(0, 10), textcoords='offset points')
                plt.title("Distribuição de Orçamentos por Faixa", fontsize=16)
                plt.xlabel("Faixa de Valores", fontsize=12)
                plt.ylabel("Quantidade de Orçamentos", fontsize=12)
                plt.xticks(rotation=45, ha='right') 

                response = string

            elif param == "ticket_medio_estados":
                data = data.get("data", []) 
                estados = []
                orcamentos = []

                for item in data: 
                    telefone = item["telefone"]
                    orcamento = item["orcamento"]
                    ddd = str(telefone)[2:4] 
                    estado = DDD_ESTADOS.get(ddd) 
    
                    if estado: 
                        estados.append(estado)
                        orcamentos.append(orcamento)

                df = pd.DataFrame({"Estado": estados, "Orcamento": orcamentos})
                ticket_medio_estado = df.groupby("Estado")["Orcamento"].mean()
                ticket_medio_estado = ticket_medio_estado.sort_values()

                string = [f"{ticket_medio}: {count}" for ticket_medio, count in ticket_medio_estado.items()]

                plt.figure(figsize=(12, 8))
                ax = sns.barplot(x=ticket_medio_estado.values, y=ticket_medio_estado.index, palette='Blues_r')
                for i, v in enumerate(ticket_medio_estado.values):
                    ax.text(v + 0.5, i, f'R$ {v:,.2f}', color='black', va='center')
                ax.set_xlabel("Ticket Médio (R$)", fontsize=14)
                ax.set_ylabel("Estado", fontsize=14)
                ax.set_title("Ticket Médio por Estado", fontsize=16)

                response = string
            
            elif param == "ramos_empresariais":
                ramos = data.get("ramos_empresariais", [])
                
                df = pd.DataFrame(ramos, columns=["Ramos Empresariais"])
                ramos_counts = df["Ramos Empresariais"].value_counts()

                plt.figure(figsize=(12, 8))
                sns.barplot(
                    x=ramos_counts.values, 
                    y=ramos_counts.index, 
                    palette="viridis"
                )
                plt.xlabel("Quantidade de Empresas", fontsize=12)
                plt.ylabel("Ramos Empresariais", fontsize=12)
                plt.title("Distribuição dos Ramos Empresariais", fontsize=14)
                for index, value in enumerate(ramos_counts.values):
                    plt.text(value + 1, index, str(value), va='center', fontsize=10)
                plt.grid(axis="x", linestyle="--", alpha=0.7)
                plt.tight_layout()

                string = [f"{ramo}: {count}" for ramo, count in ramos_counts.items()]
                response = string

            elif param == "empresarial_orcamento":
                data = data.get("data", [])
                ramos_empresariais = []
                orcamentos = []

                for item in data:
                    ramo = item["ramo_empresarial"]
                    orcamento = item["orcamento"]
        
                    ramos_empresariais.append(ramo)
                    orcamentos.append(orcamento)

                df = pd.DataFrame({"Ramo Empresarial": ramos_empresariais, "Orcamento": orcamentos})
                df_total = df.groupby("Ramo Empresarial")["Orcamento"].sum().sort_values(ascending=False).reset_index()

                plt.figure(figsize=(12, 8))
                sns.barplot(
                    data=df_total, 
                    y="Ramo Empresarial", 
                    x="Orcamento", 
                    palette="Blues_r"
                )
                ax = plt.gca()
                ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
                plt.xlabel("Orçamento Total (R$)")
                plt.ylabel("Ramo Empresarial")
                plt.title("Orçamento Total por Ramo Empresarial")
                plt.grid(axis="x", linestyle="--", alpha=0.7)
                plt.tight_layout()

                string = [f"{ramo}: R${orcamento:,.2f}" for ramo, orcamento in zip(df_total["Ramo Empresarial"], df_total["Orcamento"])]
                response = string

            buffer = io.BytesIO()  
            plt.savefig(buffer, format="png") 
            buffer.seek(0)  
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()

            return JsonResponse(
                {
                    "grafico_base64": image_base64,
                    "mensagem": "Gráfico gerado com sucesso. String BASE64 Disponível.",
                    "response": response
                },
                status=200,
            ) 

        except Exception as e:
            return JsonResponse({"mensagem": f"Ocorreu um erro: {str(e)}"}, status=400)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)