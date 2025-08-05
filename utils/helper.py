def pagination(data, page, limit):
    start = (page - 1) * limit
    end = start + limit
    return data[start:end]