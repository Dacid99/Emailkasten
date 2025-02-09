# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


# The following code is a modified version of code from xme's emlrender project https://github.com/xme/emlrender.
# Original code by Xavier Mertens, licensed under the GNU General Public License version 3 (GPLv3).
# Modifications by David & Philipp Aderbauer, licensed under the GNU Affero General Public License version 3 (AGPLv3).
# This modified code is part of an AGPLv3 project. See the LICENSE file for details.

"""Provides functions to render images from .eml files.
Functions starting with _ are helpers and are used only within the scope of this module.
"""

from __future__ import annotations

import base64
import email
import email.header
import hashlib
import logging
import os
import quopri
from email import policy
from typing import TYPE_CHECKING

import imgkit
from PIL import Image

from Emailkasten.utils import get_config

if TYPE_CHECKING:
    from email.message import EmailMessage

    from PIL import ImageFile


logger = logging.getLogger(__name__)


def _combineImages(imagesList: list[str]) -> Image.Image:
    """Combining multiple images into one with attention to their sizes.

    Args:
        imagesList: The list of images to combine.

    Returns:
        The combined image.
    """
    logger.debug("Combining image parts ...")
    imageFileList = list(map(Image.open, imagesList))

    backgroundColor = get_config("PRERENDER_IMAGE_BACKGROUND_COLOR")
    widths, heights = zip(*(imageFile.size for imageFile in imageFileList))

    newImage = Image.new("RGB", (max(widths), sum(heights)), color=backgroundColor)
    offset = 0
    for imageFile in imageFileList:
        # xCoordinate = int((new_width - im.size[0])/2)
        xCoordinate = 0
        newImage.paste(imageFile, (xCoordinate, offset))
        offset += imageFile.size[1]

    logger.debug("Successfully combined image parts.")
    return newImage


def renderEmailData(emailBytes: bytes) -> Image.Image | None:
    """Creates a prerender image of an email.

    Args:
        emailBytes: The data of the mail to be prerendered.
    """
    logger.debug("Generating prerender image for mail ...")

    dumpDir = get_config("TEMPORARY_STORAGE_DIRECTORY")
    # Create the dump directory if not existing yet
    if not os.path.isdir(dumpDir):
        os.makedirs(dumpDir)
        logger.debug("Created dump directory %s", dumpDir)

    emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)

    dirtyHTMLChars = ["\n", "\\n", "\t", "\\t", "\r", "\\r"]

    imgkitOptions = get_config("PRERENDER_IMGKIT_OPTIONS")

    imagePathList = []
    attachmentsList = []

    for part in emailMessage.walk():
        if not part.get_content_disposition():
            contentType = part.get_content_type()
            charset = part.get_content_charset("utf-8")

            logger.debug("Found MIME part: %s", contentType)
            if contentType.startswith("text/"):
                text = part.get_payload(decode=True).decode(charset, errors="replace")

                if contentType == "text/html":
                    for char in dirtyHTMLChars:
                        text = text.replace(char, "")
                else:
                    text = get_config("HTML_WRAPPER") % text

                imagePath = os.path.join(dumpDir, hash(text) + ".png")
                try:
                    imgkit.from_string(
                        text, os.path.join(dumpDir, imagePath), options=imgkitOptions
                    )
                    imagePathList.append(imagePath)
                except Exception:
                    logger.warning(
                        "Decoding MIME part of type %s returned error!",
                        contentType,
                        exc_info=True,
                    )
            elif contentType.startswith("image/"):
                imageData = part.get_payload(decode=True).decode(
                    charset, errors="replace"
                )
                imageType = contentType.split("/")[1]
                imagePath = os.path.join(dumpDir, hash(imageData) + "." + imageType)
                try:
                    with open(imagePath, "wb") as dumpImageFile:
                        dumpImageFile.write(imageData)
                    logger.debug("Decoded %s", imagePath)
                    imagePathList.append(imagePath)
                except Exception:
                    logger.warning(
                        "Decoding MIME part of type %s returned error!",
                        contentType,
                        exc_info=True,
                    )
            else:
                fileName = part.get_filename() or f"{hash(part)}.attachment"
                attachmentsList.append(f"{fileName} ({contentType})")
                logger.debug(
                    "Added attachment %s of MIME type %s", fileName, contentType
                )
        else:
            fileName = part.get_filename() or f"{hash(part)}.attachment"
            attachmentsList.append(f"{fileName} ({contentType})")
            logger.debug("Added attachment %s of MIME type %s", fileName, contentType)

    if attachmentsList:
        footer = "<p><hr><p><b>Attached Files:</b><p><ul>"
        for attachment in attachmentsList:
            footer = footer + "<li>" + attachment + "</li>"
        footer += "</ul>"
        imagePath = os.path.join(dumpDir, hash(footer) + ".png")
        try:
            imgkit.from_string(footer, imagePath, options=imgkitOptions)
            logger.debug("Created footer %s", imagePath)
            imagePathList.append(imagePath)
        except Exception:
            logger.warning("Creation of footer failed with error!", exc_info=True)
    else:
        logger.debug("No attachments found for rendering.")

    if imagePathList:
        combinedImage = _combineImages(imagePathList)
        return combinedImage
    else:
        logger.debug("No images rendered.")
        return None
