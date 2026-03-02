from PIL import Image, ImageDraw
import os

# Create assets folder if it doesn't exist
os.makedirs("assets", exist_ok=True)

frames = []
for i in range(10):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a bouncing red ball
    y = 30 + abs(i - 4) * 4  # simple bounce math
    draw.ellipse((20, y, 44, y + 24), fill="red")
    
    frames.append(img)

# Save as animated GIF
frames[0].save(
    "assets/neko_idle.gif",
    save_all=True,
    append_images=frames[1:],
    duration=100,
    loop=0,
    transparency=0,
    disposal=2
)

print("Generated assets/neko_idle.gif")
