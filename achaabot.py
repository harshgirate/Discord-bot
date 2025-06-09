import os
import discord
import google.generativeai as genai
from discord.ext import commands
from langdetect import detect
from dotenv import load_dotenv
import logging
import random

# Load environment variables from .env file
load_dotenv()

# Get Discord token
discord_token = os.getenv('DISCORD_TOKEN')

# Check if Discord token is available
if not discord_token:
    raise ValueError("Discord token not found.")

# Get Generative AI API key
generativeai_api_key = os.getenv("GENERATIVEAI_API_KEY")

# Check if Generative AI API key is available
if not generativeai_api_key:
    raise ValueError("Generative AI API key not found.")

# Configure Generative AI with API key
genai.configure(api_key=generativeai_api_key)

# Initialize bot
bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

# Initialize Generative AI models
models = {
    'gemini-pro': genai.GenerativeModel(
        'gemini-pro',
        safety_settings=[
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    ),
    
}

# Dictionary to store user preferences
user_preferences = {}

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.ERROR)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}!")

# Event: Message received
@bot.event
async def on_message(message):
    # Process other commands
    await bot.process_commands(message)

# Add error handling for CommandInvokeError
@bot.event
async def on_command_error(ctx, error):
    error_messages = {
        commands.CommandNotFound: "Sorry, that command doesn't exist. Use >help to see available commands.",
        commands.MissingRequiredArgument: "Oops! You're missing some required arguments. Please check the command syntax and try again.",
        commands.CommandInvokeError: "Oops! Something went wrong while executing the command. Please try again later.",
    }
    error_message = error_messages.get(type(error), "Oops! Something went wrong. Please try again later.")
    await ctx.send(error_message)
    logging.error(f"An error occurred: {error}")

# Command: ask
@bot.command(name="ask")
async def ask_ai(ctx: commands.Context, *, prompt: str):
    model_name = user_preferences.get(ctx.author.id, {}).get('model', 'gemini-pro')
    model = models.get(model_name)
    if model:
        response = model.generate_content(prompt)
        await ctx.reply(response.text)
    else:
        await ctx.reply("Sorry, the specified AI model is not available.")

# Command: poll
@bot.command(name="poll")
async def create_poll(ctx, question: str, *options: str):
    if len(options) < 2 or len(options) > 10:
        await ctx.send("Please provide at least 2 and at most 10 options.")
        return
    embed = discord.Embed(title=question, color=discord.Color.blue())
    for idx, option in enumerate(options):
        embed.add_field(name=f"Option {idx+1}", value=option, inline=False)
    message = await ctx.send(embed=embed)
    for idx in range(len(options)):
        await message.add_reaction(chr(0x1f1e6 + idx))

# Command: report
@bot.command(name="report")
async def report_content(ctx, content_id: int, reason: str):
    # Implement moderation system here
    # You can log the report, notify moderators, or take appropriate action
    await ctx.send(f"Content {content_id} reported for '{reason}'. Moderators will review it soon.")

# Command: set_preference
@bot.command(name="set_preference")
async def set_preference(ctx, preference_type: str, value: str):
    user_id = ctx.author.id
    user_preferences[user_id] = user_preferences.get(user_id, {})
    user_preferences[user_id][preference_type] = value
    await ctx.send(f"{preference_type.capitalize()} preference set to {value}.")

# Command: trivia
@bot.command(name="trivia")
async def trivia(ctx):
    # Define a list of trivia questions and answers
    trivia_questions = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
        {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    ]

    # Shuffle the trivia questions
    random.shuffle(trivia_questions)

    # Initialize score
    score = 0

    # Iterate through each trivia question
    for question_data in trivia_questions:
        # Send the question to the user
        await ctx.send(question_data["question"])

        # Wait for the user's answer
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        try:
            user_answer = await bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! Game over.")
            return

        # Check if the user's answer is correct
        if user_answer.content.lower() == question_data["answer"].lower():
            await ctx.send("Correct!")
            score += 1
        else:
            await ctx.send(f"Wrong! The correct answer is: {question_data['answer']}")

    # Display the final score
    await ctx.send(f"Your final score is: {score}/{len(trivia_questions)}")

    # Store user's preferred language
    user_id = ctx.author.id
    user_preferences[user_id] = user_preferences.get(user_id, {})
    user_preferences[user_id]['language'] = language
    await ctx.send(f"Language preference set to {language}")
    
# Run the bot
bot.run(discord_token)