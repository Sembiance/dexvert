"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "STOS Picture Packer",
	website          : "http://fileformats.archiveteam.org/wiki/Picture_Packer",
	ext              : [".pac", ".pp1", ".pp2", ".pp3"],
	mimeType         : "image/x-stos-picturepacker",
	magic            : ["Picture Packer bitmap"],
	unsupported      : true,
	unsupportedNotes : XU.trim`
		abydos is the only one that I could find that is supposed to support these file formats. Yet trying to convert any just yields a core dump in the plugins/atari/stos.c file.
		I located this "st2bmp" wiki page about a tool that can convert them to BMP: http://www.atari-wiki.com/index.php/ST2BMP
		However it links to the Atari Forums which are down and can't find another copy of it anywhere, including github.
		Wayback machine has it: https://web.archive.org/web/20130217085228/http://www.atari-forum.com/viewtopic.php?p=177293
		But because the forums required a login, the actual attached files and SOURCE CODE are not available :(
		Found a post talking about it here: http://eab.abime.net/showthread.php?t=78790
		I registered there and will make a post there asking about the tools/source code.`
};
