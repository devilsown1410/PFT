def pagination(data, page, limit):
    start = (page - 1) * limit
    end = start + limit
    return data[start:end]

def transaction_response(data):
    return list(map(lambda x: {
                "id": x[0],
                "amount": f"${x[1]}",
                "description": x[2],
                "transaction_type": x[3],
                "category_id": x[4],
                "user_id": x[5],
                "transaction_date": x[6]
            }, data))