/*
import {Program} from "../../Program.js";

export class modInfo extends Program
{
	website = ["http://xmp.sourceforge.net/","http://zakalwe.fi/uade","https://lib.openmpt.org/libopenmpt/","https://github.com/Sembiance/mikmodInfo","http://timidity.sourceforge.net/"];
	gentooPackage = ["media-sound/xmp","app-emulation/uade","media-sound/openmpt123","media-sound/mikmodInfo","media-sound/timidity++"];
	gentooUseFlags = "flac sdl sndfile mp3 ogg vorbis zlib alsa X gtk ncurses speex vbr";
	bin = ["xmp","uade","openmpt123","mikmodInfo","timidity","timidity"];
	informational = true;
}
*/

/*
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
exports.args = (state, p, r, inPath=state.input.filePath) => (["--jsonOutput", inPath]);
exports.post = (state, p, r, cb) =>
{
	let meta = {};
	if((r.results || "").trim().length>0)
	{
		try
		{
			const musicInfo = JSON.parse(r.results.trim());
			if(Object.keys(musicInfo.length>0))
				meta = musicInfo;
		}
		catch (err) {}
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
