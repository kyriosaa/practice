# Design and develop a non-recursive, linear-time algorithm for the maximum subarray problem.

def max_subarray_linear(A):
    # init variables
    max_sum = current_sum = A[0]
    best_start = best_end = current_start = 0

    # iterate through the array starting from the second element
    for i in range(1, len(A)):
        # decide whether to add the current element to the running subarray or just start a brand new subarray from the current element
        if current_sum + A[i] > A[i]:
            current_sum += A[i]
        else:
            current_sum = A[i]
            current_start = i  # reset start pointer

        # if new global maximum is found, update the tracking variables
        if current_sum > max_sum:
            max_sum = current_sum
            best_start = current_start
            best_end = i
            
    # return the start index, end index, and the maximum sum
    return (best_start, best_end, max_sum)