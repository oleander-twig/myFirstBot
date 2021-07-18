from telebot import TeleBot
from telebot import types
from kinopoisk.movie import Movie
TOKEN = ""
bot = TeleBot(TOKEN)
movieName = ''
references = dict()

@bot.message_handler(commands=['start', 'help'])
def send(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне название фильма.")
    bot.register_next_step_handler(message, logic)

@bot.message_handler(content_types=['text'])
def logic(message):
    movie = message.text
    movieNameList = Movie.objects.search(movie)

    if len(movieNameList) < 1:
        bot.send_message(message.chat.id, 'Фильм не найден.')
        return
    global movieName
    movieName = movieNameList[0].title

    bot.send_message(message.chat.id, 'Ты искал фильм "' + movieName + '"?')
    bot.register_next_step_handler(message, receiveReply)


def receiveReply(message):
    if message.text == 'Нет':
        bot.send_message(message.chat.id, 'Отправь название фильма еще раз :)')
        bot.register_next_step_handler(message, logic)
        return
    elif message.text == 'Да':
        markup = types.ReplyKeyboardMarkup()
        markup.row('Оставить отзыв')
        markup.row('Посмотреть отзывы')
        bot.send_message(message.chat.id, 'Ты можешь написать свой отзыв на фильм или посмотреть рецензии других пользователей. Что выберешь?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, receiveReply)
    elif message.text == 'Оставить отзыв':
        bot.send_message(message.chat.id, 'Присылай отзыв')
        bot.register_next_step_handler(message, receiveReference)
    elif message.text == 'Посмотреть отзывы':
        sendReference(message)

def receiveReference(message):
    types.ReplyKeyboardRemove()
    if movieName not in references.keys():
        references[movieName] = list()
    references[movieName].append(message.text)
    bot.register_next_step_handler(message, loop)
    markup = types.ReplyKeyboardMarkup()
    markup.row('Искать фильм')
    bot.send_message(message.chat.id, 'Отзыв сохранен!\nНажми, если хочешь снова поискать фильм!', reply_markup=markup)
    return


def sendReference(message):
    types.ReplyKeyboardRemove()
    if movieName not in references.keys():
        bot.send_message(message.chat.id, 'На этот фильм пока нет рецензий :(')
        return

    bot.send_message(message.chat.id, 'Рецензии пользователей:\n' + '\n\n'.join(references[movieName]))

    markup = types.ReplyKeyboardMarkup()
    markup.row('Искать фильм')
    bot.send_message(message.chat.id, 'Нажми, если хочешь снова поискать фильм!', reply_markup=markup)
    bot.register_next_step_handler(message, loop)

def loop(message):
    types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Отправь название фильма!')
    bot.register_next_step_handler(message, logic)



bot.polling()
