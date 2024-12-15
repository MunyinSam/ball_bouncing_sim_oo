# Bouncing Laser and Ball Tower Defence

**Inspired by "The Tower" by Munyin Sam (6710545962)**

**UML Diagram: https://www.figma.com/board/50PcfbOI5hI1ZHMqEyYTb4/OOP-Munyin-Sam?node-id=0-1&t=oxx2EmqE9eB1Q75G-1**
**Youtube: https://www.youtube.com/@munyinsam**
---

## 1. **Project Description**

### **Gameplay:**
*Bouncing Laser and Ball Tower Defence* is a survival game where you control a polygon defending against waves of balls. Armed with a bouncing laser, your goal is to clear waves, collect power-ups, and avoid getting hit. With limited health, every move counts.

- **Objective:** Survive waves of incoming balls.
- **Weapon:** A laser that you can shoot by left-clicking.
- **Twist:** The laser bounces, allowing you to hit balls from different angles.
- **Health:** You have 3 health points. If you get hit 3 times, it's game over.
- **Upgrades:** You can improve your stats through the upgrade menu or by shooting special buff balls that appear.

---

## 2. **How to Install and Run the Project**

1. **Download the Python file**.
2. **Run the `main.py` file** to start the game.

---

## 3. **Usage**

### **Menu Interaction:**
- Use specific keys to navigate through the menu. (P & Q)

### **Shooting the Laser:**
- **Left-click** anywhere on the screen to fire the laser in the direction of your mouse pointer.
- The laser **bounces off walls** and hits balls. When it hits a ball, it either **destroys** it or **reduces its health**.
- The laser has a **cooldown**, so you can only shoot after a short delay.

### **Upgrading:**
- Left-click items in the **shop menu** to purchase them and gain **buffs**.

---

## 4. **Project Design and Implementation**

### **UML Class Diagram**

The project is built around four main classes that work together to make the game function smoothly:

1. **BouncingSimulator**  
   This class is the heart of the game. It controls the main game flow, including spawning the balls and the player's paddle, updating the user interface, and managing the shop window. It coordinates with the `Ball`, `Paddle`, and `my_event` classes to ensure everything works together seamlessly.

2. **Ball**  
   The `Ball` class handles the behavior of the balls in the game. It takes care of their movement, bouncing, and collisions with the walls, paddle, and lasers. Each ball has its own attributes like position, velocity, size, and health, which are managed by this class.

3. **Paddle**  
   The `Paddle` class is where the player controls the action. It represents the polygon in the center of the screen, and it's responsible for the player's movement, laser shooting, and interaction with the balls. The paddle also handles collisions and bounces with the balls.

4. **my_event**  
   The `my_event` class is in charge of managing all the events in the game. It uses a priority queue to handle things like ball movements and laser shots in the right order. This ensures the game keeps running smoothly and all actions happen at the correct times.

### **How the Classes Work Together**

- **BouncingSimulator** is the main controller. It creates the player paddle and the balls, and keeps track of all the events happening in the game, using the **Ball** and **Paddle** classes to check for interactions like collisions. It also interacts with the **my_event** class to manage the game’s event sequence.
  
- The **Ball** class controls how balls move and bounce around the screen. It interacts with both the **Paddle** (to bounce off) and the **my_event** class (to manage events like collisions).
  
- The **Paddle** class is what the player controls, allowing them to move and shoot lasers. It checks for collisions with the balls (managed by the **Ball** class) and also communicates with the **my_event** class to handle the timing of events.
  
### **How the Code Was Modified and Extended**

- Added the laser mechanics to the **BouncingSimulator** class, allowing the player to shoot lasers and make them bounce off balls and destroy balls. Also made the UI for tracking the level, coins, score and the menu. Then applied the laser bouncing mechanics.
- In the **Ball** class, Nothing have changed much, I've just added some attributes and added a speed cap for the ball.
- A shop system was created in the **BouncingSimulator** class using tkinter because I can't find a way to open 2 window at once. Players can now shoot buff balls to give them upgrades or directly buy the buffs out of the shop.
- A csv file is also added to keep track of the player history. (For potential updates)

### **Testing and Known Issues**

We’ve tested the game to make sure it works as expected. Here are the main things we’ve verified:

- Balls bounces with other balls.
- Lasers bounce as they should and can destroy or damage the balls.
- The upgrade system works in the shop, and buffs are applied correctly.
- The UI display are correctly updated in real-time.

There are a couple of small issues:

- **Collision Detection**: Sometimes, due to floating-point precision, balls might overlap or not bounce off surfaces as expected. (It might even freeze the screen you'll need to restart the application because the event can't handle the traffic)
- **Laser Cooldown**: Occasionally, if the player clicks too quickly, the laser cooldown doesn’t trigger properly.

## 5. **Rate your project sophistication level**

I rate my simulation 85. It's hard to add many collisions in my game design where all the balls are heading to the same place so I've implemented it on the laser instead.

## Potential Improvements

One way the code could be improved is by separating the **Laser** and **Shop** into their own classes. This would make the code more modular and easier to maintain.

However, this poses a challenge because the **Laser**'s speed is an attribute that the **Shop** directly modifies when you buy an upgrade. Keeping these two systems in the same class simplifies this interaction, as the **Shop** can easily increment the **Laser's** speed without additional coordination.

If the **Laser** and **Shop** were split into separate classes, it would require more complex communication between them, potentially leading to issues with maintaining synchronization. 

While separating these functionalities would result in cleaner code, the tight coupling between the **Laser** and **Shop** through the speed attribute makes it more practical to keep them together for now. This is due to my inexperience I apologize.

