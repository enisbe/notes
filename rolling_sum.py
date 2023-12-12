
def rolling_sum2(arr, min_periods=1, ascending=True, window_size_arr = None):
    """
    Apply a rolling sum to each column of a 2D NumPy array, either ascending or descending.
    The window size for each column is determined by its index + 1.

    :param arr: A 2D NumPy array.
    :param min_periods: Minimum number of observations in window required to have a value.
    :param ascending: Boolean indicating the direction of rolling sum (True for ascending, False for descending).
    :return: A 2D NumPy array with rolling sums.
    """
    nrows, ncols = arr.shape
    result = np.empty_like(arr, dtype=float)

    # Reverse array if descending
    if not ascending:
        arr = np.flipud(arr)

    if window_size_arr is None:
        window_size_arr = list(range(ncols))
    
    # Iterate over each column
    for col in range(ncols):
        
        size = window_size_arr[col]
        window_size = size + 1
        
        # Apply rolling sum
        for row in range(nrows):
            if row < window_size - min_periods:
                result[row, col] = np.nan  # Not enough data to fill window
            else:
                start = max(0, row - window_size + 1)
                result[row, col] = arr[start:row + 1, col].sum()

    # Reverse result if descending
    if not ascending:
        result = np.flipud(result)

    return result
