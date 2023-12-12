import numpy as np

def rolling_sum(arr, min_periods=1, ascending=True, window_sizes=None):
    """
    Apply a rolling sum to each column of a 2D NumPy array, either ascending or descending.
    If window_sizes array is provided, use the respective window size for each column. 
    Otherwise, use the column index + 1 as the window size.

    :param arr: A 2D NumPy array.
    :param min_periods: Minimum number of observations in window required to have a value.
    :param ascending: Boolean indicating the direction of rolling sum (True for ascending, False for descending).
    :param window_sizes: Optional array of window sizes for each column.
    :return: A 2D NumPy array with rolling sums.
    """
    nrows, ncols = arr.shape
    result = np.empty_like(arr, dtype=float)

    # Reverse array if descending
    if not ascending:
        arr = np.flipud(arr)

    # Iterate over each column
    for col in range(ncols):
        # Use provided window size for the column, or column index + 1 if not provided
        current_window_size = window_sizes[col] if window_sizes is not None and col < len(window_sizes) else col + 1
        
        # Apply rolling sum
        for row in range(nrows):
            if row < current_window_size - min_periods:
                result[row, col] = np.nan  # Not enough data to fill window
            else:
                start = max(0, row - current_window_size + 1)
                result[row, col] = arr[start:row + 1, col].sum()

    # Reverse result if descending
    if not ascending:
        result = np.flipud(result)

    return result
