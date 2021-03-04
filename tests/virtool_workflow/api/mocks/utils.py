from datetime import datetime


async def read_file_from_request(request, name, format) -> dict:
    reader = await request.multipart()
    file = await reader.next()

    size = 0
    while True:
        chunk = await file.read_chunk(1000)
        if not chunk:
            break
        size += len(chunk)

    return {
        "id": 1,
        "description": None,
        "name": name,
        "format": format,
        "name_on_disk": f"1-{name}",
        "size": size,
        "uploaded_at": str(datetime.now()),
    }
