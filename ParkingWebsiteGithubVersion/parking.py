from PIL import Image, ImageDraw, ImageFont
import random

def draw_parking_spots(parking_spots, rows, cols, rect_width, rect_height):
    # Create an image with a white background
    img = Image.new('RGB', (rect_width * (cols+4), rect_height * rows), 'grey')
    Disabled = Image.open('static/handicap.png')
    Electric = Image.open('static/ev.png')
    pExit = Image.open('static/peopleExit.png')
    
    Disabled = Disabled.resize((30, 30))
    Electric = Electric.resize((30, 30))
    pExit = pExit.resize((60, 60))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("static/arial.ttf", 18)
    c_font = ImageFont.truetype("static/arial.ttf", 35)

    park_offset_x = rect_width*2

    skipped_row = 0
    prev_skipped = False

    # Loop through the rows and columns, drawing rectangles
    for row in range(rows):
        if row in [1, 4]:
            skipped_row += 1
            prev_skipped = True
            continue

        for col in range(cols):
            index = row * cols + col + 1 - (skipped_row * cols)
            print("Row:", row, "Index:", index)
            if index in [item[0] for item in parking_spots]:
                spot = [item for item in parking_spots if item[0] == index][0]
                spot_type = spot[2]
                color = [item[1] for item in parking_spots if item[0] == index][0]
                fill_color = 'green' if color else 'red'
                x1 = col * rect_width + park_offset_x
                y1 = row * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                draw.rectangle((x1, y1, x2, y2), fill=fill_color, outline ="white")
                # Add the text in the center of the rectangle
                x = x1 + rect_width / 2 - 4
                y = y1 + rect_height / 2
                draw.text((x-4  , y-4), str(index), fill='white', align='center', font=font)

                if prev_skipped:
                    if spot_type == 'Electric':
                        img.paste(Electric, (int(x-8), int(y-60)), mask=Electric)
                    elif spot_type == 'Disabled':
                        img.paste(Disabled, (int(x-8), int(y-60)), mask=Disabled)
                else:
                    if spot_type == 'Electric':
                        img.paste(Electric, (int(x-8), int(y+30)), mask=Electric)
                    elif spot_type == 'Disabled':
                        img.paste(Disabled, (int(x-8), int(y+30)), mask=Disabled)

        prev_skipped = False
        img.paste(pExit, (int(20), int(350)), mask=pExit)
        draw.text((1450  , 225), "Entrance", fill='white', align='center', font=c_font)
        draw.text((1450  , 710), "Exit", fill='white', align='center', font=c_font)

    return img

