# Asteroids Game

This is an implementation of the classic arcade game Asteroids.

## Gameplay

You pilot a spaceship, represented by a triangle, in a field of dangerous asteroids. Your objective is to survive as long as possible by moving your ship and shooting to destroy the incoming asteroids.

## Features
- Arcade-style physics with asteroid collisions based on size
- Three different control schemes (tank, mouse ship-relative, mouse screen-relative)
- Configurable difficulty scaling over time  
- Multiple boundary behaviors (wrap, bounce, etc.)
- Invulnerability periods with visual feedback

## Controls

The game supports three different control schemes to suit different player preferences:

### Tank Controls (Default)
*   **WASD** keys for ship-relative movement and rotation
*   **W/S** - Move forward/backward along ship's facing direction
*   **A/D** - Rotate ship left/right
*   **SPACE** - Fire weapon

### Mouse Ship-Relative Controls  
*   **Mouse** - Aim ship direction
*   **WASD** - Move relative to ship orientation
*   **W/S** - Move forward/backward along ship's facing direction
*   **A/D** - Strafe left/right relative to ship
*   **SPACE** - Fire weapon

### Mouse Screen-Relative Controls
*   **Mouse** - Aim ship direction  
*   **WASD** - Move relative to screen
*   **W** - Move up on screen
*   **S** - Move down on screen
*   **A** - Move left on screen
*   **D** - Move right on screen
*   **SPACE** - Fire weapon

*Control scheme can be changed in `settings/controls.py` by modifying `ACTIVE_CONTROL_SCHEME`.*

## Key Concepts & Mechanics

