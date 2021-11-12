/*
import {Program} from "../../Program.js";

export class ffprobe extends Program
{
	website = "https://ffmpeg.org/";
	gentooPackage = "media-video/ffmpeg";
	gentooUseFlags = "X alsa amr bzip2 dav1d encode fontconfig gnutls gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://ffmpeg.org/",
	gentooPackage  : "media-video/ffmpeg",
	gentooUseFlags : "X alsa amr bzip2 dav1d encode fontconfig gnutls gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib",
	informational  : true
};

exports.bin = () => "ffprobe";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-show_streams", "-show_format", inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	let seenFormatSection = false;
	(r.results || "").trim().split("\n").forEach(line =>
	{
		if(line.trim().startsWith("format_long_name="))
			meta.formatLongName = line.trim().substring("format_long_name=".length);

		if(line.trim()==="[FORMAT]")
		{
			seenFormatSection = true;
			return;
		}

		if(!seenFormatSection)
			return;
		
		const tag = (line.trim().match(/^TAG:(?<key>[^=]+)=(?<value>.+)$/) || {groups : {}}).groups;
		if(tag.key && tag.value && tag.key.trim().length>0 && tag.value.trim().length>0)
			meta[tag.key.trim()] = tag.value.trim();
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
