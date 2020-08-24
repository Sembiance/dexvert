"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : ["http://xmp.sourceforge.net/", "http://zakalwe.fi/uade", "https://lib.openmpt.org/libopenmpt/", "https://github.com/Sembiance/mikmodInfo", "http://timidity.sourceforge.net/"],
	gentooPackage  : ["media-sound/xmp", "app-emulation/uade", "media-sound/openmpt123", "media-sound/mikmodInfo", "media-sound/timidity++"],
	gentooUseFlags : "flac sdl sndfile mp3 ogg vorbis zlib alsa X gtk ncurses speex vbr",
	bin            : ["xmp", "uade", "openmpt123", "mikmodInfo", "timidity", "timidity"],
	informational  : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "modInfo");
exports.args = (state, p, inPath=state.input.filePath) => (["--jsonOutput", inPath]);
exports.post = (state, p, cb) =>
{
	let meta = {};
	if(state.run.modInfo && state.run.modInfo.length>0 && state.run.modInfo[0] && state.run.modInfo[0].trim().length>0)
	{
		try
		{
			const musicInfo = JSON.parse(state.run.modInfo[0].trim());
			if(Object.keys(musicInfo.length>0))
				meta = musicInfo;
		}
		catch (err) {}
	}

	if(Object.keys(meta).length>0)
		state.run.meta.modInfo = meta;

	setImmediate(cb);
};
