import sentry_sdk

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from dotenv import load_dotenv
from os import getenv
import logging

from bot.buttons import SaveLinkButton, DeleteSavedLinkButton
from bot.db import db
from bot.messages import MessageProcessor
from bot.models import Link, Artist, Genre, User, Chat, Album, Track, AlbumArtist, AlbumGenre, ArtistGenre, \
    TrackArtist, LastFMUsername, SavedLink
from bot.commands import CommandFactory
from bot.search import SearchInline

load_dotenv()

logging.basicConfig(
    # filename='musicbucket-bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)


def _setup_database():
    db.connect()
    db.create_tables(
        [User, Chat, Link, Artist, Album, Track, Genre, AlbumArtist, AlbumGenre, ArtistGenre, TrackArtist,
         LastFMUsername, SavedLink])


def _setup_sentry():
    public_key = getenv('SENTRY_PUBLIC_KEY', None)
    project_id = getenv('SENTRY_PROJECT_ID', None)

    if public_key and project_id:
        sentry_sdk.init(f"https://{public_key}@sentry.io/{project_id}")


def main():
    # Init app
    _setup_database()
    _setup_sentry()

    # Bot start
    updater = Updater(getenv('TOKEN'), use_context=True)

    # Register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(
        CommandHandler('music', CommandFactory.run_music_command, pass_args=True)
    )
    dispatcher.add_handler(
        CommandHandler('music_from_beginning', CommandFactory.run_music_from_beginning_command, pass_args=True)
    )
    dispatcher.add_handler(
        CommandHandler('mymusic', CommandFactory.run_my_music_command)
    )
    dispatcher.add_handler(
        CommandHandler('recommendations', CommandFactory.run_recommendations_command)
    )
    dispatcher.add_handler(
        CommandHandler('np', CommandFactory.run_now_playing_command)
    )
    dispatcher.add_handler(
        CommandHandler('lastfmset', CommandFactory.run_lastfmset_command, pass_args=True)
    )
    dispatcher.add_handler(
        CommandHandler('savedlinks', CommandFactory.run_saved_links_command)
    )
    dispatcher.add_handler(
        CommandHandler('deletesavedlinks', CommandFactory.run_delete_saved_links_command)
    )
    dispatcher.add_handler(
        CommandHandler('stats', CommandFactory.run_stats_command)
    )
    dispatcher.add_handler(
        InlineQueryHandler(SearchInline)
    )
    dispatcher.add_handler(
        CallbackQueryHandler(SaveLinkButton.handle, pattern=f'{SaveLinkButton.CALLBACK_NAME}')
    )
    dispatcher.add_handler(
        CallbackQueryHandler(DeleteSavedLinkButton.handle, pattern=f'{DeleteSavedLinkButton.CALLBACK_NAME}')
    )

    # Non command handlers
    dispatcher.add_handler(MessageHandler(
        Filters.text, MessageProcessor.process_message))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
