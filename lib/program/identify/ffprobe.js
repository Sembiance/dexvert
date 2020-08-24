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
exports.args = (state, p, inPath=state.input.filePath) => (["-show_streams", "-show_format", inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};
	let seenFormatSection = false;
	((state.run.ffprobe || [])[0] || "").trim().split("\n").forEach(line =>
	{
		if(line.trim()==="format_long_name=Binary text")
			meta.formatLongName = line.trim();

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

	if(Object.keys(meta).length>0)
		state.run.meta.ffprobe = meta;

	setImmediate(cb);
};
