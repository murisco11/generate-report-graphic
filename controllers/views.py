import base64
import io
import matplotlib.pyplot as plt
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

                fig, ax = plt.subplots(figsize=(12, 8))
                ax.set_title(titulo)
                ax.pie(
                    estado_counts,
                    labels=estado_counts.index, # type: ignore
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax.axis("equal")

                response = string

            elif param == "datas":
                datas = data.get("datas", [])
                datas_convertidas = [
                    datetime.strptime(data_str, "%d/%m/%Y").strftime("%m/%Y")
                    for data_str in datas
                ]
                df = pd.DataFrame(datas_convertidas, columns=["Mes_Ano"])
                mes_ano_counts = df["Mes_Ano"].value_counts().sort_index()

                string = [f"{mes_ano}: {count}" for mes_ano, count in mes_ano_counts.items()]

                fig, ax = plt.subplots(figsize=(12, 8))
                ax.bar(mes_ano_counts.index, mes_ano_counts.values) # type: ignore
                ax.set_xlabel("Mês/Ano")
                ax.set_ylabel("Contagem")
                ax.set_title("Contagem de Datas por Mês/Ano")
                ax.set_xticklabels(mes_ano_counts.index, rotation=45)

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
                bins = [5000, 10000, 20000, 50000, 100000] 
                labels = ['5k-10k', '10k-20k', '20k-50k', '50k-100k'] 
                df['Faixas'] = pd.cut(df['Valores'], bins=bins, labels=labels, include_lowest=True)
                faixa_counts = df['Faixas'].value_counts().sort_index()    
                string = [f"{faixa}: {count}" for faixa, count in faixa_counts.items()]
       
                
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.barh(faixa_counts.index, faixa_counts.values) # type: ignore
                ax.set_xlabel("Quantidade de Orçamentos")
                ax.set_ylabel("Faixa de Valores")
                ax.set_title("Distribuição de Orçamentos por Faixa")
                for i, v in enumerate(faixa_counts.values):
                    ax.text(v + 0.5, i, str(v), va='center')

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

                fig, ax = plt.subplots(figsize=(12, 8))
                ticket_medio_estado.plot(kind="barh", ax=ax, color='skyblue')
                ax.set_xlabel("Ticket Médio (R$)")
                ax.set_ylabel("Estado")
                ax.set_title("Ticket Médio por Estado")
                plt.xticks(rotation=45)

                response = string
            
            elif param == "ramos_empresariais":
                ramos = data.get("ramos_empresariais", [])
                print(ramos)
                df = pd.DataFrame(ramos, columns=["Ramos Empresariais"])
                
                ramos_counts = df["Ramos Empresariais"].value_counts()
                string = [f"{ramo}: {count}" for ramo, count in ramos_counts.items()]
            
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.pie(
                        ramos_counts.values, # type: ignore
                        labels=ramos_counts.index, # type: ignore
                        autopct="%1.1f%%",
                        colors=["blue", "green", "orange", "red", "purple"],
                        startangle=140,
                        wedgeprops={"edgecolor": "black"}
    )
                ax.set_title("Distribuição dos Ramos Empresariais")
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

                orcamento_por_ramo = df.groupby("Ramo Empresarial")["Orcamento"].sum()

                fig, ax = plt.subplots(figsize=(10, 8))
                ax.pie(orcamento_por_ramo, labels=orcamento_por_ramo.index, autopct='%1.1f%%', startangle=90) # type: ignore
                ax.axis('equal') 
                ax.set_title("Distribuição do Orçamento por Ramo Empresarial")

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