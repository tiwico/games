import pygame
import pandas as pd
import datetime
import re
import os
from openai import OpenAI

# Initialize Pygame
pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Lasagna Chat Game")
clock = pygame.time.Clock()

# Variables
images = "/"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pattern = r'\b(night|dark)\b'
pattern_2 = r'\b(day|light)\b'
time_of_day = "day"

# Load background images
background_image = pygame.image.load('background-1.png')
background_image_night = pygame.image.load('background-1-ng.png')

# Colors and font
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
LIGHT_GREY, LIGHT_PURPLE, DARK_PURPLE  = (211, 211, 211), (228, 188, 238), (89, 68, 85)
FONT = pygame.font.Font(None, 32)

# Input and ChatGPT response box setup
input_box = pygame.Rect(60, 550, 600, 40)
chat_box = pygame.Rect(10, 10, 780, 150)
input_text, chat_text = '', ''
active, cursor_visible = False, True
cursor_timer = 0
chat_text_display_length = 0
last_increment_time = 0
increment_interval = 25  # Time in milliseconds between each character increment

# Create a new surface with per-pixel alpha
input_box_surface = pygame.Surface(input_box.size, pygame.SRCALPHA)
semi_transparent_color = (*LIGHT_PURPLE, 60)
chat_box_surface = pygame.Surface(chat_box.size, pygame.SRCALPHA)
semi_transparent_grey = (*DARK_PURPLE, 125)

# DataFrame for conversation
conversation_df = pd.DataFrame(columns=['Speaker','User-id', 'Message'])

# Define the character and its starting position
character_ani = [pygame.image.load(f'giphy-meditation-{i}.png') for i in range(1, 8)]
character_height = 100
start_x = screen_width // 2  # Center horizontally
start_y = screen_height // 2 - character_height // 2 + 100  # Position near bottom
character_rect = character_ani[0].get_rect(center=(start_x, start_y))

# Frame and animation settings
frame = 0  # Initialize frame index for character animation
frame_update_time = 100  # Time in milliseconds to update frame
last_update = pygame.time.get_ticks()

# Function to call ChatGPT
def chat_with_gpt(message, max_chars=1000):
    if re.search(pattern, input_text, re.IGNORECASE):
        try:
            client = OpenAI(api_key='<API KEY>')
            response = client.completions.create(
                model="text-davinci-003",
                prompt="Acknowledge that the user is speaking about night: " + message + ". Try to limit text to 150 characters max.",
                max_tokens=60)
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in GPT-3 request: {e}")
            return "Sorry, I couldn't process that message."
    elif re.search(pattern_2, input_text, re.IGNORECASE):
        try:
            client = OpenAI(api_key='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')
            response = client.completions.create(
                model="text-davinci-003",
                prompt="Acknowledge that the user is speaking about day: " + message + ". Try to limit text to 150 characters max.",
                max_tokens=60)
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in GPT-3 request: {e}")
            return "Sorry, I couldn't process that message."
    else:
        try:
            client = OpenAI(api_key='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')
            response = client.completions.create(
                model="text-davinci-003",
                prompt="Your name is Lasagna please respond in a professional tone: " + message + ". Try to limit text to 150 characters max.",
                max_tokens=60)
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in GPT-3 request: {e}")
            return "Sorry, I couldn't process that message."

# Function to wrap text according to pixel width
def wrap_text(text, box_width):
    lines, words = [], text.split(' ')
    while words:
        line_words = []
        while words and FONT.size(' '.join(line_words + [words[0]]))[0] <= box_width:
            line_words.append(words.pop(0))
        lines.append(' '.join(line_words))
    return lines

# Initial message to GPT and get response
gpt_response = chat_with_gpt(input_text)
chat_text = f"Astro: {gpt_response}"

# Define the send button
send_button = pygame.Rect(input_box.right + 10, input_box.y, 80, 40)
send_button_text = 'Send'

# Function to draw the button with text
def draw_button(button, text, button_color):
    pygame.draw.rect(screen, button_color, button)
    text_surf = FONT.render(text, True, WHITE)
    screen.blit(text_surf, text_surf.get_rect(center=button.center))

