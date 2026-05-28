# insertion sort is basically creating two sub-arrays (sorted, unsorted)
# and sorting from the unsorted into the sorted

def recursive_insertion_sort(array, n):     
    # base case
    if n <= 1:
        return
    
    # recursively sort the first n-1 items
    recursive_insertion_sort(array, n-1)

    # insert nth item in the sorted part
    key = array[n-1]
    i = n-2
    while i >= 0 and array[i] > key:
        array[i+1] = array[i]
        i -= 1
    array[i+1] = key