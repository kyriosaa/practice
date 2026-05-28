# Design an algorithm for computing sqrt(2) for any positive integer n. 
# Besides assignment and comparison, your algorithm may only use the four basic arithmetical operations. 
# In your answer, you first describe the idea (approach) and then the pseudo-code. 

def int_sqrt_algorithm(n):
    left = 1
    right = n
    ans = 1

    while left <= right:
        mid = (left + right) / 2
        square = mid * mid

        if square == n:
            return mid
        
        elif square < n:
            # mid is valid but there might be larger one
            ans = mid
            left = mid + 1

        else:
            # search lower half
            right = mid - 1

    return ans