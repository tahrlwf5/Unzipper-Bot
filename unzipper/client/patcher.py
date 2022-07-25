# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  #
# See the GNU General Public License for more details.                  #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>   #
# ===================================================================== #

import logging
from os import path, remove
from .pyro_client import UnzipperBot
from unzipper.database.thumbnail import get_thumbnail
from unzipper.helpers_nexa.utils import run_shell_cmds
from unzipper.database.users import add_user, is_user_in_db, is_user_in_bdb
from config import Config


class PatchMethods:
    def __init__(self) -> None:
        super().__init__()

    async def check_user(self: UnzipperBot, message):
        """
        Checks database checks of new users
        """
        # Checking if user is banned
        is_banned = await is_user_in_bdb(int(message.from_user.id))
        if is_banned:
            await message.reply("**آسف أنت محظور!** \n\nأبلغ عن هذا الى مسؤول @ta_ja199 إذا كنت تعتقد أن هذا خطأ")
            raise UserIsBanned
        # Chacking if user already in db
        is_in_db = await is_user_in_db(int(message.from_user.id))
        if not is_in_db:
            try:
                await add_user(int(message.from_user.id))
                await self.send_message(
                    chat_id=Config.LOGS_CHANNEL,
                    text=f"**#مستخدم_جديد** 🎙 \n\n**بروفايل  المستخدم:** `{message.from_user.mention}` \n**اي دي مستخدم** `{message.from_user.id}` \n**رابط البروفايل:** [Click here](tg://user?id={message.from_user.id})",
                    disable_web_page_preview=True
                )
            except Exception as e:
                logging.warn(
                    f"Unable to add user to the database due to: \n{e}")

    async def get_or_gen_thumb(self: UnzipperBot, uid: int, doc_f: str, isvid: bool = False):
        """
        Get saved thumbnail from the database. If there isn't any thumbnail saved, None will be returned.
        For video files, a thumbnail will be generated using ffmpeg

        Parameters:

            - `uid` - User id
            - `doc_f` - File path
            - `isvid` - Pass True if file is a video
        """
        dbthumb = await get_thumbnail(int(uid), True)
        if dbthumb:
            return dbthumb
        elif isvid:
            thmb_pth = f"Dump/thumbnail_{path.basename(doc_f)}.jpg"
            if path.exists(thmb_pth):
                remove(thmb_pth)
            await run_shell_cmds(f"ffmpeg -ss 00:00:01.00 -i {doc_f} -vf 'scale=320:320:force_original_aspect_ratio=decrease' -vframes 1 {thmb_pth}")
            return thmb_pth
        else:
            return None


class UserIsBanned(Exception):
    def __init__(self) -> None:
        super().__init__("You're banned from using this bot!")


def init_patch():
    """
    Apply custom methods defined in CustomMethods class to pyrogram.Client class
    """
    for ckey, cval in PatchMethods.__dict__.items():
        if ckey[:2] != "__":
            setattr(UnzipperBot, ckey, cval)
