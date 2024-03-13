color_red = 91
color_green = 92
color_yellow = 93
def colorize_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"
