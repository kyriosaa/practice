def merge_sort(arr):
    # base case
    # list of 0 or 1 elements is already sorted
    if len(arr) <= 1:
        return arr
    
    # divide the list by two
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    # recursive call to both sides
    left_sorted = merge_sort(left_half)
    right_sorted = merge_sort(right_half)
    
    # combine
    return merge(left_sorted, right_sorted)

def merge(left, right):
    sorted_merged = []
    i = j = 0
    
    # compare elements and add the smaller one
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            sorted_merged.append(left[i])
            i += 1
        else:
            sorted_merged.append(right[j])
            j += 1
            
    # append the last element in either list (we dont know which one will have the final element)
    sorted_merged.extend(left[i:])
    sorted_merged.extend(right[j:])
    
    return sorted_merged

if __name__ == "__main__":
    test_arr = [38, 27, 43, 3, 9, 82, 10]
    print(f"original: {test_arr}")
    sorted_arr = merge_sort(test_arr)
    print(f"sorted:   {sorted_arr}")