# Main game loop
running = True
while running:
    # Get the current mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Background change based on chat content
    if re.search(pattern, chat_text, re.IGNORECASE):
        time_of_day = "night"
    if re.search(pattern_2, chat_text, re.IGNORECASE):
        time_of_day = "day"
    screen.blit(background_image_night if time_of_day == "night" else background_image, (0, 0))

    # Fill chat box with semi-transparent color
    chat_box_surface.fill(semi_transparent_grey)
    screen.blit(chat_box_surface, chat_box.topleft)

    # Increment display length of chat text based on timer
    if chat_text_display_length < len(chat_text):
        if pygame.time.get_ticks() - last_increment_time > increment_interval:
            chat_text_display_length += 1
            last_increment_time = pygame.time.get_ticks()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
            if send_button.collidepoint(event.pos):
                gpt_response = chat_with_gpt(input_text)
                chat_text = f"Astro: {gpt_response}"
                chat_text_display_length = 0
                conversation_df.loc[len(conversation_df)] = ['User',"f06b22441da10adf9d3bde78f8c8c838c64de9d3095ffc8513d25dbddcb8e47a", input_text]
                conversation_df.loc[len(conversation_df)] = ['GPT',"", gpt_response]
                input_text = ''
        elif event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_RETURN:
                gpt_response = chat_with_gpt(input_text)
                chat_text = f"Astro: {gpt_response}"
                chat_text_display_length = 0
                conversation_df.loc[len(conversation_df)] = ['User',"f06b22441da10adf9d3bde78f8c8c838c64de9d3095ffc8513d25dbddcb8e47a", input_text]
                conversation_df.loc[len(conversation_df)] = ['GPT',"", gpt_response]
                input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    # Cursor blink logic
    cursor_timer = (cursor_timer + 1) % 60
    cursor_visible = cursor_timer < 30

    # Reset y_offset for chat box
    y_offset = chat_box.y + 10

    # Render text for chat box with wrapping
    chat_lines = wrap_text(chat_text[:chat_text_display_length], chat_box.width - 10)
    for line in chat_lines:
        line_surface = FONT.render(line, True, WHITE)
        screen.blit(line_surface, (chat_box.x + 5, y_offset))
        y_offset += line_surface.get_height() + 5  # Increase y_offset for next line


    # Draw input box and chat box contents
    input_box_surface.fill(semi_transparent_color)
    screen.blit(input_box_surface, input_box.topleft)
    for y_offset, line in enumerate(wrap_text(input_text, input_box.width - 10), start=input_box.y + 5):
        screen.blit(FONT.render(line, True, WHITE), (input_box.x + 5, y_offset))
    pygame.draw.rect(screen, LIGHT_PURPLE, input_box, 2)
    """for y_offset, line in enumerate(wrap_text(chat_text, chat_box.width - 10), start=chat_box.y + 5):
        screen.blit(FONT.render(line, True, BLACK), (chat_box.x + 5, y_offset))"""
    pygame.draw.rect(screen, LIGHT_GREY, chat_box, 2)

    # Cursor drawing
    if active and cursor_visible:
        cursor_x, cursor_y = input_box.x + FONT.render(input_text, True, WHITE).get_width() + 10, input_box.y + 10
        pygame.draw.rect(screen, WHITE, (cursor_x, cursor_y, 2, FONT.get_height()))

    # Character animation
    if pygame.time.get_ticks() - last_update > frame_update_time:
        last_update = pygame.time.get_ticks()
        frame = (frame + 1) % len(character_ani)  # Cycle through frames
    screen.blit(character_ani[frame], character_rect)

    # Draw send button
    draw_button(send_button, send_button_text, LIGHT_PURPLE if send_button.collidepoint(mouse_pos) else BLACK)

    # Update display and cap frame rate
    pygame.display.flip()
    clock.tick(30)

# Export conversation to CSV
csv_file_path = os.path.expanduser(f'~/Downloads/conversation{timestamp}.csv')
try:
    conversation_df.to_csv(csv_file_path, index=False)
    print(f"Conversation exported successfully to {csv_file_path}")
except Exception as e:
    print(f"Error exporting conversation: {e}")
pygame.quit()
