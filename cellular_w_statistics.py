import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import convolve2d

# Parameters
WIDTH = 200
HEIGHT = 200
RULE = "B368/S245"
KERNEL_SIZE = 3  # (default = 3 Moore neighborhood)

# Initialize the grid with a sparse random distribution
grid = np.random.choice([0, 1], size=(HEIGHT, WIDTH),
                        p=[0.85, 0.15]).astype(np.uint8)

# Statistics tracking
population_counts = []
entropy_values = []


def create_kernel(KERNEL_SIZE):
    """Create the kernel for neighbor computation."""
    kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), dtype=np.uint8)
    kernel[KERNEL_SIZE // 2, KERNEL_SIZE // 2] = 0  # No self-counting
    return kernel


def parse_rule(RULE):
    """Parse the rule into birth and survive conditions."""
    birth, survive = RULE.split('/')
    birth_conditions = list(map(int, birth[1:]))
    survive_conditions = list(map(int, survive[1:]))
    return birth_conditions, survive_conditions


def compute_neighbors(grid, kernel):
    """Compute the number of neighbors for each cell."""
    return convolve2d(grid, kernel, mode='same', boundary='wrap').astype(np.uint8)


def compute_entropy(grid):
    """Compute the Shannon entropy of the grid."""
    total_cells = grid.size
    p_alive = np.sum(grid) / total_cells
    p_dead = 1 - p_alive

    entropy = 0
    if p_alive > 0:
        entropy -= p_alive * np.log2(p_alive)
    if p_dead > 0:
        entropy -= p_dead * np.log2(p_dead)

    return entropy


def apply_rule(grid, neighbors, birth_conditions, survive_conditions):
    """Apply the cellular automaton rule to the grid."""
    birth_mask = (grid == 0) & np.isin(neighbors, birth_conditions)
    survive_mask = (grid == 1) & np.isin(neighbors, survive_conditions)
    new_grid = np.zeros_like(grid, dtype=np.uint8)
    new_grid[birth_mask | survive_mask] = 1
    return new_grid


def update(frame, img, grid, birth_conditions, survive_conditions, kernel, stats_ax, stats_ax2, stats_fig):
    """Update the grid and statistics for each animation frame."""
    neighbors = compute_neighbors(grid, kernel)
    new_grid = apply_rule(
        grid, neighbors, birth_conditions, survive_conditions)
    grid[:] = new_grid
    img.set_data(grid)

    # Track population
    live_cells = np.sum(grid)
    population_counts.append(live_cells)

    # Compute and track entropy
    entropy = compute_entropy(grid)
    entropy_values.append(entropy)

    # Update statistics plot
    stats_ax.clear()
    stats_ax2.clear()

    stats_ax.plot(population_counts, label='Live Cells', color='blue')
    stats_ax.set_xlabel("Time Step")
    stats_ax.set_ylabel("Live Cells", color='blue')
    stats_ax.tick_params(axis='y', labelcolor='blue')

    stats_ax2.plot(entropy_values, label='Shannon Entropy',
                   linestyle='dashed', color='red')
    stats_ax2.set_ylabel("Entropy", color='red')
    stats_ax2.tick_params(axis='y', labelcolor='red')

    # Print entropy value near last point
    stats_ax2.text(len(entropy_values) - 1, entropy_values[-1], f"{entropy_values[-1]:.2f}",
                   color='red', fontsize=10, verticalalignment='bottom', horizontalalignment='right')

    stats_ax.set_title("Population Decay & Entropy Over Time")

    # Apply legends
    stats_ax.legend(loc='upper left')
    stats_ax2.legend(loc='upper right')

    # ***KEY CHANGE: Manually Position Labels***
    stats_ax.yaxis.set_label_position("left")  # Force left for Live Cells
    stats_ax2.yaxis.set_label_position("right")  # Force right for Entropy

    # Force update
    stats_fig.canvas.draw_idle()
    plt.pause(0.01)

    return img,


def create_plots(grid):
    """Create the figures and axes for the automaton and statistics."""
    fig, ax = plt.subplots(figsize=(10, 10))
    img = ax.imshow(grid, cmap='gray', interpolation='nearest')
    ax.set_title(f"2D Cellular Automaton (Rule {RULE})")
    ax.axis('off')

    stats_fig, stats_ax = plt.subplots()
    stats_ax2 = stats_ax.twinx()

    stats_ax.set_ylabel("Live Cells", color='blue')
    stats_ax.tick_params(axis='y', labelcolor='blue')
    stats_ax.yaxis.label.set_color('blue')

    stats_ax2.set_ylabel("Entropy", color='red')
    stats_ax2.tick_params(axis='y', labelcolor='red')
    stats_ax2.yaxis.label.set_color('red')

    return fig, ax, stats_fig, stats_ax, stats_ax2, img


def on_close(event, ani):
    """Stop the animation when the window is closed."""
    if ani.event_source is not None:
        ani.event_source.stop()


def main():
    """Main function to set up and run the simulation."""
    # Parse the rule and create the kernel
    birth_conditions, survive_conditions = parse_rule(RULE)
    kernel = create_kernel(KERNEL_SIZE)

    # Create the plot and animation setup
    fig, ax, stats_fig, stats_ax, stats_ax2, img = create_plots(grid)

    # Create the animation
    ani = animation.FuncAnimation(
        fig, update,
        fargs=(img, grid, birth_conditions, survive_conditions,
               kernel, stats_ax, stats_ax2, stats_fig),
        interval=50, blit=False, cache_frame_data=False
    )

    # Connect the close event to stop the animation
    fig.canvas.mpl_connect('close_event', lambda event: on_close(event, ani))
    stats_fig.canvas.mpl_connect(
        'close_event', lambda event: on_close(event, ani))

    # Display the animation and stats
    plt.show()


if __name__ == "__main__":
    main()
