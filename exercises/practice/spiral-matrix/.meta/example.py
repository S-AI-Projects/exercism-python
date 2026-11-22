def spiral_matrix(size):
    matrix = [[0] * size for _ in range(size)]
    row = 0
    col = -1
    element = 1

    # Direction vectors for traversing East (right), South (down), West (left), North (up)
    row_deltas = [0, 1, 0, -1]
    col_deltas = [1, 0, -1, 0]

    # A spiral matrix traverses 2 * size - 1 directional segments.
    # Invariant: Step lengths decrease by 1 every two segments: size, size-1, size-1, size-2, size-2...
    # The formula (2 * size - segment_index) // 2 computes the exact step count for each segment.
    for segment_index in range(2 * size - 1):
        segment_steps = (2 * size - segment_index) // 2
        for _ in range(segment_steps):
            row += row_deltas[segment_index % 4]
            col += col_deltas[segment_index % 4]
            matrix[row][col] = element
            element += 1

    return matrix
