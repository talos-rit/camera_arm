from enum import Enum
from publisher import Publisher
import tkinter
import time
from threading import Thread


class Direction(Enum):
    """ Directional Enum for interface controls

    """
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __int__(self):
        """
        Used for casting Enum object to integer
        """
        return self.value


class ManualInterface:
    """
    Representation of a manual interface used to control 
    the robotic arm which holds the camera.
    """
    
    def __init__(self):
        """ Constructor sets up tkinter manual interface, including buttons and labels
        """
        
         # unicode button symbols
        
        self.up_arrow = "\u2191"
        self.down_arrow = "\u2193"
        self.left_arrow = "\u2190"
        self.right_arrow = "\u2192"
        self.home = "🏠"
        self.switch = " ⤭ "
                
        self.rootWindow = tkinter.Tk()
        self.rootWindow.title("Talos Manual Interface")
        
        self.pressed_keys = {} # keeps track of keys which are pressed down
        self.move_delay_ms = 300 # time inbetween each directional command being sent while directional button is depressed
        
        # setting up manual vs automatic control toggle
        
        self.manual_mode = True  # True for manual, False for computer vision
        
        self.mode_label = tkinter.Label(self.rootWindow, text = "Mode: Manual", font = ("Cascadia Code", 12))
        self.mode_label.grid(row = 2, column = 4)
           
        self.toggle_button = tkinter.Button(self.rootWindow, text = self.switch, font = ("Cascadia Code", 16, "bold"), command = self.toggle_command_mode)
        self.toggle_button.grid(row = 2, column = 5, padx = 10)
        
        # setting up home button
        
        self.home_button = tkinter.Button(self.rootWindow, text = self.home, font = ("Cascadia Code", 16), command = self.move_home)
        self.home_button.grid(row = 3, column = 4)
        
        # setting up directional buttons
        
        self.up_button = tkinter.Button(self.rootWindow, text = self.up_arrow, height = 2, width = 10, font = ("Cascadia Code", 16, "bold"))
        self.up_button.grid(row = 1, column = 1, padx = 10, pady = 10)
        
        self.bind_button(self.up_button, Direction.UP)

        self.down_button = tkinter.Button(self.rootWindow, text = self.down_arrow, height = 2, width = 10, font = ("Cascadia Code", 16, "bold"))
        self.down_button.grid(row = 3, column = 1, padx = 10, pady = 10)

        self.bind_button(self.down_button, Direction.DOWN)

        self.left_button = tkinter.Button(self.rootWindow, text = self.left_arrow, height = 2, width = 10, font = ("Cascadia Code", 16, "bold"))
        self.left_button.grid(row = 2, column = 0, padx = 10, pady = 10)
        
        self.bind_button(self.left_button, Direction.LEFT)

        self.right_button = tkinter.Button(self.rootWindow, text = self.right_arrow, height = 2, width = 10, font = ("Cascadia Code", 16, "bold"))
        self.right_button.grid(row = 2, column = 2, padx = 10, pady = 10)
        
        self.bind_button(self.right_button, Direction.RIGHT)
        
        self.setup_keyboard_controls()

        self.last_key_presses = {}
        
        
    def setup_keyboard_controls(self):
        """ Does the tedious work of binding the keyboard arrow keys to the button controls.
        """
        self.rootWindow.bind("<KeyPress-Up>", lambda event: self.start_move(Direction.UP))
        self.rootWindow.bind("<KeyRelease-Up>", lambda event: self.stop_move(Direction.UP))
        
        self.rootWindow.bind("<KeyPress-Down>", lambda event: self.start_move(Direction.DOWN))
        self.rootWindow.bind("<KeyRelease-Down>", lambda event: self.stop_move(Direction.DOWN))
        
        self.rootWindow.bind("<KeyPress-Left>", lambda event: self.start_move(Direction.LEFT))
        self.rootWindow.bind("<KeyRelease-Left>", lambda event: self.stop_move(Direction.LEFT))
        
        self.rootWindow.bind("<KeyPress-Right>", lambda event: self.start_move(Direction.RIGHT))
        self.rootWindow.bind("<KeyRelease-Right>", lambda event: self.stop_move(Direction.RIGHT))
        
        
    def bind_button(self, button, direction):
        """ Shortens the constructor by binding button up/down presses.

        Args:
            button (tkinter.Button): button to bind with press and release functions
            direction (string): global variables for directional commands are provided at the top of this file
        """
        
        button.bind("<ButtonPress>", lambda event: self.start_move(direction))
        button.bind("<ButtonRelease>", lambda event: self.stop_move(direction))
    
    def start_move(self, direction):
        """ Moves the robotic arm a static number of degrees per second.

        Args:
            direction (string): global variables for directional commands are provided at the top of this file 
        """
        if self.manual_mode:

            self.last_key_presses[int(direction)] = time.time()

            if direction not in self.pressed_keys:
                
                self.pressed_keys[direction] = True
                self.keep_moving(direction)
                
                self.change_button_state(direction, "sunken")
                   
    def stop_move(self, direction):
        """ Stops a movement going the current direction.

        Args:
            direction (string): global variables for directional commands are provided at the top of this file 
        """
        if self.manual_mode:
            if direction in self.pressed_keys:
                if int(direction) in self.last_key_presses:
                    last_pressed_time = self.last_key_presses[int(direction)]

                    # Fix for operating systems that spam KEYDOWN KEYUP when a key is
                    # held down:

                    # I know this is jank but this is the best way I could figure out...
                    # Time.sleep stops the whole function, so new key presses will not
                    # be heard until after the sleep. So, create a new thread which is
                    # async to wait for a new key press
                    def stop_func():
                        # Wait a fraction of a second
                        time.sleep(0.1)
                        # Get the last time the key was pressed again
                        new_last_pressed_time = self.last_key_presses[int(direction)]
                       
                        # Check if the key has been pressed or if the times are the same
                        if new_last_pressed_time == last_pressed_time:
                            self.pressed_keys.pop(direction)
                            self.change_button_state(direction, "raised")

                    # Start the thread
                    thread = Thread(target=stop_func)
                    thread.start()
                else:
                    self.pressed_keys.pop(direction)
                    self.change_button_state(direction, "raised")
    
    
    def change_button_state(self, direction, depression):
        """ Changes button state to sunken or raised based on input depression argument.

        Args:
            direction (enum): the directional button to change.
            depression (string): "raised" or "sunken", the depression state to change to.
        """
        
        match direction:
            case Direction.UP:
                self.up_button.config(relief = depression)
            case Direction.DOWN:
                self.down_button.config(relief = depression)
            case Direction.LEFT:
                self.left_button.config(relief = depression)
            case Direction.RIGHT:
                self.right_button.config(relief = depression)

        # Send a continuous polar pan STOP if no key is pressed
        if len(self.pressed_keys) == 0:
            Publisher.polar_pan_continuous_stop()
            print("Stopping")
    
    def keep_moving(self, direction):
        """ Continuously allows moving to continue as controls are pressed and stops them once released by recursively calling this function while
            the associated directional is being pressed.

        Args:
            direction (_type_): global variables for directional commands are provided at the top of this file
        """
        if direction in self.pressed_keys:
            
            print("Moving", end = " ")
            moving_azimuth = 0
            moving_altitude = 0
            
            # moves toward input direction by delta 10 (degrees)
            match direction:
                case Direction.UP:
                    moving_altitude = 1
                    print("up")
                case Direction.DOWN:
                    moving_altitude = -1
                    print("down")
                case Direction.LEFT:
                    moving_azimuth = 1
                    print("left")
                case Direction.RIGHT:
                    moving_azimuth = -1
                    print("right")

            Publisher.polar_pan_continuous_start(
                moving_azimuth=moving_azimuth,
                moving_altitude=moving_altitude
            )
            
            self.rootWindow.after(self.move_delay_ms, lambda: self.keep_moving(direction)) # lambda used as function reference to execute when required
        
        
    def move_home(self):
        """ Moves the robotic arm from its current location to its home position
        """
        print("Moving home")
        Publisher.home(1000) # sends a command to move to home via the publisher
    
    
    def launch_user_interface(self):
        """ Launches user interface on demand.
        """
        self.rootWindow.mainloop()
    
    
    def toggle_command_mode(self):
        """ Toggles command mode between manual mode and automatic mode.
            Disables all other controls when in automatic mode.
        """
        self.manual_mode = not self.manual_mode
        
        if self.manual_mode:
            self.mode_label.config(text = "Mode: Manual")
            
            self.up_button.config(state = "normal")
            self.down_button.config(state = "normal")
            self.left_button.config(state = "normal")
            self.right_button.config(state = "normal")
            
            self.home_button.config(state = "normal")
            
            self.pressed_keys = {}
            
        else:
            self.mode_label.config(text = "Mode: Automatic")
            
            self.up_button.config(state = "disabled")
            self.down_button.config(state = "disabled")
            self.left_button.config(state = "disabled")
            self.right_button.config(state = "disabled")
            
            self.home_button.config(state = "disabled")
            
            self.pressed_keys = {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
