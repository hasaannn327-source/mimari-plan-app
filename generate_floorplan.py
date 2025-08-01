import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc


def draw_room(ax, x, y, w, h, label, area=None, wall_lw=2):
    """Draw a single rectangular room with an optional interior label."""
    # Outer wall of the room
    ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=wall_lw))

    # Label text
    text = label
    if area is not None:
        text += f"\n{area:.0f} m²"
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)


def draw_door(ax, hinge_x, hinge_y, orientation="right", door_w=0.9, lw=1):
    """Draw a simple door with swing arc given a hinge point and orientation."""
    r = door_w  # radius of swing arc equals the door width for simplicity
    if orientation == "right":
        arc = Arc((hinge_x, hinge_y), 2 * r, 2 * r, theta1=270, theta2=360, lw=lw)
        ax.plot([hinge_x, hinge_x], [hinge_y, hinge_y + door_w], color="black", lw=lw)
    elif orientation == "left":
        arc = Arc((hinge_x, hinge_y), 2 * r, 2 * r, theta1=180, theta2=270, lw=lw)
        ax.plot([hinge_x, hinge_x], [hinge_y, hinge_y + door_w], color="black", lw=lw)
    elif orientation == "up":
        arc = Arc((hinge_x, hinge_y), 2 * r, 2 * r, theta1=0, theta2=90, lw=lw)
        ax.plot([hinge_x, hinge_x + door_w], [hinge_y, hinge_y], color="black", lw=lw)
    elif orientation == "down":
        arc = Arc((hinge_x, hinge_y), 2 * r, 2 * r, theta1=90, theta2=180, lw=lw)
        ax.plot([hinge_x, hinge_x + door_w], [hinge_y, hinge_y], color="black", lw=lw)
    else:
        raise ValueError("orientation must be one of right|left|up|down")

    ax.add_patch(arc)


def draw_window(ax, x, y, length, orientation="horizontal", lw=3, color="steelblue"):
    """Draw a window segment as a thicker line along a wall."""
    if orientation == "horizontal":
        ax.plot([x, x + length], [y, y], color=color, lw=lw)
    elif orientation == "vertical":
        ax.plot([x, x], [y, y + length], color=color, lw=lw)
    else:
        raise ValueError("orientation must be horizontal|vertical")


def main():
    # Figure and axes setup
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_aspect("equal")
    ax.axis("off")

    outer_wall_lw = 4

    # --- Building Outline ---
    ax.add_patch(Rectangle((0, 0), 18, 12, fill=False, linewidth=outer_wall_lw))

    # --- Central Hallway & Core (3 m wide) ---
    hallway_x = 7.5
    hallway_w = 3
    ax.add_patch(Rectangle((hallway_x, 0), hallway_w, 12, fill=False, linewidth=2))
    ax.text(hallway_x + hallway_w / 2, 6, "Hallway\n& Stairs", ha="center", va="center", fontsize=9)

    # Stairs (approx. 2 m×4 m)
    ax.add_patch(Rectangle((8, 3), 2, 4, fill=False, linewidth=1))
    ax.text(9, 5, "Stairs", ha="center", va="center", fontsize=7)

    # Elevator (2 m×2 m)
    ax.add_patch(Rectangle((8, 8), 2, 2, fill=False, linewidth=1))
    ax.text(9, 9, "Elevator", ha="center", va="center", fontsize=7)

    # --- Apartments ---
    # Left apartment coordinates
    left_x = 0
    right_x = 10.5
    apt_w = 7.5

    # Apartment labels (type & area)
    ax.text(left_x + apt_w / 2, 11.5, "2+1\n90 m²", ha="center", va="center", fontsize=10, weight="bold")
    ax.text(right_x + apt_w / 2, 11.5, "2+1\n90 m²", ha="center", va="center", fontsize=10, weight="bold")

    # --- Room layout for one apartment (reuse for both sides) ---
    def draw_apartment(origin_x):
        # Living room + Kitchen (front)
        draw_room(ax, origin_x, 0, apt_w, 4.5, "Living\n+ Kitchen", area=34)
        # Bedroom 1
        draw_room(ax, origin_x, 4.5, apt_w / 2, 3.75, "Bedroom 1", area=14)
        # Bedroom 2
        draw_room(ax, origin_x + apt_w / 2, 4.5, apt_w / 2, 3.75, "Bedroom 2", area=14)
        # Bathroom
        draw_room(ax, origin_x, 8.25, 2.5, 3.75, "Bathroom", area=9)
        # Corridor inside apartment
        draw_room(ax, origin_x + 2.5, 8.25, 5, 3.75, "Corridor", area=9)

        # Apartment entrance door from hallway
        if origin_x == left_x:
            draw_door(ax, hallway_x, 2, orientation="left")
        else:
            draw_door(ax, hallway_x + hallway_w, 2, orientation="right")

        # Sample internal doors (corridor → bedrooms)
        # Door to Bedroom 1
        draw_door(ax, origin_x + apt_w / 4, 4.5, orientation="up")
        # Door to Bedroom 2
        draw_door(ax, origin_x + 3 * apt_w / 4, 4.5, orientation="up")
        # Door to Bathroom
        draw_door(ax, origin_x + 2.5, 8.25, orientation="up")

        # Windows: front (living) & back (bedrooms)
        draw_window(ax, origin_x + 1, 0, apt_w - 2, orientation="horizontal")  # front side
        draw_window(ax, origin_x + 1, 12, apt_w - 2, orientation="horizontal")  # back side

    draw_apartment(left_x)
    draw_apartment(right_x)

    # --- Street annotation (bottom side) ---
    ax.annotate("Main Street", xy=(9, -0.6), ha="center", fontsize=9)
    # Direction arrows
    ax.arrow(9, -0.3, 4, 0, head_width=0.3, head_length=0.3)
    ax.arrow(9, -0.3, -4, 0, head_width=0.3, head_length=0.3)

    # Save figure
    plt.savefig("floorplan.png", dpi=300, bbox_inches="tight")
    print("Floor plan generated and saved as floorplan.png")


if __name__ == "__main__":
    main()