*   **Asteroid Splitting:** When hit by a shot, larger asteroids get reduced in size and may split into smaller fragments.
*   **Invulnerability:** Newly spawned or split asteroids are temporarily invulnerable, indicated by blinking and/or a thicker border.
*   **Game Over:** Collision with an asteroid results in instant game over.
*  **Collision Detection:** For collision between circular shapes (the player's ship, asteroids and shots) a precise circular collision detection method is used. For simpler checks, such as determining if a sprite is outside the screen boundaries, Pygame's built-in rectangular collision checks (`sprite.rect.colliderect()`) are used. This is less precise for rotation but efficient for basic boundary checks.
*  **Scoring:** Currently, there is no scoring system or explicit win condition, but the game will display your survival time at the end of each attempt.

## Collision Detection

Collision detection is handled in two main ways in this game:

1.  **Circular Collision:** For checking overlaps between game objects that are circular in shape (the player's ship, asteroids, and shots), a precise circular collision detection method is used. This checks if the distance between the centers of two circular objects is less than the sum of their radii. This logic is primarily implemented within the `CircleShape.check_collision()` method and utilized in the `Game.handle_collisions()` loop.

2.  **Rectangular Collision:** For simpler checks, such as determining if a sprite is outside the screen boundaries, Pygame's built-in rectangular collision checks (`sprite.rect.colliderect()`) are used. This is less precise for rotation but efficient for basic boundary checks.

All collision responses (like splitting asteroids or triggering game over) are handled in the `Game.handle_collisions()` method based on the results of these checks.

## Built With

This project is based on a Guided Project from [Boot.dev](https://boot.dev), a platform focused on teaching programming through hands-on coding challenges.

Development was greatly aided by the sage advice and debugging assistance provided by Boots, the AI teaching assistant on Boot.dev.

## Installation

To get a copy of the game up and running on your local machine, follow these steps:

1.  **Clone the repository:**
    Open your terminal and run the following command to download the project files:
    ```bash
    git clone https://github.com/TobiasPartzsch/asteroids-game.git
    ```

2.  **Navigate into the project directory:**
    Change your current directory to the newly cloned project folder:
    ```bash
    cd asteroids-game
    ```

3.  **Set up a virtual environment (recommended):**
    It's best practice to install project dependencies within a virtual environment to avoid conflicts with your system's Python packages.
    ```bash
    python -m venv .venv
    ```
    This command creates a virtual environment named `.venv` in the project directory.

4.  **Activate the virtual environment:**
    You need to activate the virtual environment to use the Python interpreter and packages within it. The command depends on your operating system and shell:

    *   **On Linux or macOS (Bash/Zsh):**
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```

5.  **Install dependencies:**
    With the virtual environment activated, install the necessary Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
    This command reads the list of required packages from the `requirements.txt` file and installs them into your virtual environment.

Once these steps are complete, you are ready to run the game!

## How to Run

After following the installation steps and activating the virtual environment, you can run the game using the shell script you created or directly with Python:

*   **Using the run script (recommended):**
    Navigate to the project's root directory in your terminal and **ensure your virtual environment is activated**. Then run:
    ```bash
    ./run_game.sh
    ```
    (Make sure the script is executable: `chmod +x run_game.sh`)

*   **Directly with Python:**
    Navigate to the project's root directory in your terminal (with the virtual environment activated) and run:
    ```bash
    python src/main.py
    ```
    *(Note: If `python` doesn't point to the correct interpreter in your activated venv, you might need `python3` instead, but this should not be necessary if the venv is activated correctly.)*

## Adjusting Settings

Many aspects of the game can be customized by modifying the settings files located in the `settings/` and `src/` directories. These settings are defined as Python constants.

You can adjust values like screen dimensions, game speed, asteroid behavior, and more to change the difficulty or visual style.

This section details the primary settings available for adjusting the game's difficulty, visuals, and behavior.


*   **`settings/graphics.py`**:
    *   `SCREEN_WIDTH` (`int`) and `SCREEN_HEIGHT` (`int`): Adjust the window dimensions.
    *   `FPS` (`int`): Change the frame rate. Higher values provide smoother motion but may impact performance.
    *   `GameColors` (`StrEnum`): Modify the predefined color names used throughout the game.
    *   `ASTEROID_BORDER_COLOR_OPTIONS` (`tuple[str | tuple[int, int, int], ...]`) and `ASTEROID_FILL_COLOR_OPTIONS` (`tuple[str | tuple[int, int, int], ...]`) : These tuples define the pool of colors (using color names or RGB tuples) that asteroids will randomly select from for their borders and fills when created. Add or remove options to change the visual variety.
    *   `BorderWidths` (`IntEnum`): Adjust the integer values for the border thickness of different game objects.

*   **`settings/asteroids.py`**:

    **Shape Settings:**
    *   `MIN_RADIUS` (`float`): The base size of the smallest asteroid tier.
    *   `SIZES` (`int`): The total number of asteroid size tiers (e.g., 5 sizes means radii of `MIN_RADIUS * 1`, `MIN_RADIUS * 2`, ..., `MIN_RADIUS * 5`).
    *   `MAX_RADIUS` (`float`): The calculated maximum radius for the largest asteroid tier (`MIN_RADIUS * SIZES`).

    **Spawning Settings:**
    *   **Growth Functions**: The game uses `GrowthSetting` dataclasses to define how certain parameters change over time, making the game progressively more challenging. Each `GrowthSetting` specifies:
        *   `function_type`: Either `GrowthFunction.POLYNOMIAL` or `GrowthFunction.EXPONENTIAL`
        *   `coefficients`: A tuple of numbers that define the growth curve
        
        **Polynomial functions** (`ax^n + bx^(n-1) + ... + k`) use coefficients in decreasing power order:
        *   `(0.1, 2.0)` represents `0.1*time + 2.0` (linear growth)
        *   `(0.05, 0.1, 1.0)` represents `0.05*time² + 0.1*time + 1.0` (quadratic growth)
        
        **Exponential functions** (`ae^(bx)`) use exactly two coefficients `(a, b)`:
        *   `(1.0, 0.03)` represents `1.0 * e^(0.03*time)` (exponential growth)
    
    *   `SPAWN_RATE_GROWTH` (`GrowthSetting`): Controls how frequently new asteroids are added to the game over time. Uses a `GrowthSetting` dataclass with configurable growth functions.
    *   `STARTING_SPEED_SPREAD` (`tuple[float, float]`): A `(min, max)` tuple defining the range of initial speeds in pixels per second for newly spawned asteroids.
    *   `SPEED_GROWTH` (`GrowthSetting`): Defines a multiplier applied to asteroid speeds over time, making asteroids progressively faster as the game continues.
    *   `SPAWN_INVUL_TIME_IN_SEC` (`float`): The duration in seconds that a new or split asteroid is invulnerable (indicated by blinking).
    *   `MAX_SPAWN_ATTEMPTS` (`int`): Maximum attempts to find a clear spawn location before giving up.

    **Splitting Settings:**
    *   `SPLIT_SPEEDUP` (`float`): A multiplier applied to the parent asteroid's velocity for newly created fragments.
    *   `SPLIT_DIRECTIONS` (`tuple[float, ...]`): Multipliers applied to `SPLIT_ANGLE` to determine fragment directions. For example, `(-1, 1)` creates two fragments, while `(-0.5, 0, 0.5)` creates three.
    *   `SPLIT_ANGLE` (`tuple[float, float]`): A `(min, max)` range in degrees for the random split angle.

    **Collision Settings:**
    *   `COLLISION_ENABLED` (`bool`): Set to `True` to enable asteroid-asteroid collisions with physics-based bouncing.
    *   `ON_COLLISION` (`CollisionBehavior`): Defines the behavior when two asteroids collide (options: `NOTHING`, `DELETE`, `SPLIT`, `BOUNCE`).

    **Visual Settings:**
    *   `BORDER_WIDTH_INVULNERABLE_MULTIPLIER` (`int`): Multiplier for border thickness during invulnerability periods.
    *   `INVULNERABILITY_BLINKING_PER_SECOND` (`float`): How many times per second invulnerable asteroids blink.
    *   `INVULNERABILITY_BLINK_PATTERN` (`tuple[int, int]`): Pattern for blinking as `(on_cycles, off_cycles)`.

*   **`settings/controls.py`**:
    *   `ACTIVE_CONTROL_SCHEME`: Choose between `TANK_CONTROLS`, `MOUSE_SHIP_CONTROLS`, or `MOUSE_SCREEN_CONTROLS`
    *   **Control Scheme Configuration**: Each scheme defines movement type, turn behavior, and key mappings
    *   **Movement Types**: `TANK` (classic), `MOUSE_SHIP_RELATIVE` (mouse aiming + ship movement), `MOUSE_SCREEN_RELATIVE` (mouse aiming + screen movement)
    *   **Turn Behaviors**: `SMOOTH` (gradual rotation), `MOUSE_FOLLOW` (instant/smooth mouse following), `DISCRETE` (snap to angles)

*   **`src/player.py`**:
    *   `RADIUS` (`float`): The size of the player's spaceship.
    *   `TURN_SPEED` (`float`): How fast the player's spaceship rotates (e.g., in degrees per second).
    *   `SPEED` (`float`): How fast the player's spaceship moves forward and backward (e.g., in pixels per second).
    *   `SHOOT_COOLDOWN_SECOND` (`float`): The time in seconds the player must wait between firing shots. A lower value allows faster shooting (makes the game easier).
    *   `BOUNDARY_BEHAVIOR` (`BoundaryBehavior`): Defines how the player's spaceship behaves when it reaches the screen boundaries (e.g., wrap around, bounce).

*   **`src/shot.py`**:
    *   `SPEED` (`float`): The speed of the player's shots (e.g., in pixels per second). Increasing this makes shots travel faster (makes the game easier).
    *   `RADIUS` (`float`): The size of the player's shots. Increasing this makes shots larger and potentially easier to hit targets with (makes the game easier).

## Development Challenges

During the development of this game, we encountered a couple of notable challenges:

1.  **Boundary Handling Complexity:** Implementing the various boundary behaviors (like wrapping or bouncing) proved to be more complex than initially anticipated. While the logic was designed based on geometric principles, a subtle error in handling collisions with vertical and horizontal edges caused unexpected bounce behavior. Debugging this required careful examination of the collision points and velocity vector changes at the boundaries.

2.  **Mutable Vector Behavior and Splitting:** A significant challenge arose from a misunderstanding of how `pygame.Vector2` objects are handled in Python, particularly with in-place operations like `+=`. When creating fragments during asteroid splits, passing the parent asteroid's position vector by reference (instead of a copy) led to all fragments sharing the *same* position object. Subsequent `+=` operations on the position of one fragment would unexpectedly modify the position of all other fragments (and the parent), resulting in the fragments appearing stacked and moving incorrectly (e.g., appearing to jump forward or only one being visible). This was resolved by ensuring a `.copy()` of the position vector was used when initializing new fragments, ensuring each sprite instance had its own unique position object. This highlighted the crucial difference between operations that modify mutable objects in place (`+=`) versus those that return new objects (`*=` or multiplication followed by assignment).
This was resolved after a careful debugging process that involved extensive logging and tracking of the vector's state.

These challenges were valuable learning experiences and demonstrate the importance of careful state management and understanding the nuances of object mutability in Python.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open a pull request on the [GitHub repository](https://github.com/TobiasPartzsch/asteroids-game). I will review them (eventually).

## Contact

If you have any questions or would like to discuss the project, you can reach out via the [Boot.dev Discord server](https://boot.dev/community). Look for me there!

I've made a dedicated post about this project seeking feedback [here](https://discordapp.com/channels/551921866173054977/1385922425937727528).
