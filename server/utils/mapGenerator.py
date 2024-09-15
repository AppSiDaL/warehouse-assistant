from PIL import Image, ImageDraw

def generate_map_image(corridor_color, platform_position):
    # Crear una imagen de ejemplo
    img = Image.new('RGB', (1280, 847), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Dibujar el pasillo basado en el color
    corridor_color_rgb = (255, 255, 255)  # Default to white
    if corridor_color == "red":
        corridor_color_rgb = (255, 0, 0)
    elif corridor_color == "green":
        corridor_color_rgb = (0, 255, 0)
    elif corridor_color == "blue":
        corridor_color_rgb = (0, 0, 255)
    
    d.rectangle([0, 0, 120, 847], fill=corridor_color_rgb)
    
    # Dibujar la plataforma basada en la posición relativa
    platform_x, platform_y = 640, 423  # Default to center
    if platform_position == "left":
        platform_x = 320
    elif platform_position == "right":
        platform_x = 960
    elif platform_position == "front":
        platform_y = 211
    elif platform_position == "back":
        platform_y = 635
    
    d.ellipse((platform_x - 10, platform_y - 10, platform_x + 10, platform_y + 10), fill=(255, 255, 0))
    
    return img

def modify_map_image(img, corridor_color, platform_position):
    d = ImageDraw.Draw(img)
    
    # Dibujar el pasillo basado en el color
    corridor_color_rgb = (255, 255, 255)  # Default to white
    if corridor_color == "red":
        corridor_color_rgb = (255, 0, 0)
    elif corridor_color == "green":
        corridor_color_rgb = (0, 255, 0)
    elif corridor_color == "blue":
        corridor_color_rgb = (0, 0, 255)
    elif corridor_color == "black":
        corridor_color_rgb = (0, 0, 0)
    elif corridor_color == "white":
        corridor_color_rgb = (255, 255, 255)
    
    d.rectangle([0, 0, 1280, 847], fill=corridor_color_rgb)
    
    # Dibujar la plataforma basada en la posición relativa
    platform_x, platform_y = 640, 423  # Default to center
    if platform_position == "left":
        platform_x = 320
    elif platform_position == "right":
        platform_x = 960
    elif platform_position == "front":
        platform_y = 211
    elif platform_position == "back":
        platform_y = 635
    
    d.ellipse((platform_x - 10, platform_y - 10, platform_x + 10, platform_y + 10), fill=(255, 255, 0))
    
    return img