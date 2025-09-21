
#contains helper function and global constants needed everywhere else

def transparentColour(colour, alpha):
    return (colour[0], colour[1], colour[2], alpha)

colours = {
    "black":          ( 0 , 0 , 0 ),
    "white":          (255,255,255),
    "grey":           (170,170,170),
    "red":            (255, 0 , 0 ),
    "green":          ( 0 ,255, 0 ),
    "blue":           ( 0 , 0 ,255),
    "dark red":       (122, 0 , 0 ),
    "dark green":     ( 0 , 74, 0 ),
    "wood":           (250,217,145),
    "orange":         (252,139, 73),
    "purple":         (102, 66,245),
    "yellow":         (255,200, 0 ),
    "wind":           (255,231,209),
    "flame":          (255, 90, 0 ),
    "electric":       (249,170, 0 ),
    "steel":          (224,229,229),
    "dark earth":     ( 46, 26, 0 ),
    "earth":          ( 92, 55, 0 ),
    "ice":            (181,255,254),
    "icePlatform":    (209,255,254)
}

FPS = 60