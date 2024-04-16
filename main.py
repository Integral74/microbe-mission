import discord
import os
import random
import json
from dotenv import load_dotenv
from discord import app_commands
from sentence_transformers import SentenceTransformer, util
import pickle

load_dotenv()
# test
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Ex: {question1: answer1, ...}
with open("questions.json", encoding="utf8") as f:
    questions = json.load(f)

# add images
agent_images = {
    "/Users/brycennelson/Desktop/images/agents/Rickettsia_rickettsii.jpg":"Rickettsia rickettsii"
}
parts_of_things = {
    "/Users/brycennelson/Desktop/images/parts/cart.webp":"cat"
}
other_things = {
    "/Users/brycennelson/Desktop/images/other/benzene.webp":"benzene"
}

def compare(text1, text2):
    return util.pytorch_cos_sim(model.encode(text1, convert_to_tensor=True),
                                model.encode(text2, convert_to_tensor=True)).item()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)

    if message.author == client.user:
        return

    # Hello Message
    if message.content.startswith('/hello'):
        await message.channel.send('Welcome to the MM bot!')
    if message.content.startswith('/help'):
        await message.channel.send('Please visit the following link to view the Mimi documentation: https://docs.google.com/document/d/14n9yHbBwBZW4RRpGSmKFnLyFMfxlq8w_nciCN0tWsRc/edit?usp=sharing')
    # Leaderboard
    # First item in tuple is total questions answered and second item in tuple is the answer streak
    if message.content.startswith("/leaderboard"):
        # Did .strip("@") because om doesn't like pings during school
        leaderboard_total_answers = dict(sorted(leaderboard.items(), key=lambda t: t[1][0], reverse=True))
        leaderboard_answer_streak = dict(sorted(leaderboard.items(), key=lambda t: t[1][1], reverse=True))

        leaderboard_total_answer_str = "*Total Answers* \n" + "".join(f"{user}: {leaderboard[user][0]} \n" for user in leaderboard_total_answers.keys())
        leaderboard_answer_streak_str = "*Answer Steaks:* \n" + "".join(f"{user}: {leaderboard[user][1]} \n" for user in leaderboard_answer_streak.keys())

        await message.channel.send("***Leaderboard:*** \n \n" + leaderboard_total_answer_str + "\n" + leaderboard_answer_streak_str)

    # Amoeba Message
    if message.content.startswith("/amoeba"):
        await message.channel.send('Amoeba is Amazing! Amoeba is amoebasome!')

    # Image Id
    if message.content.startswith('/imageid'):
        choice_for_imageid = message.content.split(" ")[1]
        rounds = int(message.content.split(" ")[2])
        accuracy=0
        for i in range(rounds):
            if choice_for_imageid == "agents":
                imageQuestion = random.choice(list(agent_images.keys()))
                imageAnswer = agent_images[imageQuestion]
            elif choice_for_imageid == "parts of things":
                imageQuestion = random.choice(list(parts_of_things.keys()))
                imageAnswer = parts_of_things[imageQuestion]
            elif choice_for_imageid == "other":
                imageQuestion = random.choice(list(other_things.keys()))
                imageAnswer = other_things[imageQuestion]

            await message.channel.send(file=discord.File(imageQuestion))

            answer_message = await client.wait_for("message", check=lambda m: m.author == message.author)

            if answer_message.content.lower() == imageAnswer.lower():
                await message.channel.send(f"{message.author.mention}, Great job! You got it correct! You said: {imageAnswer} and it is correct!")
                accuracy += 1
                # Leaderboard
                if message.author.mention in leaderboard:
                    leaderboard[message.author.mention][0] += 1
                    leaderboard[message.author.mention][1] += 1
                else:
                    leaderboard[message.author.mention] = [1, 1]
            else:
                await message.channel.send(f'{message.author.mention}, Too bad. You got it wrong. Please review the question. The expected answer was: {imageAnswer}.')

                # Leaderboard
                if message.author.mention in leaderboard:
                    leaderboard[message.author.mention][1] = 0
                else:
                    leaderboard[message.author.mention] = [0, 0]

            # Dumps leaderboard
            with open('leaderboard.json', 'w') as f:
                json.dump(leaderboard, f)
        await message.channel.send(f'Your accuracy was {accuracy/rounds * 100}%.')
    # Anki Questions
    if message.content.startswith('/anki'):
        question_agent = message.content.split(" ")[1]
        rounds = int(message.content.split(" ")[2])
        for i in range(rounds):
            question = random.choice(list(questions[question_agent].keys()))
            total_accuracy=0
            await message.channel.send(question)

            answer_message = await client.wait_for("message", check=lambda m: m.author == message.author)

            answer_message = answer_message.content

            answer = questions[question_agent][question]

            accuracy = compare(str(answer_message).lower(), str(answer).lower())
            total_accuracy += accuracy
            if str(answer_message).lower() == str(answer).lower():
                await message.channel.send(
                    f"{message.author.mention} \n `Great job! You got it correct!` \n `Accuracy:` {round(accuracy * 100, 2)}%. `Here's what is in the question bank.` \n `Correct Answer:` {answer}")

                # Leaderboard
                if message.author.mention in leaderboard:
                    leaderboard[message.author.mention][0] += 1
                    leaderboard[message.author.mention][1] += 1
                else:
                    leaderboard[message.author.mention] = [1, 1]

            else:
                if accuracy > 0.58:
                    await message.channel.send(
                        f"{message.author.mention} \n `Great job! You got it correct!` \n `Accuracy:` {round(accuracy * 100, 2)}%. `Here's what is in the question bank.` \n `Correct Answer:` {answer}")

                    # Leaderboard
                    if message.author.mention in leaderboard:
                        leaderboard[message.author.mention][0] += 1
                        leaderboard[message.author.mention][1] += 1
                    else:
                        leaderboard[message.author.mention] = [1, 1]

                else:
                    await message.channel.send(
                        f"{message.author.mention} \n `Too bad. You got it wrong. Please review the question.` \n `Accuracy:` {round(accuracy * 100, 2)}%. `Here's what is in the question bank.` \n `Correct Answer:` {answer}")

                    # Leaderboard
                    if message.author.mention in leaderboard:
                        leaderboard[message.author.mention][1] = 0
                    else:
                        leaderboard[message.author.mention] = [0, 0]
            
        overall_accuracy = (total_accuracy / rounds) * 100
        await message.channel.send(f"You just completed {rounds} rounds with an overall accuracy of {overall_accuracy}%")
        # Dumps leaderboard
        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard, f)

        flag_question = await client.wait_for("message", check=lambda m: m.author == message.author)

        if flag_question.content.startswith("/flag"):
            # Reason why the question was flagged
            flag_reason = flag_question.content.split("/flag")[1].strip(" ")
            with open("flag.txt", mode="a", encoding="utf-8") as f:
                f.write(f"Question: {question} --- Reason for flag: {flag_reason} \n")

            await message.channel.send(
                "Thanks for flagging this question! I will go back and review the question and its answer. Please DM me if you have any other questions regarding this issue.")


client.run(TOKEN)
