import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import convolve2d

# Parameters
WIDTH, HEIGHT = 200, 200
RULE = "B3/S23"
KERNEL_SIZE = 3  # Moore neighborhood

# Initialize the grid with a sparse random distribution
grid = np.random.choice([0, 1], size=(HEIGHT, WIDTH),
                        p=[0.85, 0.15]).astype(np.uint8)


def create_kernel(size):
    """Create a convolution kernel of given size."""
    kernel = np.ones((size, size), dtype=np.uint8)
    kernel[size // 2, size // 2] = 0  # Exclude the center cell
    return kernel


def parse_rule(rule):
    """Parse the rule string (e.g., 'B3/S23') into birth and survival conditions."""
    if '/' not in rule or not rule.startswith('B') or 'S' not in rule:
        raise ValueError("Invalid rule format. Expected 'Bx/Sy'.")

    birth, survive = rule.split('/')
    try:
        birth_conditions = list(map(int, birth[1:]))
        survive_conditions = list(map(int, survive[1:]))
    except ValueError:
        raise ValueError(
            "Invalid rule format. Expected 'Bx/Sy' with numeric values.")

    return birth_conditions, survive_conditions


def compute_neighbors(grid, kernel):
    """Calculate the number of alive neighbors for each cell."""
    return convolve2d(grid, kernel, mode='same', boundary='wrap').astype(np.uint8)


def apply_rule(grid, neighbors, birth_conditions, survive_conditions):
    """Update the grid based on birth and survival rules."""
    birth_mask = (grid == 0) & np.isin(neighbors, birth_conditions)
    survive_mask = (grid == 1) & np.isin(neighbors, survive_conditions)
    grid[:] = 0  # Reset all cells to dead
    grid[birth_mask | survive_mask] = 1  # Apply rules
    return grid


def update(frame, img, grid, birth_conditions, survive_conditions, kernel):
    """Update function for the animation."""
    neighbors = compute_neighbors(grid, kernel)
    apply_rule(grid, neighbors, birth_conditions, survive_conditions)
    img.set_data(grid)  # Update displayed image
    return img,


def create_plot(grid):
    """Set up the figure and axis for visualization."""
    fig, ax = plt.subplots(figsize=(10, 10))
    img = ax.imshow(grid, cmap='gray', interpolation='nearest')
    ax.set_title(f"2D Cellular Automaton (Rule {RULE})")
    ax.axis('off')
    return fig, ax, img


def on_close(event, ani):
    """Stop the animation when the window is closed."""
    if ani.event_source is not None:
        ani.event_source.stop()


def main():
    """Main function to initialize and run the simulation."""
    birth_conditions, survive_conditions = parse_rule(RULE)
    kernel = create_kernel(KERNEL_SIZE)

    fig, ax, img = create_plot(grid)

    ani = animation.FuncAnimation(
        fig, update,
        fargs=(img, grid, birth_conditions, survive_conditions, kernel),
        interval=50, blit=False, cache_frame_data=False
    )

    fig.canvas.mpl_connect('close_event', lambda event: on_close(event, ani))
    plt.show()


if __name__ == "__main__":
    main()
