# utils.py
def merge_sort_flights(flights, key=lambda x: x.price):
    if len(flights) <= 1:
        return flights
    mid = len(flights) // 2
    left = merge_sort_flights(flights[:mid], key)
    right = merge_sort_flights(flights[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    sorted_list = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) < key(right[j]):
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list
