def build_email(order: dict) -> dict:
    """
    Monta o e-mail de confirmação do pedido.
    Retorna um dict com 'subject', 'html' e 'text'
    (texto puro como fallback para clientes que não renderizam HTML).
    """
    order_id      = order["order_id"]
    customer_name = order["customer_name"]
    product       = order["product"]
    quantity      = order["quantity"]
    created_at    = order["created_at"]

    subject = f"Pedido #{order_id[:8].upper()} confirmado!"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2 style="color: #2d6a4f;">✅ Pedido confirmado!</h2>
        <p>Olá, <strong>{customer_name}</strong>!</p>
        <p>Recebemos seu pedido com sucesso. Aqui estão os detalhes:</p>

        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background: #f0f0f0;">
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Pedido</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">#{order_id[:8].upper()}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Produto</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{product}</td>
            </tr>
            <tr style="background: #f0f0f0;">
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Quantidade</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{quantity}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Data</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{created_at}</td>
            </tr>
        </table>

        <p style="margin-top: 24px; color: #555;">
            Obrigado por comprar conosco!
        </p>
        <p style="color: #aaa; font-size: 12px;">
            Este é um e-mail automático, não responda.
        </p>
    </body>
    </html>
    """

    text = (
        f"Pedido confirmado!\n\n"
        f"Olá, {customer_name}!\n"
        f"Pedido: #{order_id[:8].upper()}\n"
        f"Produto: {product}\n"
        f"Quantidade: {quantity}\n"
        f"Data: {created_at}\n\n"
        f"Obrigado por comprar conosco!"
    )

    return {"subject": subject, "html": html, "text": text}