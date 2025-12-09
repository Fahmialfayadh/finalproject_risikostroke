def merge_sort(records, key, reverse=False):
    # Base case
    if len(records) <= 1:
        return records

    mid = len(records) // 2
    left = merge_sort(records[:mid], key, reverse)
    right = merge_sort(records[mid:], key, reverse)

    return merge(left, right, key, reverse)


def merge(left, right, key, reverse):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        a = getattr(left[i], key)
        b = getattr(right[j], key)

        if reverse:
            if a > b:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if a < b:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
# ===========================

def search(records, query, fields):
    query = query.lower()
    filtered = []

    for record in records:
        for field in fields:
            value = getattr(record, field, "") or ""
            value = str(value).lower()

            if query in value:
                filtered.append(record)
                break  # ini benar (keluar dari loop field)
    
    return filtered
