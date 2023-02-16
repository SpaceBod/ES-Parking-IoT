from PIL import Image, ImageDraw, ImageFont
import random

def draw_parking_spots(parking_spots, rows, cols, rect_width, rect_height):
    # Create an image with a white background
    img = Image.new('RGB', (rect_width * (cols+4), rect_height * rows), 'grey')
    handicap = Image.open('img/handicap.png')
    electric = Image.open('img/ev.png')
    pExit = Image.open('img/peopleExit.png')
    
    handicap = handicap.resize((30, 30))
    electric = electric.resize((30, 30))
    pExit = pExit.resize((60, 60))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 18)
    c_font = ImageFont.truetype("arial.ttf", 35)

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
                    if spot_type == 'electric':
                        img.paste(electric, (int(x-8), int(y-60)), mask=electric)
                    elif spot_type == 'handicap':
                        img.paste(handicap, (int(x-8), int(y-60)), mask=handicap)
                else:
                    if spot_type == 'electric':
                        img.paste(electric, (int(x-8), int(y+30)), mask=electric)
                    elif spot_type == 'handicap':
                        img.paste(handicap, (int(x-8), int(y+30)), mask=handicap)

        prev_skipped = False
        img.paste(pExit, (int(20), int(350)), mask=pExit)
        draw.text((1450  , 225), "Entrance", fill='white', align='center', font=c_font)
        draw.text((1450  , 710), "Exit", fill='white', align='center', font=c_font)
    return img

# Example usage
parking_spots = [[i+1, random.choice([True, False]), random.choice(["normal", "electric", "handicap"])] for i in range(64)]
img = draw_parking_spots(parking_spots, 6, 16, 80, 160)
img.save("imgOut.jpg", format='JPEG', subsampling=0, quality=100)
