import pygame
import pandas as pd
import datetime
import re
import os
from openai import OpenAI
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('<path>')
pygame.mixer.music.play(-1)  # The '-1' makes the music loop indefinitely

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Project XYZ")
clock = pygame.time.Clock()

# Game States
STATE_OPENING = "opening"
STATE_MAIN_GAME = "main_game"
STATE_ANALYTICS = "analytics"

# Start with the opening state
current_state = STATE_OPENING

# Variables
images = "<path>"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pattern = r'\b(night|dark|tonight|nightime|night time)\b'
pattern_2 = r'\b(day|daytime|light)\b'
pattern_3 = r'\b(meditate|meditating|meditation)\b'
pattern_4 = r'\b(trailblazer|trail blazer)\b'
time_of_day = "day"

# Load background images
opening_screen_image = pygame.image.load(images + 'opening-background.png')
background_image = pygame.image.load(images + 'background-1.png')
background_image_night = pygame.image.load(images + 'background-1-ng.png')

def show_opening_screen():
    global current_state
    screen.blit(opening_screen_image, (0, 0))  # or use an opening screen image
    # Display opening screen content (title, instructions, etc.)
    # ...

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            current_state = STATE_MAIN_GAME
    return True

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
character_ani = [pygame.image.load(images + f'giphy-meditation-{i}.png') for i in range(1, 8)]
character_height = 100
start_x = screen_width // 2  # Center horizontally
start_y = screen_height // 2 - character_height // 2 + 100  # Position near bottom
character_rect = character_ani[0].get_rect(center=(start_x, start_y))

# Frame and animation settings
frame = 0  # Initialize frame index for character animation
frame_update_time = 100  # Time in milliseconds to update frame
last_update = pygame.time.get_ticks()

prepend = "Your name is <Name> please respond in a professional tone: "

# Function to call ChatGPT
def chat_with_gpt(message, max_chars=1000):
    try:
        print(prepend)
        client = OpenAI(api_key='<api-key>')
        response = client.completions.create(
            model="text-davinci-003",
            prompt= prepend + message + ". Try to limit text to 150 characters max.",
            max_tokens=60)
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error in GPT-3 request: {e}")
        return "Sorry, I couldn't process that message."

# Prepend Variables:
def get_prepend_text(input_text):
    if re.search(pattern, input_text, re.IGNORECASE):
        return "Acknowledge that the user is speaking about night: "
    elif re.search(pattern_2, input_text, re.IGNORECASE):
        return "Acknowledge that the user is speaking about day: " 
    elif re.search(pattern_3, input_text, re.IGNORECASE):
        return "Acknowledge that meditation is beneficial: "
    elif re.search(pattern_4, input_text, re.IGNORECASE):
        return "Talk about being a Saleforce Trailblazer: "
    else:
        return "Please respond in a professional tone and take the last message into context: "

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
chat_text = f"<name>: {gpt_response}"

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
    if current_state == STATE_OPENING:
        running = show_opening_screen()
        pygame.display.flip()
    elif current_state == STATE_MAIN_GAME:
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
                    prepend = get_prepend_text(input_text)
                    gpt_response = chat_with_gpt(input_text)
                    chat_text = f"<name>: {gpt_response}"
                    chat_text_display_length = 0
                    conversation_df.loc[len(conversation_df)] = ['User',"f06b22441da10adf9d3bde78f8c8c838c64de9d3095ffc8513d25dbddcb8e47a", input_text]
                    conversation_df.loc[len(conversation_df)] = ['GPT',"", gpt_response]
                    input_text = ''
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    prepend = get_prepend_text(input_text)
                    gpt_response = chat_with_gpt(input_text)
                    chat_text = f"<name>: {gpt_response}"
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

####
path = "<file path>"

# Ensure you have the stopwords dataset downloaded
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

# Function to clean text
def clean_text(text):
    if not isinstance(text, str):
        return []
    tokens = nltk.word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha() and word not in stop_words]
    return tokens

# Combine all conversation files into one DataFrame
def combine_files():
    all_texts = []
    for filename in os.listdir(path):
        if filename.startswith('conversation') and filename.endswith('.csv'):  # Assuming CSV format
            df = pd.read_csv(path+filename)
            # Filter rows where 'speaker' is 'user' and append 'message' column to list
            all_texts.extend(df[df['Speaker'] == 'User']['Message'].tolist())
    return pd.DataFrame({'Message': all_texts})

# Generate n-grams
def generate_ngrams(df, n):
    all_ngrams = []
    for text in df['Message']:
        tokens = clean_text(text)
        all_ngrams.extend(ngrams(tokens, n))
    return all_ngrams

# Create a word cloud
def create_wordcloud(ngrams_list):
    ngrams_text = ' '.join(['_'.join(ng) for ng in ngrams_list])
    wordcloud = WordCloud(width=800, height=600, 
                          background_color='black', 
                          stopwords=set(stopwords.words('english')),
                          min_font_size=10).generate(ngrams_text)

    # Plotting the WordCloud                    
    plt.figure(figsize = (8, 6), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 1) 
    plt.show()

# Main execution
df = combine_files()
ngrams_list = generate_ngrams(df, 1)  # Change 2 to another number for different n-grams
create_wordcloud(ngrams_list)
####
