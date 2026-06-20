## LEGO Robotics with AI: Building Smart Robots with Pybricks and LEGO BOOST

🤖 This project is a LEGO robotics system built mainly with Pybricks running
MicroPython on the LEGO hub, combined with a Python-based host application that
connects over Bluetooth and controls the robot in real time.

🔧 The robot itself is based on a LEGO BOOST-style setup where we use two main
motors for movement, a DriveBase system for coordinated motion, and additional
ports including interface ports and an external motor for extended functionality.
We also use a light/color sensor for detecting inputs and the hub lights to
visually indicate states and feedback during execution.

⚙️ Instead of relying only on fixed programs, the robot starts with configurable
parameters like speed, turning rates, and motor behavior. These parameters
control how the DriveBase moves the robot and how the additional motor and
ports behave during execution.

📡 This project also demonstrates real-time bidirectional communication between the host and the robot. The host sends commands, parameters, and generated code to the hub, while the hub sends back sensor readings, execution status, and parameter updates. This continuous data exchange ensures the system stays synchronized and responsive during runtime.

🧠 On top of this hardware setup, the project adds an AI layer. A user can type
natural language prompts, and an OpenAI model interprets them and converts them
into structured robot parameters. These updated values are then used to
regenerate the MicroPython code and deploy it directly to the hub, allowing the
robot to change behavior dynamically without manually rewriting code.

📦 In the case of Pybricks, unlike LEGO BOOST, we do not need to keep a tablet or
computer connected for the robot to run. Once the program is deployed, it is
stored directly on the hub and can execute autonomously anywhere, making the
robot fully portable and independent.

🚀 In short, it is a MicroPython-based LEGO robotics project inspired by LEGO
BOOST hardware using two motors, a light/color sensor, hub LEDs, and additional
interface ports, combined with Pybricks and a Python host system, extended with
AI so the robot can be controlled and reprogrammed using simple text prompts.

### Links & Resources

<small>

- [LEGO BOOST](https://www.lego.com/en-us/themes/boost/videos)
- [LEGO SPIKE](https://spike.legoeducation.com/)
- [Pybricks](https://pybricks.com/)
- [Pybricks Code](https://code.pybricks.com/)

</small>

## Clone and Run

```bash
# Clone the repository
git clone https://github.com/Ashot72/lego-robotics-ai-with-pybricks
cd lego-robotics-ai-with-pybricks

# First-time setup
setup.bat

# OpenAI API key — copy .env.example to .env, then set:
# OPENAI_API_KEY=sk-your-key-here
# Get a key: https://platform.openai.com/api-keys
copy .env.example .env

# Start the app
host.bat
```

## Debugging in VS Code

Install Microsoft's [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) extension.

Open the Run view (View → Run or Ctrl+Shift+D) and choose **Debug Host**.

## Video

[Watch on YouTube](https://youtu.be/Mez0NQzGOWs)
